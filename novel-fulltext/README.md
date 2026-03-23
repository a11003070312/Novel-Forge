# 小说全文目录说明

用于存放可直接阅读的章节正文。

## 建议结构

```
novel-fulltext/
└── 卷一/
    ├── 第001章-章节名.md
    ├── 第002章-章节名.md
    └── ...
```

## 维护要求

新增章节后，必须同步更新 `viewer/content-index.json` 中的 `novelFulltext` 列表，否则前端无法展示新章节目录。
