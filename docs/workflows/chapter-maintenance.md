# 新增章节维护流程（标准版）

## 适用场景

用户提供“新写好的章节”，需要把项目状态同步到可检索、可阅读、可追踪。

## 输入信息

至少需要：

- 所属卷（如：第一卷）
- 章节号与章节名（如：第004章：宗门试炼）
- 章节正文

建议补充：

- 本章新增/推进/回收的伏笔
- 本章人物关系变化
- 本章时间推进点

## 执行步骤

1. 新建章节文件到 `novel-fulltext/卷X/`
2. 更新 `viewer/content-index.json`（`novelFulltext` + `searchFiles`）
3. 更新 `volumes/vol-XX.md` 的章节列表与进度
4. 更新 `clues/foreshadowing.md`
5. 更新 `timeline.md`
6. 更新 `characters/relationships.json`（如有）
7. 更新 `characters/key-figures/*.md`（重点人物状态）
8. 运行 `python scripts/vector-search.py --rebuild`
9. 用 1-2 条查询验证检索命中

## 验收标准

- Viewer “小说全文”能看到新章节并可点开阅读
- Viewer 全局搜索能搜到新章节关键词
- 伏笔、时间线、人物状态与正文一致
- 向量检索命中新章节相关内容

## 输出模板（给用户）

```
已完成第NNN章维护。

新增:
- novel-fulltext/卷X/第NNN章-章节名.md

更新:
- viewer/content-index.json
- volumes/vol-XX.md
- clues/foreshadowing.md
- timeline.md
- characters/relationships.json（如有）
- characters/key-figures/XXX.md（如有）

检索:
- 向量索引重建: 成功/失败
- 验证查询: 命中X条
```
