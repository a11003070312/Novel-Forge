#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vector-search.py -- 小说工程语义向量检索工具

功能:
1) 对小说工程中的 Markdown/YAML 文本分块并建立向量索引
2) 执行语义检索，返回最相关文本片段
3) 支持索引状态查看与重建

用法:
  python scripts/vector-search.py "林轩和苏婉儿的关系变化"
  python scripts/vector-search.py "传承线索" --top 8
  python scripts/vector-search.py --status
  python scripts/vector-search.py --rebuild
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

if not os.environ.get("HF_ENDPOINT"):
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

MISSING_DEPS: List[str] = []

try:
    import yaml
except ImportError:
    MISSING_DEPS.append("pyyaml")

try:
    import lancedb
except ImportError:
    MISSING_DEPS.append("lancedb")

try:
    import pyarrow  # noqa: F401
except ImportError:
    MISSING_DEPS.append("pyarrow")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    MISSING_DEPS.append("sentence-transformers")

if MISSING_DEPS:
    print(
        "[错误] 缺少依赖: " + ", ".join(MISSING_DEPS) + "\n"
        "请执行: pip install " + " ".join(MISSING_DEPS),
        file=sys.stderr,
    )
    sys.exit(2)

MODEL_NAME = "BAAI/bge-base-zh-v1.5"
DB_DIR_NAME = ".vector-db"
TABLE_NAME = "novel_chunks"
CHUNK_SIZE = 320
CHUNK_OVERLAP = 50
TOP_K_DEFAULT = 6

INDEX_RULES = [
    "outline.md",
    "timeline.md",
    "volumes/**/*.md",
    "novel-fulltext/**/*.md",
    "characters/**/*.md",
    "clues/**/*.md",
    "worldbuilding/**/*.md",
]

SEPARATOR = "=" * 68
SUB_SEPARATOR = "-" * 68


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "viewer" / "index.html").exists() and (current / "README.md").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    print("[错误] 无法定位项目根目录。", file=sys.stderr)
    sys.exit(2)


def collect_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for rule in INDEX_RULES:
        if "*" in rule:
            for fp in sorted(root.glob(rule)):
                if fp.is_file() and not fp.name.startswith("_"):
                    files.append(fp)
        else:
            fp = root / rule
            if fp.is_file() and not fp.name.startswith("_"):
                files.append(fp)
    deduped = sorted(set(files))
    return deduped


def read_text(filepath: Path) -> str:
    try:
        return filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def strip_frontmatter(md_text: str) -> str:
    if not md_text.startswith("---"):
        return md_text
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", md_text, re.DOTALL)
    if match:
        return md_text[match.end():]
    return md_text


def flatten_yaml(obj: object, depth: int = 0) -> str:
    if depth > 12:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        parts: List[str] = []
        for key, value in obj.items():
            if isinstance(key, str):
                parts.append(key)
            parts.append(flatten_yaml(value, depth + 1))
        return " ".join(p for p in parts if p)
    if isinstance(obj, list):
        return " ".join(flatten_yaml(item, depth + 1) for item in obj)
    return ""


def normalize_text(filepath: Path, raw_text: str) -> str:
    suffix = filepath.suffix.lower()
    if suffix == ".md":
        text = strip_frontmatter(raw_text)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        return text
    if suffix in {".yaml", ".yml"}:
        try:
            parsed = yaml.safe_load(raw_text)
        except yaml.YAMLError:
            return raw_text
        return flatten_yaml(parsed)
    return raw_text


def chunk_text(text: str, source: str) -> List[Dict[str, str]]:
    if not text.strip():
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        return []

    chunks: List[Dict[str, str]] = []
    current: List[str] = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para)
        if current and current_len + para_len > CHUNK_SIZE:
            chunk_value = "\n\n".join(current)
            chunks.append({"text": chunk_value, "source": source})

            if CHUNK_OVERLAP > 0:
                tail = current[-1]
                current = [tail]
                current_len = len(tail)
            else:
                current = []
                current_len = 0

        current.append(para)
        current_len += para_len

    if current:
        chunk_value = "\n\n".join(current)
        chunks.append({"text": chunk_value, "source": source})

    return chunks


def build_chunks(root: Path, files: List[Path]) -> List[Dict[str, str]]:
    chunks: List[Dict[str, str]] = []
    for fp in files:
        raw = read_text(fp)
        if not raw:
            continue
        content = normalize_text(fp, raw)
        source = str(fp.relative_to(root)).replace("\\", "/")
        chunks.extend(chunk_text(content, source))
    return chunks


def compute_fingerprint(files: List[Path]) -> str:
    hasher = hashlib.sha256()
    for fp in sorted(files):
        try:
            stat = fp.stat()
            hasher.update(f"{fp}:{stat.st_size}:{stat.st_mtime}".encode("utf-8"))
        except OSError:
            continue
    return hasher.hexdigest()[:16]


def read_saved_fingerprint(db_dir: Path) -> str:
    fp = db_dir / "fingerprint.txt"
    if fp.exists():
        return fp.read_text(encoding="utf-8").strip()
    return ""


def save_fingerprint(db_dir: Path, fingerprint: str) -> None:
    (db_dir / "fingerprint.txt").write_text(fingerprint, encoding="utf-8")


def get_model() -> SentenceTransformer:
    print(f"加载模型: {MODEL_NAME}", file=sys.stderr)
    return SentenceTransformer(MODEL_NAME)


def build_index(root: Path, db_dir: Path, model: SentenceTransformer, files: List[Path]) -> int:
    chunks = build_chunks(root, files)
    if not chunks:
        print("[警告] 没有可索引文本。", file=sys.stderr)
        return 0

    print(f"生成向量中: {len(chunks)} 个文本块", file=sys.stderr)
    vectors = model.encode(
        [chunk["text"] for chunk in chunks],
        show_progress_bar=False,
        normalize_embeddings=True,
    )

    rows = []
    for idx, chunk in enumerate(chunks):
        rows.append(
            {
                "id": idx,
                "text": chunk["text"],
                "source": chunk["source"],
                "vector": vectors[idx].tolist(),
            }
        )

    db = lancedb.connect(str(db_dir / "lance.db"))
    try:
        db.drop_table(TABLE_NAME)
    except Exception:
        pass

    db.create_table(TABLE_NAME, rows)
    save_fingerprint(db_dir, compute_fingerprint(files))
    return len(chunks)


def search_index(db_dir: Path, model: SentenceTransformer, query: str, top_k: int) -> List[Dict]:
    db = lancedb.connect(str(db_dir / "lance.db"))
    try:
        table = db.open_table(TABLE_NAME)
    except Exception:
        print("[错误] 向量表不存在，请先 --rebuild。", file=sys.stderr)
        sys.exit(2)

    query_text = f"为这个句子生成表示以用于检索相关段落：{query}"
    query_vec = model.encode([query_text], normalize_embeddings=True)[0]
    results = (
        table.search(query_vec.tolist())
        .metric("cosine")
        .limit(top_k)
        .to_list()
    )
    return results


def format_results(query: str, results: List[Dict]) -> str:
    lines = [SEPARATOR, f'语义检索: "{query}"', SEPARATOR]
    if not results:
        lines.extend(["无匹配结果", SEPARATOR])
        return "\n".join(lines)

    for i, item in enumerate(results, 1):
        score = 1.0 - item.get("_distance", 0.0)
        source = item.get("source", "unknown")
        text = item.get("text", "").replace("\n", " ").strip()
        if len(text) > 180:
            text = text[:180] + "..."
        lines.append(f"[{i}] 相关度: {score:.3f} | 来源: {source}")
        lines.append(f"    {text}")
        lines.append("")

    lines.extend([SUB_SEPARATOR, f"共 {len(results)} 条结果", SEPARATOR])
    return "\n".join(lines)


def format_status(root: Path, db_dir: Path) -> str:
    files = collect_files(root)
    db_path = db_dir / "lance.db"
    current_fp = compute_fingerprint(files)
    saved_fp = read_saved_fingerprint(db_dir)

    lines = [SEPARATOR, "向量索引状态", SEPARATOR]
    lines.append(f"索引目录: {db_dir}")
    lines.append(f"纳入索引文件: {len(files)}")

    if not db_path.exists():
        lines.append("状态: 未构建")
        lines.extend([SEPARATOR])
        return "\n".join(lines)

    if current_fp == saved_fp and saved_fp:
        lines.append("状态: 最新")
    else:
        lines.append("状态: 过期（文件变化，建议重建）")

    try:
        db = lancedb.connect(str(db_path))
        table = db.open_table(TABLE_NAME)
        lines.append(f"索引块数: {table.count_rows()}")
    except Exception:
        lines.append("索引块数: 无法读取")

    lines.extend([SEPARATOR])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="小说语义向量检索")
    parser.add_argument("query", nargs="?", help="语义检索查询文本")
    parser.add_argument("--top", type=int, default=TOP_K_DEFAULT, help="返回条数，默认 6")
    parser.add_argument("--rebuild", action="store_true", help="强制重建索引")
    parser.add_argument("--status", action="store_true", help="查看索引状态")
    args = parser.parse_args()

    root = find_project_root()
    db_dir = root / DB_DIR_NAME
    db_dir.mkdir(exist_ok=True)
    files = collect_files(root)

    if args.status:
        print(format_status(root, db_dir))
        return 0

    if args.rebuild:
        if not files:
            print("[错误] 没有可索引文件。", file=sys.stderr)
            return 2
        model = get_model()
        count = build_index(root, db_dir, model, files)
        print(f"索引重建完成: {count} 个文本块")
        return 0

    if not args.query:
        parser.print_help()
        return 2

    current_fp = compute_fingerprint(files)
    saved_fp = read_saved_fingerprint(db_dir)
    db_exists = (db_dir / "lance.db").exists()

    model = get_model()
    if not db_exists or current_fp != saved_fp:
        print("索引不存在或已过期，自动重建中...", file=sys.stderr)
        build_index(root, db_dir, model, files)

    results = search_index(db_dir, model, args.query, args.top)
    print(format_results(args.query, results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
