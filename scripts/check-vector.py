#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-vector.py -- 检测向量检索环境是否就绪

退出码:
  0: 依赖已安装，且索引存在
  1: 依赖已安装，但索引不存在
  2: 缺少依赖
"""

import sys
from pathlib import Path

missing = []

try:
    import lancedb  # noqa: F401
except ImportError:
    missing.append("lancedb")

try:
    import pyarrow  # noqa: F401
except ImportError:
    missing.append("pyarrow")

try:
    from sentence_transformers import SentenceTransformer  # noqa: F401
except ImportError:
    missing.append("sentence-transformers")

if missing:
    print("DEPS_MISSING: " + ", ".join(missing))
    sys.exit(2)


def find_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "viewer" / "index.html").exists():
            return parent
    return here.parent.parent


root = find_root()
index_exists = (root / ".vector-db" / "lance.db").exists()

if index_exists:
    print("VECTOR_OK")
    sys.exit(0)

print("INDEX_MISSING")
sys.exit(1)
