# 小说管理系统设计文档

**日期**: 2026-03-23
**项目**: 道痕小说写作辅助工具

## 概述

构建一个本地 HTML 可视化工具，用于预览和管理小说创作内容。内容以 Markdown 文件存储，由 Claude Code 直接编辑，HTML 页面提供美观的图形化预览界面，激发创作灵感。

## 核心定位

- **内容管理**: Claude Code 编辑 Markdown 文件
- **可视化预览**: HTML 页面渲染展示
- **规模**: 长篇/超长篇小说（5-10+ 卷，百万字级别）
- **功能重点**: 宏观管理（大纲/世界观）+ 细节追踪（伏笔/线索）

## 技术架构

### 技术栈
- **前端**: Vue 3 (CDN) + Marked.js + 原生 CSS
- **数据格式**: Markdown 文件
- **服务器**: Python HTTP Server (`python -m http.server`)
- **样式**: 现代简洁风格（白底深字）

### 启动方式
```bash
cd E:/副业/小说工厂/道痕_doubao
python -m http.server 8080
# 浏览器访问: http://localhost:8080/viewer/
```

## 文件结构

```
道痕_doubao/
├── README.md
├── outline.md                   # 总大纲
├── worldbuilding/
│   ├── world.md                 # 世界观总览
│   ├── combat-system.md         # 战斗体系
│   ├── power-levels.md          # 境界体系
│   └── locations.md             # 地点设定
├── characters/
│   ├── protagonists/            # 主角团
│   ├── antagonists/             # 反派
│   └── supporting/              # 配角
├── volumes/
│   ├── vol-01.md                # 第一卷
│   ├── vol-02.md
│   └── ...
├── clues/
│   ├── foreshadowing.md         # 伏笔追踪
│   ├── plot-threads.md          # 线索追踪
│   └── mysteries.md             # 未解之谜
├── timeline.md                  # 时间线
└── viewer/
    ├── index.html               # 可视化页面
    ├── style.css                # 样式
    └── app.js                   # 逻辑
```

## Markdown 文件格式

### 人物设定示例 (characters/protagonists/主角名.md)
```markdown
---
name: 张三
age: 25
realm: 筑基期
status: alive
tags: [主角, 剑修, 天才]
---

# 张三

## 基本信息
- 年龄：25
- 境界：筑基期
- 身份：某某宗弟子

## 性格特点
...

## 重要经历
- 第1卷：...
- 第3卷：...

## 关系网络
- 师父：李四
- 仇人：王五
```

## 功能模块

### 1. 仪表盘 (Dashboard)
- 小说基本信息（标题、当前进度、总字数）
- 快速入口：最近编辑的文件、待完善的伏笔
- 统计数据：卷数、人物数、伏笔数

### 2. 大纲视图 (Outline)
- 树状结构展示总大纲
- 点击卷标题跳转到对应卷详情
- 支持折叠/展开

### 3. 世界观浏览 (Worldbuilding)
- 标签页切换：世界观总览 / 战斗体系 / 境界体系 / 地点
- Markdown 渲染，支持表格、列表
- 侧边栏快速导航（锚点跳转）

### 4. 人物图谱 (Characters)
- 卡片式布局，显示姓名、境界、标签
- 点击卡片查看详细设定
- 按分类筛选：主角团 / 反派 / 配角
- 关系网络可视化（可选）

### 5. 伏笔追踪 (Clues)
- 列表展示所有伏笔，标注状态（已埋 / 已回收 / 待回收）
- 点击查看详情和相关章节
- 按状态筛选

### 6. 时间线 (Timeline)
- 横向时间轴，展示关键事件
- 点击事件查看详情

### 7. 全局搜索
- 顶部搜索框，实时搜索所有 Markdown 文件
- 搜索范围：文件名 + 文件内容
- 结果展示：文件路径 + 匹配内容片段 + 关键词高亮
- 高级筛选：按模块筛选（人物/伏笔/世界观等）
- 快速跳转：点击结果自动跳转到对应位置

### 8. 导出功能
- 每个内容区右上角显示"复制"和"下载"按钮
- 复制：将 Markdown 原文复制到剪贴板
- 下载：下载 Markdown 格式文件

## 界面布局

```
┌─────────────────────────────────────────────┐
│  道痕 | 小说管理系统          [搜索框]      │
├──────┬──────────────────────────────────────┤
│ 导航 │                                      │
│ 栏   │        主内容区                       │
│      │                                      │
│ 仪表盘│                                      │
│ 大纲 │                                      │
│ 世界观│                                      │
│ 人物 │                                      │
│ 伏笔 │                                      │
│ 时间线│                                      │
└──────┴──────────────────────────────────────┘
```

## 样式设计（现代简洁风）

- **主色调**: `#1a1a1a`（深灰文字）+ `#ffffff`（白底）
- **强调色**: `#0066cc`（蓝色链接/按钮）
- **字体**: 系统默认 sans-serif
- **间距**: 8px 基准网格
- **圆角**: 4px
- **阴影**: 轻微 box-shadow

## 核心技术实现

### 1. 文件读取
```javascript
async function loadMarkdown(path) {
  const response = await fetch(`../${path}`)
  const text = await response.text()
  return marked.parse(text)
}
```

### 2. 复制到剪贴板
```javascript
async function copyToClipboard(markdownText) {
  await navigator.clipboard.writeText(markdownText)
  // 显示提示：已复制
}
```

### 3. 下载 Markdown 文件
```javascript
function downloadMarkdown(filename, content) {
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}
```

### 4. 全局搜索实现
```javascript
// 启动时加载所有 Markdown 文件到内存
const allFiles = [
  { path: 'characters/主角名.md', content: '...' },
  { path: 'volumes/vol-01.md', content: '...' },
]

// 搜索函数
function search(keyword) {
  return allFiles
    .map(file => {
      const matches = findMatches(file.content, keyword)
      return { file, matches }
    })
    .filter(result => result.matches.length > 0)
}

// 高亮显示
function highlightKeyword(text, keyword) {
  return text.replace(
    new RegExp(keyword, 'gi'),
    match => `<mark>${match}</mark>`
  )
}
```

### 5. 搜索结果展示格式
```
搜索："筑基期" (找到 15 处)

📄 characters/主角名.md
  ...境界：筑基期...
  [查看详情] [复制] [下载]

📄 volumes/vol-03.md
  ...突破到筑基期后...
  [查看详情] [复制] [下载]
```

### 6. 性能优化
- 首次加载时缓存所有文件内容
- 搜索时使用防抖（debounce），避免频繁搜索
- 结果分页显示（每页 20 条）
- 快速跳转：点击结果 → 切换模块 → 滚动到位置 → 高亮显示

## 实现文件结构

```
viewer/
├── index.html       # 主页面（约 300 行）
├── style.css        # 样式（约 200 行）
└── app.js           # 逻辑（约 400 行）
```

## 下一步

1. 创建基础文件结构和示例 Markdown 文件
2. 实现 HTML viewer 的核心功能
3. 测试和优化用户体验
