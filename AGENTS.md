# 道痕项目维护规则（Codex）

本文件用于固化“新增章节后必须维护哪些文件”的流程。

## 1. 每次新增章节的强制更新清单

当用户给出新章节正文后，Codex 必须按顺序完成：

1. **保存章节正文**
- 新建文件：`novel-fulltext/卷X/第NNN章-章节名.md`

2. **维护卷章目录**
- 更新：`volumes/vol-XX.md`
- 更新该卷的章节列表、剧情要点、当前进度

3. **维护全文阅读索引**
- 更新：`viewer/content-index.json`
- 在 `novelFulltext` 中追加章节条目（`id/title/path`）
- 在 `searchFiles` 中加入新章节路径（用于全局搜索）

4. **维护伏笔追踪**
- 更新：`clues/foreshadowing.md`
- 标注“新埋/推进/回收”的伏笔条目与章节号

5. **维护时间线**
- 更新：`timeline.md`
- 追加本章关键事件与时间点

6. **维护人物关系与重点人物档案**
- 如关系变化，更新：`characters/relationships.json`
- 如人物状态变化，更新对应：
  - `characters/key-figures/*.md`
  - 必要时同步 `characters/protagonists/*.md` 等基础人物档

7. **重建向量索引**
- 执行：`python scripts/vector-search.py --rebuild`

8. **快速验证检索**
- 执行 1-2 条查询，例如：
  - `python scripts/vector-search.py "第NNN章的核心冲突"`
  - `python scripts/vector-search.py "本章涉及的主要人物关系变化"`

## 2. 必须反馈给用户的结果

每次章节维护后，需要给用户一个“变更摘要”：

- 新增章节文件路径
- 更新了哪些索引/状态文件
- 伏笔新增/推进/回收各多少条
- 时间线新增事件数
- 人物关系是否变化
- 向量索引是否重建成功

## 3. 最小原则

- 不得跳过 `viewer/content-index.json`（否则前端看不到新章节）
- 不得跳过 `clues/foreshadowing.md` 与 `timeline.md`（否则连续性会断）
- 不得只改关系图而不改重点人物档案（人物细节会过期）
