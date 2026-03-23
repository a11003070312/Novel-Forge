const { createApp } = Vue;

const DEFAULT_CONTENT_INDEX = {
  modules: {
    outline: "outline.md",
    worldbuilding: "worldbuilding/world.md",
    volumes: "volumes/vol-01.md"
  },
  searchFiles: [
    "outline.md",
    "timeline.md",
    "worldbuilding/world.md",
    "worldbuilding/combat-system.md",
    "volumes/vol-01.md",
    "clues/foreshadowing.md",
    "characters/protagonists/主角.md"
  ],
  novelFulltext: [],
  keyCharacters: []
};

const DEFAULT_RELATIONSHIP_GRAPH = {
  nodes: [
    { id: "lin-xuan", name: "林轩", x: 400, y: 220, radius: 50, type: "main" },
    { id: "jian-chen", name: "剑尘真人", x: 240, y: 110, radius: 40, type: "ally" },
    { id: "su-waner", name: "苏婉儿", x: 570, y: 130, radius: 40, type: "ally" },
    { id: "zhao-wuji", name: "赵无极", x: 410, y: 360, radius: 45, type: "enemy" }
  ],
  edges: [
    { id: "e-1", x1: 240, y1: 110, x2: 400, y2: 220, label: "师徒" },
    { id: "e-2", x1: 570, y1: 130, x2: 400, y2: 220, label: "盟友" },
    { id: "e-3", x1: 400, y1: 220, x2: 410, y2: 360, label: "宿敌" }
  ]
};

createApp({
  data() {
    return {
      currentModule: "dashboard",
      currentTitle: "",
      currentContent: "",
      currentFile: "",
      renderedContent: "",
      searchQuery: "",
      searchResults: [],
      showSearch: false,
      allFiles: [],
      contentIndex: DEFAULT_CONTENT_INDEX,
      stats: { volumes: 0, characters: 0, keyCharacters: 0, chapters: 0, clues: 0 },
      relationshipNodes: [],
      relationshipEdges: [],
      timelineEvents: [],
      timelineOffset: 0,
      timelineDragging: false,
      timelineDragStart: 0,
      cluesList: [],
      novelTree: [],
      selectedNovelChapter: null,
      novelCurrentTitle: "",
      novelCurrentContent: "",
      novelCurrentFilename: "",
      novelRenderedContent: "",
      keyCharacters: [],
      selectedKeyCharacter: null,
      keyCharacterContent: "",
      keyCharacterFilename: "",
      keyCharacterRenderedContent: ""
    };
  },
  async mounted() {
    await this.loadContentIndex();

    await Promise.all([
      this.loadAllFiles(),
      this.initializeRelationshipGraph(),
      this.initializeTimeline(),
      this.initializeClues()
    ]);

    this.initializeNovelReader();
    this.initializeKeyCharacterPanel();
    this.calculateStats();
  },
  methods: {
    async loadContentIndex() {
      try {
        const response = await fetch("./content-index.json");
        if (!response.ok) {
          throw new Error("index file missing");
        }
        const loadedIndex = await response.json();
        this.contentIndex = {
          ...DEFAULT_CONTENT_INDEX,
          ...loadedIndex,
          modules: {
            ...DEFAULT_CONTENT_INDEX.modules,
            ...(loadedIndex.modules || {})
          }
        };
      } catch (e) {
        console.log("使用默认内容索引", e);
        this.contentIndex = { ...DEFAULT_CONTENT_INDEX };
      }
    },

    getAllIndexedFiles() {
      const files = [];
      const modules = this.contentIndex.modules || {};
      const searchFiles = this.contentIndex.searchFiles || [];
      const novelVolumes = this.contentIndex.novelFulltext || [];
      const keyCharacters = this.contentIndex.keyCharacters || [];

      Object.values(modules).forEach(path => files.push(path));
      searchFiles.forEach(path => files.push(path));

      novelVolumes.forEach(volume => {
        (volume.chapters || []).forEach(chapter => {
          files.push(chapter.path);
        });
      });

      keyCharacters.forEach(character => {
        files.push(character.path);
      });

      return [...new Set(files.filter(Boolean))];
    },

    async fetchText(path) {
      const response = await fetch(`../${path}`);
      if (!response.ok) {
        throw new Error(`文件加载失败: ${path}`);
      }
      return response.text();
    },

    async loadAllFiles() {
      this.allFiles = [];
      const filePaths = this.getAllIndexedFiles();

      for (const path of filePaths) {
        try {
          const content = await this.fetchText(path);
          this.allFiles.push({ path, content });
        } catch (e) {
          console.log("文件加载失败:", path);
        }
      }
    },

    calculateStats() {
      this.stats.volumes = this.novelTree.length || this.allFiles.filter(f => f.path.startsWith("volumes/")).length;
      this.stats.characters = this.allFiles.filter(f => f.path.startsWith("characters/") && f.path.endsWith(".md")).length;
      this.stats.keyCharacters = this.keyCharacters.length;
      this.stats.chapters = this.novelTree.reduce((sum, volume) => sum + (volume.chapters || []).length, 0);
      this.stats.clues = this.allFiles.filter(f => f.path.startsWith("clues/")).length;
    },

    async initializeRelationshipGraph() {
      try {
        const response = await fetch("../characters/relationships.json");
        if (!response.ok) {
          throw new Error("relationship data missing");
        }
        const graph = await response.json();
        this.relationshipNodes = graph.nodes || [];
        this.relationshipEdges = graph.edges || [];
      } catch (e) {
        this.relationshipNodes = DEFAULT_RELATIONSHIP_GRAPH.nodes;
        this.relationshipEdges = DEFAULT_RELATIONSHIP_GRAPH.edges;
      }
    },

    initializeTimeline() {
      this.timelineEvents = [
        { id: 1, time: "第0年·春", title: "获得传承", description: "林轩在秘境中触发上古道痕传承。", position: 0 },
        { id: 2, time: "第0年·夏", title: "进入天剑宗", description: "通过灵根测试，成为外门弟子。", position: 320 },
        { id: 3, time: "第0年·秋", title: "外门试炼", description: "首次实战并取得青锋剑。", position: 640 },
        { id: 4, time: "第0年·冬", title: "练气九层", description: "完成卷一阶段性突破。", position: 960 }
      ];
    },

    initializeClues() {
      this.cluesList = [
        { id: 1, title: "神秘传承的来历", content: "传承疑似来自上古大能，真实身份未知。", chapter: "第1卷第3章", status: "pending" },
        { id: 2, title: "苏婉儿真实身份", content: "苏婉儿在宗门之外另有势力背景。", chapter: "第2卷第10章", status: "pending" },
        { id: 3, title: "青锋剑的秘密", content: "青锋剑具备成长属性，已在第二卷回收。", chapter: "第1卷第5章", status: "resolved", resolution: "第2卷第15章" }
      ];
    },

    initializeNovelReader() {
      this.novelTree = this.contentIndex.novelFulltext || [];
      if (!this.selectedNovelChapter && this.novelTree.length > 0) {
        const firstVolume = this.novelTree[0];
        if (firstVolume.chapters && firstVolume.chapters.length > 0) {
          this.openNovelChapter(firstVolume.chapters[0]);
        }
      }
    },

    initializeKeyCharacterPanel() {
      this.keyCharacters = this.contentIndex.keyCharacters || [];
      if (!this.selectedKeyCharacter && this.keyCharacters.length > 0) {
        this.openKeyCharacter(this.keyCharacters[0]);
      }
    },

    async loadModule(module) {
      this.currentModule = module;
      this.showSearch = false;
      this.searchQuery = "";
      this.searchResults = [];

      const staticModules = new Set(["dashboard", "characters", "keyCharacters", "timeline", "clues", "novelFulltext"]);
      if (staticModules.has(module)) {
        if (module === "novelFulltext") {
          this.initializeNovelReader();
        }
        if (module === "keyCharacters") {
          this.initializeKeyCharacterPanel();
        }
        return;
      }

      const filePath = (this.contentIndex.modules || {})[module];
      if (filePath) {
        await this.loadFile(`../${filePath}`);
      }
    },

    async loadFile(path) {
      try {
        const response = await fetch(path);
        this.currentContent = await response.text();
        this.currentFile = path.replace("../", "");
        this.currentTitle = this.extractTitle(this.currentContent);
        this.renderedContent = marked.parse(this.currentContent);
      } catch (e) {
        this.renderedContent = "<p>文件加载失败</p>";
      }
    },

    extractTitle(content) {
      const match = content.match(/^#\s+(.+)$/m);
      return match ? match[1] : "内容";
    },

    toggleSearch() {
      this.showSearch = !this.showSearch;
      if (!this.showSearch) {
        this.searchQuery = "";
        this.searchResults = [];
      }
    },

    handleSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = [];
        return;
      }

      const keyword = this.searchQuery.toLowerCase();
      this.searchResults = [];

      this.allFiles.forEach(file => {
        const pathHit = file.path.toLowerCase().includes(keyword);
        const contentHit = file.content.toLowerCase().includes(keyword);
        if (pathHit || contentHit) {
          const snippet = this.extractSnippet(file.content, this.searchQuery);
          this.searchResults.push({
            path: file.path,
            content: file.content,
            snippet: this.highlightKeyword(snippet, this.searchQuery)
          });
        }
      });
    },

    extractSnippet(content, keyword) {
      const loweredContent = content.toLowerCase();
      const loweredKeyword = keyword.toLowerCase();
      const index = loweredContent.indexOf(loweredKeyword);
      if (index === -1) {
        return content.slice(0, 140) + (content.length > 140 ? "..." : "");
      }
      const start = Math.max(0, index - 50);
      const end = Math.min(content.length, index + 120);
      return "..." + content.substring(start, end) + "...";
    },

    escapeRegex(rawText) {
      return rawText.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    },

    highlightKeyword(text, keyword) {
      const safeKeyword = this.escapeRegex(keyword);
      const regex = new RegExp(`(${safeKeyword})`, "gi");
      return text.replace(regex, "<mark>$1</mark>");
    },

    async viewFile(path) {
      await this.loadFile("../" + path);
      this.currentModule = "content";
      this.showSearch = false;
      this.searchQuery = "";
      this.searchResults = [];
    },

    async openNovelChapter(chapter) {
      try {
        const content = await this.fetchText(chapter.path);
        this.selectedNovelChapter = chapter;
        this.novelCurrentTitle = chapter.title;
        this.novelCurrentContent = content;
        this.novelCurrentFilename = chapter.path.split("/").pop();
        this.novelRenderedContent = marked.parse(content);
      } catch (e) {
        this.novelRenderedContent = "<p>章节加载失败</p>";
      }
    },

    async openKeyCharacter(character) {
      try {
        const content = await this.fetchText(character.path);
        this.selectedKeyCharacter = character;
        this.keyCharacterContent = content;
        this.keyCharacterFilename = character.path.split("/").pop();
        this.keyCharacterRenderedContent = marked.parse(content);
      } catch (e) {
        this.keyCharacterRenderedContent = "<p>人物档案加载失败</p>";
      }
    },

    async copyContent(content) {
      try {
        await navigator.clipboard.writeText(content);
        alert("已复制到剪贴板");
      } catch (e) {
        alert("复制失败");
      }
    },

    downloadFile(filename, content) {
      const blob = new Blob([content], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    },

    startTimelineDrag(e) {
      this.timelineDragging = true;
      this.timelineDragStart = e.clientX - this.timelineOffset;
    },

    onTimelineDrag(e) {
      if (!this.timelineDragging) return;
      e.preventDefault();
      this.timelineOffset = e.clientX - this.timelineDragStart;
    },

    endTimelineDrag() {
      this.timelineDragging = false;
    }
  }
}).mount("#app");
