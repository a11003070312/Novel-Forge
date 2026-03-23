#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vector-search.py -- 小说语义向量检索命令行入口
"""

from __future__ import annotations

import argparse
import json
import sys

import vector_search_core as core


def main() -> int:
    parser = argparse.ArgumentParser(description="小说语义向量检索")
    parser.add_argument("query", nargs="?", help="语义检索查询文本")
    parser.add_argument("--top", type=int, default=core.TOP_K_DEFAULT, help="返回条数，默认 6")
    parser.add_argument("--rebuild", action="store_true", help="强制重建索引")
    parser.add_argument("--status", action="store_true", help="查看索引状态")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    args = parser.parse_args()

    try:
        root = core.find_project_root()
        db_dir = root / core.DB_DIR_NAME
        db_dir.mkdir(exist_ok=True)

        if args.status:
            if args.json:
                print(json.dumps({"ok": True, "status_text": core.format_status(root, db_dir)}, ensure_ascii=False))
            else:
                print(core.format_status(root, db_dir))
            return 0

        files = core.collect_files(root)

        if args.rebuild:
            core.ensure_dependencies()
            model = core.get_model()
            count = core.build_index(root, db_dir, model, files)
            payload = {"ok": True, "rebuilt": True, "chunk_count": count}
            if args.json:
                print(json.dumps(payload, ensure_ascii=False))
            else:
                print(f"索引重建完成: {count} 个文本块")
            return 0

        if not args.query:
            parser.print_help()
            return 2

        result = core.semantic_search(args.query, args.top, auto_rebuild=True)
        if args.json:
            print(json.dumps({"ok": True, **result}, ensure_ascii=False))
        else:
            # Rebuild info goes to stderr for readability.
            if result.get("rebuilt"):
                print("索引不存在或已过期，已自动重建。", file=sys.stderr)
            raw_for_print = []
            for item in result["results"]:
                raw_for_print.append({"source": item["path"], "text": item["text"], "_distance": 1.0 - item["score"]})
            print(core.format_results(args.query, raw_for_print))
        return 0
    except Exception as exc:
        message = str(exc)
        if args.json:
            print(json.dumps({"ok": False, "error": "VECTOR_ERROR", "message": message}, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
