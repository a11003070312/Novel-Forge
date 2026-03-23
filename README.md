# 墨痕工坊 (Novel Forge)

> 专为长篇小说创作打造的可视化管理工具

一个优雅的本地小说创作辅助系统，帮助作者管理复杂的长篇小说内容。通过 Markdown 文件存储内容，配合精美的可视化界面，让创作灵感自由流动。

![深色主题](https://img.shields.io/badge/theme-dark-0f172a)
![Vue 3](https://img.shields.io/badge/vue-3.4-42b883)
![无需构建](https://img.shields.io/badge/build-none-green)

## ✨ 核心特性

### 📊 可视化管理
- **仪表盘**：一目了然的创作统计（卷数、人物、伏笔）
- **人物关系图谱**：SVG 绘制的节点连线，直观展示人物关系网络
- **可拖动时间线**：横向滚动查看故事事件，支持鼠标拖拽
- **伏笔追踪看板**：卡片化展示，状态标签清晰标注（待回收/已回收）

### 📝 内容管理
- **总大纲**：管理整体故事结构
- **世界观设定**：世界规则、战斗体系、境界划分
- **人物档案**：详细的角色设定和关系网络
- **卷章管理**：各卷内容、章节列表
- **线索追踪**：伏笔埋设与回收管理

### 🎨 设计亮点
- **深色主题**：营造专注创作的氛围（#0f172a 背景）
- **衬线字体**：Noto Serif SC、Crimson Pro 增加文学气息
- **流畅动画**：悬停效果和过渡动画
- **卡片化设计**：减少文字密度，增加视觉层次

### 🔍 强大搜索
- 全局实时搜索所有 Markdown 文件
- 关键词高亮显示
- 快速定位内容

### 📤 便捷导出
- 一键复制 Markdown 原文到剪贴板
- 下载 Markdown 文件

## 🚀 快速开始

### 前置要求
- Python 3.x（用于启动本地服务器）
- 现代浏览器（Chrome、Edge、Firefox）

### 启动步骤

1. **克隆或下载项目**
```bash
cd 道痕_doubao
```

2. **启动本地服务器**
```bash
python -m http.server 8080
```

3. **打开浏览器**
```
http://localhost:8080/viewer/
```

就这么简单！无需安装依赖，无需构建步骤。

## 📁 文件结构

```
道痕_doubao/
├── README.md                    # 项目说明
├── outline.md                   # 总大纲
├── timeline.md                  # 时间线
├── worldbuilding/               # 世界观设定
│   ├── world.md                 # 世界观总览
│   ├── combat-system.md         # 战斗体系
│   └── power-levels.md          # 境界体系
├── characters/                  # 人物设定
│   ├── protagonists/            # 主角团
│   ├── antagonists/             # 反派
│   └── supporting/              # 配角
├── volumes/                     # 各卷内容
│   ├── vol-01.md
│   ├── vol-02.md
│   └── ...
├── clues/                       # 伏笔和线索
│   ├── foreshadowing.md         # 伏笔追踪
│   ├── plot-threads.md          # 线索追踪
│   └── mysteries.md             # 未解之谜
├── docs/                        # 文档
│   └── plans/                   # 设计文档
└── viewer/                      # 可视化界面
    ├── index.html               # 主页面
    ├── style.css                # 样式
    └── app.js                   # 逻辑
```

## 🎯 使用场景

### 场景 1：规划新卷内容
1. 打开"总大纲"查看整体结构
2. 切换到"人物关系"查看角色网络
3. 检查"伏笔追踪"确认待回收的线索
4. 用 Claude Code 编辑 `volumes/vol-XX.md` 添加新卷

### 场景 2：管理人物关系
1. 打开"人物关系"模块
2. 查看 SVG 关系图谱
3. 点击节点查看详细设定
4. 用 Claude Code 编辑 `characters/` 下的文件

### 场景 3：追踪伏笔
1. 打开"伏笔追踪"看板
2. 查看"待回收"栏的伏笔
3. 规划在哪一卷回收
4. 回收后移动到"已回收"栏

### 场景 4：查看时间线
1. 打开"时间线"模块
2. 横向拖动查看事件
3. 确认故事时间逻辑
4. 用 Claude Code 编辑 `timeline.md`

## 💡 工作流程

**推荐的创作流程**：

1. **用 Claude Code 编辑内容**
   - 直接编辑 Markdown 文件
   - 利用 AI 辅助创作
   - 版本控制（Git）

2. **用可视化界面预览**
   - 刷新浏览器查看更新
   - 图形化查看关系和结构
   - 激发创作灵感

3. **导出和备份**
   - 一键复制 Markdown 内容
   - 下载文件到本地
   - Git 版本管理

## 🛠️ 技术栈

- **前端框架**：Vue 3 (CDN)
- **Markdown 渲染**：Marked.js
- **字体**：Noto Serif SC、Crimson Pro、Inter
- **图形绘制**：SVG
- **服务器**：Python HTTP Server
- **数据存储**：Markdown 文件

**无需构建工具**，开箱即用！

## 🎨 界面预览

### 深色主题
- 背景色：`#0f172a`（深蓝灰）
- 主色调：`#3b82f6`（蓝色）
- 强调色：`#8b5cf6`（紫色）

### 核心模块
- **仪表盘**：统计卡片 + 快速入口
- **人物关系**：SVG 节点图 + 连线标注
- **时间线**：横向可拖动时间轴
- **伏笔追踪**：看板式卡片布局

## 📝 Markdown 文件格式

### 人物设定示例
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

## 关系网络
- 师父：李四
- 仇人：王五
```

### 伏笔追踪示例
```markdown
# 伏笔追踪

## 未回收伏笔

### 神秘传承的来历
- **埋下位置**: 第1卷第3章
- **计划回收**: 第5卷
- **状态**: 🔴 待回收
```

## 🔧 自定义配置

### 修改主题颜色
编辑 `viewer/style.css`，修改 CSS 变量：
```css
:root {
  --bg-primary: #0f172a;
  --text-primary: #f1f5f9;
  --accent: #3b82f6;
}
```

### 添加新模块
1. 在根目录创建新的 Markdown 文件
2. 在 `viewer/app.js` 的 `allFiles` 数组中添加路径
3. 在 `viewer/index.html` 导航栏添加入口

## 🤝 贡献

这是一个个人创作工具，欢迎根据自己的需求进行定制。

## 📄 许可证

MIT License - 自由使用和修改

## 🙏 致谢

- **Vue.js** - 响应式框架
- **Marked.js** - Markdown 渲染
- **Google Fonts** - 优雅字体
- **Claude Code** - AI 辅助创作

---

**墨痕工坊** - 让创作灵感自由流动 ✨
