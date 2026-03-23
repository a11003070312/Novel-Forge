const { createApp } = Vue;

createApp({
  data() {
    return {
      currentModule: 'dashboard',
      currentTitle: '',
      currentContent: '',
      currentFile: '',
      renderedContent: '',
      searchQuery: '',
      searchResults: [],
      showSearch: false,
      allFiles: [],
      stats: { volumes: 0, characters: 0, clues: 0 },
      relationshipNodes: [],
      relationshipEdges: [],
      timelineEvents: [],
      timelineOffset: 0,
      timelineDragging: false,
      timelineDragStart: 0,
      cluesList: []
    };
  },
  async mounted() {
    await this.loadAllFiles();
    this.calculateStats();
    this.initializeRelationshipGraph();
    this.initializeTimeline();
    this.initializeClues();
  },
  methods: {
    async loadAllFiles() {
      const filePaths = [
        '../outline.md',
        '../timeline.md',
        '../worldbuilding/world.md',
        '../worldbuilding/combat-system.md',
        '../characters/protagonists/主角.md',
        '../volumes/vol-01.md',
        '../clues/foreshadowing.md'
      ];

      for (const path of filePaths) {
        try {
          const response = await fetch(path);
          const content = await response.text();
          this.allFiles.push({ path: path.replace('../', ''), content });
        } catch (e) {
          console.log('文件加载失败:', path);
        }
      }
    },

    calculateStats() {
      this.stats.volumes = this.allFiles.filter(f => f.path.startsWith('volumes/')).length;
      this.stats.characters = this.allFiles.filter(f => f.path.startsWith('characters/')).length;
      this.stats.clues = this.allFiles.filter(f => f.path.includes('clues')).length;
    },

    initializeRelationshipGraph() {
      this.relationshipNodes = [
        { id: 1, name: '主角', x: 400, y: 200, radius: 50, type: 'main' },
        { id: 2, name: '师父', x: 250, y: 100, radius: 40, type: 'ally' },
        { id: 3, name: '师兄', x: 550, y: 100, radius: 40, type: 'ally' },
        { id: 4, name: '宿敌', x: 400, y: 350, radius: 45, type: 'enemy' },
        { id: 5, name: '红颜', x: 600, y: 250, radius: 40, type: 'ally' }
      ];
      this.relationshipEdges = [
        { id: 1, x1: 250, y1: 100, x2: 400, y2: 200, label: '师徒' },
        { id: 2, x1: 550, y1: 100, x2: 400, y2: 200, label: '同门' },
        { id: 3, x1: 400, y1: 200, x2: 400, y2: 350, label: '仇敌' },
        { id: 4, x1: 600, y1: 250, x2: 400, y2: 200, label: '情缘' }
      ];
    },

    initializeTimeline() {
      this.timelineEvents = [
        { id: 1, time: '第一章', title: '初入修仙界', description: '主角意外获得传承', position: 0 },
        { id: 2, time: '第五章', title: '拜入宗门', description: '通过考核成为外门弟子', position: 300 },
        { id: 3, time: '第十章', title: '突破境界', description: '炼气期突破至筑基期', position: 600 },
        { id: 4, time: '第十五章', title: '秘境探险', description: '发现上古遗迹', position: 900 },
        { id: 5, time: '第二十章', title: '宗门大比', description: '获得第一名', position: 1200 }
      ];
    },

    initializeClues() {
      this.cluesList = [
        { id: 1, title: '神秘玉佩', content: '主角在第一章获得的玉佩，似乎隐藏着秘密', chapter: '第一章', status: 'pending' },
        { id: 2, title: '师父的过往', content: '师父提到的旧事，暗示着一段不为人知的历史', chapter: '第三章', status: 'pending' },
        { id: 3, title: '古籍记载', content: '在藏书阁发现的古籍，记载了失传的功法', chapter: '第七章', status: 'resolved', resolution: '第十五章：在秘境中找到完整功法' },
        { id: 4, title: '宿敌身份', content: '宿敌的真实身份和目的尚未揭晓', chapter: '第十章', status: 'pending' }
      ];
    },

    async loadModule(module) {
      this.currentModule = module;
      this.showSearch = false;
      this.searchQuery = '';
      this.searchResults = [];

      if (module === 'dashboard' || module === 'characters' || module === 'timeline' || module === 'clues') return;

      const fileMap = {
        outline: '../outline.md',
        worldbuilding: '../worldbuilding/world.md',
        volumes: '../volumes/vol-01.md'
      };

      const filePath = fileMap[module];
      if (filePath) {
        await this.loadFile(filePath);
      }
    },

    async loadFile(path) {
      try {
        const response = await fetch(path);
        this.currentContent = await response.text();
        this.currentFile = path.split('/').pop();
        this.currentTitle = this.extractTitle(this.currentContent);
        this.renderedContent = marked.parse(this.currentContent);
      } catch (e) {
        this.renderedContent = '<p>文件加载失败</p>';
      }
    },

    extractTitle(content) {
      const match = content.match(/^#\s+(.+)$/m);
      return match ? match[1] : '内容';
    },

    toggleSearch() {
      this.showSearch = !this.showSearch;
      if (!this.showSearch) {
        this.searchQuery = '';
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
        if (file.content.toLowerCase().includes(keyword)) {
          const snippet = this.extractSnippet(file.content, keyword);
          this.searchResults.push({
            path: file.path,
            content: file.content,
            snippet: this.highlightKeyword(snippet, this.searchQuery)
          });
        }
      });
    },

    extractSnippet(content, keyword) {
      const index = content.toLowerCase().indexOf(keyword.toLowerCase());
      const start = Math.max(0, index - 50);
      const end = Math.min(content.length, index + 100);
      return '...' + content.substring(start, end) + '...';
    },

    highlightKeyword(text, keyword) {
      const regex = new RegExp(`(${keyword})`, 'gi');
      return text.replace(regex, '<mark>$1</mark>');
    },

    async viewFile(path) {
      await this.loadFile('../' + path);
      this.currentModule = 'content';
      this.showSearch = false;
      this.searchQuery = '';
      this.searchResults = [];
    },

    async copyContent(content) {
      try {
        await navigator.clipboard.writeText(content);
        alert('已复制到剪贴板');
      } catch (e) {
        alert('复制失败');
      }
    },

    downloadFile(filename, content) {
      const blob = new Blob([content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
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
}).mount('#app');
