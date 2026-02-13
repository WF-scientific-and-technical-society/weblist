const State = {
    currentPath: '/',
    currentView: 'grid',
    selectedFiles: [],
    config: null,
    user: null,
    fileCache: new Map(),
    
    setPath(path) {
        this.currentPath = path;
        window.dispatchEvent(new CustomEvent('pathChanged', { detail: path }));
    },
    
    setView(view) {
        this.currentView = view;
        localStorage.setItem('viewMode', view);
        window.dispatchEvent(new CustomEvent('viewChanged', { detail: view }));
    },
    
    toggleFileSelection(fileId) {
        const index = this.selectedFiles.indexOf(fileId);
        if (index === -1) {
            this.selectedFiles.push(fileId);
        } else {
            this.selectedFiles.splice(index, 1);
        }
        window.dispatchEvent(new CustomEvent('selectionChanged', { detail: this.selectedFiles }));
    },
    
    clearSelection() {
        this.selectedFiles = [];
        window.dispatchEvent(new CustomEvent('selectionChanged', { detail: [] }));
    },
    
    setConfig(config) {
        this.config = config;
        window.dispatchEvent(new CustomEvent('configChanged', { detail: config }));
    },
    
    setUser(user) {
        this.user = user;
        window.dispatchEvent(new CustomEvent('userChanged', { detail: user }));
    },
    
    cacheFiles(path, files) {
        this.fileCache.set(path, {
            files,
            timestamp: Date.now()
        });
    },
    
    getCachedFiles(path) {
        const cached = this.fileCache.get(path);
        if (cached && Date.now() - cached.timestamp < 60000) {
            return cached.files;
        }
        return null;
    },
    
    clearCache() {
        this.fileCache.clear();
    }
};

window.State = State;
