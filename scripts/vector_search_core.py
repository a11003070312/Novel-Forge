#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vector_search_core.py -- 向量检索核心库
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
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
if importlib.util.find_spec("yaml") is None:
    MISSING_DEPS.append("pyyaml")
if importlib.util.find_spec("lancedb") is None:
    MISSING_DEPS.append("lancedb")
if importlib.util.find_spec("pyarrow") is None:
    MISSING_DEPS.append("pyarrow")
if importlib.util.find_spec("sentence_transformers") is None:
    MISSING_DEPS.append("sentence-transformers")

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

_MODEL_CACHE = None


def _import_yaml():
    return importlib.import_module("yaml")


def _import_lancedb():
    return importlib.import_module("lancedb")


def ensure_dependencies() -> None:
    if MISSING_DEPS:
        raise RuntimeError(
            "[错误] 缺少依赖: " + ", ".join(MISSING_DEPS) + "\n"
            "请执行: pip install " + " ".join(MISSING_DEPS)
        )


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "viewer" / "index.html").exists() and (current / "README.md").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    raise RuntimeError("[错误] 无法定位项目根目录。")


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
    return sorted(set(files))


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
            yaml_mod = _import_yaml()
            parsed = yaml_mod.safe_load(raw_text)
        except Exception:
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
        chunks.append({"text": "\n\n".join(current), "source": source})
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


def get_model():
    ensure_dependencies()
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        try:
            sentence_transformers = importlib.import_module("sentence_transformers")
            print(f"加载模型: {MODEL_NAME}", file=sys.stderr)
            _MODEL_CACHE = sentence_transformers.SentenceTransformer(MODEL_NAME)
        except Exception as exc:
            raise RuntimeError(
                "向量模型加载失败。请先确认可访问模型源，并执行 "
                "`python scripts/vector-search.py --rebuild` 预构建索引。"
                f" 原因: {exc}"
            ) from exc
    return _MODEL_CACHE


def build_index(root: Path, db_dir: Path, model, files: List[Path]) -> int:
    ensure_dependencies()
    chunks = build_chunks(root, files)
    if not chunks:
        return 0

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

    lancedb_mod = _import_lancedb()
    db = lancedb_mod.connect(str(db_dir / "lance.db"))
    try:
        db.drop_table(TABLE_NAME)
    except Exception:
        pass
    db.create_table(TABLE_NAME, rows)
    save_fingerprint(db_dir, compute_fingerprint(files))
    return len(chunks)


def search_index(db_dir: Path, model, query: str, top_k: int) -> List[Dict]:
    ensure_dependencies()
    lancedb_mod = _import_lancedb()
    db = lancedb_mod.connect(str(db_dir / "lance.db"))
    table = db.open_table(TABLE_NAME)
    query_text = f"为这个句子生成表示以用于检索相关段落：{query}"
    query_vec = model.encode([query_text], normalize_embeddings=True)[0]
    return (
        table.search(query_vec.tolist())
        .metric("cosine")
        .limit(top_k)
        .to_list()
    )


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
        lancedb_mod = _import_lancedb()
        db = lancedb_mod.connect(str(db_path))
        table = db.open_table(TABLE_NAME)
        lines.append(f"索引块数: {table.count_rows()}")
    except Exception:
        lines.append("索引块数: 无法读取")
    lines.extend([SEPARATOR])
    return "\n".join(lines)


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


def to_result_items(results: List[Dict]) -> List[Dict]:
    items: List[Dict] = []
    for item in results:
        source = item.get("source", "unknown")
        text = item.get("text", "").strip()
        score = 1.0 - item.get("_distance", 0.0)
        snippet = text[:240] + ("..." if len(text) > 240 else "")
        items.append(
            {
                "path": source,
                "score": round(score, 4),
                "snippet": snippet,
                "text": text,
            }
        )
    return items


def semantic_search(query: str, top_k: int = TOP_K_DEFAULT, auto_rebuild: bool = True) -> Dict:
    ensure_dependencies()
    root = find_project_root()
    db_dir = root / DB_DIR_NAME
    db_dir.mkdir(exist_ok=True)
    files = collect_files(root)
    current_fp = compute_fingerprint(files)
    saved_fp = read_saved_fingerprint(db_dir)
    db_exists = (db_dir / "lance.db").exists()

    model = get_model()
    rebuilt = False
    if auto_rebuild and (not db_exists or current_fp != saved_fp):
        build_index(root, db_dir, model, files)
        rebuilt = True

    raw = search_index(db_dir, model, query, top_k)
    return {
        "query": query,
        "rebuilt": rebuilt,
        "results": to_result_items(raw),
    }
