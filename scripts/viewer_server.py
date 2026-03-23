#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
viewer_server.py -- Viewer 本地服务（静态文件 + 向量搜索 API）
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import vector_search_core as core

ROOT = Path(__file__).resolve().parent.parent


class ViewerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/vector-search":
            self.handle_vector_search(parsed.query)
            return
        if parsed.path == "/api/vector-status":
            self.handle_vector_status()
            return
        super().do_GET()

    def handle_vector_status(self):
        try:
            root = core.find_project_root()
            db_dir = root / core.DB_DIR_NAME
            db_exists = (db_dir / "lance.db").exists()
            payload = {
                "ok": True,
                "deps_missing": core.MISSING_DEPS,
                "index_exists": db_exists,
                "status": "ready" if db_exists and not core.MISSING_DEPS else "degraded",
            }
            self.write_json(200, payload)
        except Exception as exc:
            self.write_json(500, {"ok": False, "error": "STATUS_ERROR", "message": str(exc)})

    def handle_vector_search(self, query_string: str):
        params = parse_qs(query_string)
        q = (params.get("q", [""])[0] or "").strip()
        top = params.get("top", ["6"])[0]

        if not q:
            self.write_json(400, {"ok": False, "error": "EMPTY_QUERY", "message": "缺少查询参数 q"})
            return

        try:
            top_k = max(1, min(20, int(top)))
        except ValueError:
            top_k = 6

        try:
            result = core.semantic_search(q, top_k=top_k, auto_rebuild=True)
            self.write_json(
                200,
                {
                    "ok": True,
                    "query": q,
                    "rebuilt": result.get("rebuilt", False),
                    "results": result.get("results", []),
                    "deps_missing": core.MISSING_DEPS,
                },
            )
        except Exception as exc:
            message = str(exc)
            status_code = 503 if "缺少依赖" in message else 500
            self.write_json(
                status_code,
                {
                    "ok": False,
                    "error": "VECTOR_SEARCH_FAILED",
                    "message": message,
                    "deps_missing": core.MISSING_DEPS,
                },
            )

    def write_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args):
        sys.stdout.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))


def main():
    parser = argparse.ArgumentParser(description="Novel Forge viewer server")
    parser.add_argument("--port", type=int, default=8080, help="HTTP 端口，默认 8080")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), ViewerHandler)
    print("========================================")
    print("  墨痕工坊 - Viewer 服务已启动")
    print(f"  访问地址: http://localhost:{args.port}/viewer/")
    print(f"  API: http://localhost:{args.port}/api/vector-search?q=关键词")
    if core.MISSING_DEPS:
        print("  [提示] 向量依赖未安装，语义搜索将不可用。")
        print("  安装命令: pip install -r scripts/requirements-vector.txt")
    print("========================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
