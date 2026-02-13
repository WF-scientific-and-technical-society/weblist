document.addEventListener('DOMContentLoaded', async () => {
    await initApp();
    setupEventListeners();
});

async function initApp() {
    const savedView = localStorage.getItem('viewMode') || 'grid';
    State.setView(savedView);
    
    await loadConfig();
    await checkAuth();
    await loadFiles(State.currentPath);
}

async function loadConfig() {
    const result = await API.getConfig();
    if (result.code === 200 && result.data) {
        State.setConfig(result.data);
        applyConfig(result.data);
    }
}

function applyConfig(config) {
    if (config.site) {
        document.title = config.site.title || '个人网盘';
        const titleEl = document.getElementById('siteTitle');
        if (titleEl) titleEl.textContent = config.site.title;
    }
    
    if (config.theme) {
        Utils.applyTheme(config.theme);
    }
    
    if (config.layout) {
        const footer = document.getElementById('appFooter');
        if (footer && config.layout.footer_html) {
            footer.innerHTML = config.layout.footer_html;
        }
        if (footer && config.layout.show_footer === false) {
            footer.style.display = 'none';
        }
    }
}

async function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) userDisplay.textContent = '管理员';
    }
}

async function loadFiles(path) {
    const fileManager = document.getElementById('fileManager');
    const loading = document.getElementById('loading');
    const fileGrid = document.getElementById('fileGrid');
    
    loading.style.display = 'flex';
    fileGrid.innerHTML = '';
    
    const cached = State.getCachedFiles(path);
    if (cached) {
        renderFiles(cached);
        loading.style.display = 'none';
        return;
    }
    
    const result = await API.listFiles(path);
    
    loading.style.display = 'none';
    
    if (result.code === 200 && result.data) {
        State.cacheFiles(path, result.data);
        renderFiles(result.data);
        updateBreadcrumb(path);
    } else {
        showEmptyState();
        Utils.showToast(result.message || '加载失败', 'error');
    }
}

function renderFiles(data) {
    const fileGrid = document.getElementById('fileGrid');
    fileGrid.innerHTML = '';
    
    const folders = data.folders || data.folder || [];
    const files = data.files || data.file || [];
    
    if (folders.length === 0 && files.length === 0) {
        showEmptyState();
        return;
    }
    
    folders.forEach(folder => {
        const item = createFileItem(folder, true);
        fileGrid.appendChild(item);
    });
    
    files.forEach(file => {
        const item = createFileItem(file, false);
        fileGrid.appendChild(item);
    });
    
    updateViewMode();
}

function createFileItem(file, isFolder) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.dataset.id = file.id;
    div.dataset.name = file.name;
    div.dataset.type = isFolder ? 'folder' : 'file';
    
    const icon = Utils.getFileIcon(file.name, isFolder);
    const size = isFolder ? '' : (file.size_formatted || file.size || '');
    
    div.innerHTML = `
        <div class="file-icon">${icon}</div>
        <div class="file-name">${Utils.escapeHtml(file.name)}</div>
        ${size ? `<div class="file-size">${size}</div>` : ''}
    `;
    
    div.addEventListener('click', (e) => handleFileClick(file, isFolder, e));
    div.addEventListener('dblclick', () => handleFileDblClick(file, isFolder));
    div.addEventListener('contextmenu', (e) => showContextMenu(e, file, isFolder));
    
    return div;
}

function handleFileClick(file, isFolder, e) {
    if (e.ctrlKey || e.metaKey) {
        State.toggleFileSelection(file.id);
        e.target.closest('.file-item').classList.toggle('selected');
    }
}

function handleFileDblClick(file, isFolder) {
    if (isFolder) {
        const newPath = State.currentPath === '/' 
            ? `/${file.name}` 
            : `${State.currentPath}/${file.name}`;
        State.setPath(newPath);
        loadFiles(newPath);
    } else {
        downloadFile(file);
    }
}

async function downloadFile(file) {
    const filePath = State.currentPath === '/' 
        ? `/${file.name}` 
        : `${State.currentPath}/${file.name}`;
    
    Utils.showToast('正在获取下载链接...', 'success');
    
    const result = await API.downloadFile(filePath);
    
    if (result.code === 200 && result.data?.url) {
        window.open(result.data.url, '_blank');
    } else {
        Utils.showToast(result.message || '获取下载链接失败', 'error');
    }
}

function updateBreadcrumb(path) {
    const breadcrumb = document.getElementById('breadcrumb');
    const items = Utils.buildBreadcrumb(path);
    
    breadcrumb.innerHTML = items.map((item, index) => {
        const isLast = index === items.length - 1;
        if (isLast) {
            return `<span>${Utils.escapeHtml(item.name)}</span>`;
        }
        return `<a href="#" data-path="${item.path}">${Utils.escapeHtml(item.name)}</a><span>/</span>`;
    }).join('');
    
    breadcrumb.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            const path = e.target.dataset.path;
            State.setPath(path);
            loadFiles(path);
        });
    });
}

function showEmptyState() {
    const fileGrid = document.getElementById('fileGrid');
    fileGrid.innerHTML = `
        <div class="empty-state">
            <div class="empty-icon">📂</div>
            <p>此文件夹为空</p>
        </div>
    `;
}

function updateViewMode() {
    const fileManager = document.getElementById('fileManager');
    const view = State.currentView;
    
    if (view === 'list') {
        fileManager.classList.add('file-list-view');
    } else {
        fileManager.classList.remove('file-list-view');
    }
}

function showContextMenu(e, file, isFolder) {
    e.preventDefault();
    
    const contextMenu = document.getElementById('contextMenu');
    contextMenu.classList.add('show');
    
    const x = e.clientX + window.scrollX;
    const y = e.clientY + window.scrollY;
    
    contextMenu.style.left = `${Math.min(x, window.innerWidth - 160)}px`;
    contextMenu.style.top = `${Math.min(y, window.innerHeight - 200)}px`;
    
    contextMenu.dataset.fileId = file.id;
    contextMenu.dataset.fileName = file.name;
    contextMenu.dataset.isFolder = isFolder;
}

function hideContextMenu() {
    const contextMenu = document.getElementById('contextMenu');
    contextMenu.classList.remove('show');
}

function setupEventListeners() {
    document.getElementById('menuToggle')?.addEventListener('click', () => {
        document.getElementById('sidebar')?.classList.toggle('show');
    });
    
    document.getElementById('gridViewBtn')?.addEventListener('click', () => {
        State.setView('grid');
        updateViewMode();
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('gridViewBtn').classList.add('active');
    });
    
    document.getElementById('listViewBtn')?.addEventListener('click', () => {
        State.setView('list');
        updateViewMode();
        document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('listViewBtn').classList.add('active');
    });
    
    document.getElementById('loginBtn')?.addEventListener('click', () => {
        document.getElementById('loginModal')?.classList.add('show');
    });
    
    document.getElementById('closeLoginModal')?.addEventListener('click', () => {
        document.getElementById('loginModal')?.classList.remove('show');
    });
    
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        const result = await API.login(username, password);
        
        if (result.code === 200) {
            Utils.showToast('登录成功', 'success');
            document.getElementById('loginModal')?.classList.remove('show');
            document.getElementById('userDisplay').textContent = '管理员';
        } else {
            Utils.showToast(result.message || '登录失败', 'error');
        }
    });
    
    document.getElementById('uploadBtn')?.addEventListener('click', () => {
        document.getElementById('uploadModal')?.classList.add('show');
    });
    
    document.getElementById('closeUploadModal')?.addEventListener('click', () => {
        document.getElementById('uploadModal')?.classList.remove('show');
    });
    
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea?.addEventListener('click', () => fileInput?.click());
    
    uploadArea?.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea?.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea?.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileUpload(e.dataTransfer.files);
    });
    
    fileInput?.addEventListener('change', (e) => {
        handleFileUpload(e.target.files);
    });
    
    document.getElementById('newFolderBtn')?.addEventListener('click', () => {
        document.getElementById('newFolderModal')?.classList.add('show');
    });
    
    document.getElementById('closeFolderModal')?.addEventListener('click', () => {
        document.getElementById('newFolderModal')?.classList.remove('show');
    });
    
    document.getElementById('newFolderForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const folderName = document.getElementById('folderName').value;
        
        const result = await API.createFolder(State.currentPath, folderName);
        
        if (result.code === 200 || result.success) {
            Utils.showToast('文件夹创建成功', 'success');
            document.getElementById('newFolderModal')?.classList.remove('show');
            document.getElementById('folderName').value = '';
            State.clearCache();
            loadFiles(State.currentPath);
        } else {
            Utils.showToast(result.message || '创建失败', 'error');
        }
    });
    
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    const performSearch = Utils.debounce(async () => {
        const keyword = searchInput.value.trim();
        if (keyword) {
            const result = await API.searchFiles(keyword, State.currentPath);
            if (result.code === 200 && result.data) {
                renderFiles(result.data);
            }
        } else {
            loadFiles(State.currentPath);
        }
    }, 300);
    
    searchInput?.addEventListener('input', performSearch);
    searchBtn?.addEventListener('click', performSearch);
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const path = link.dataset.path;
            if (path && path !== '/recent' && path !== '/shared') {
                State.setPath(path);
                loadFiles(path);
            }
        });
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.context-menu')) {
            hideContextMenu();
        }
    });
    
    document.querySelectorAll('.context-menu li').forEach(item => {
        item.addEventListener('click', async () => {
            const action = item.dataset.action;
            const contextMenu = document.getElementById('contextMenu');
            const fileName = contextMenu.dataset.fileName;
            const isFolder = contextMenu.dataset.isFolder === 'true';
            const filePath = State.currentPath === '/' 
                ? `/${fileName}` 
                : `${State.currentPath}/${fileName}`;
            
            hideContextMenu();
            
            switch (action) {
                case 'download':
                    if (!isFolder) {
                        downloadFile({ name: fileName });
                    }
                    break;
                case 'share':
                    const shareResult = await API.shareFile(filePath);
                    if (shareResult.code === 200 && shareResult.data) {
                        Utils.copyToClipboard(shareResult.data.share_url);
                        Utils.showToast('分享链接已复制', 'success');
                    }
                    break;
                case 'delete':
                    const confirmed = await Utils.showConfirm('确认删除', `确定要删除 ${fileName} 吗？`);
                    if (confirmed) {
                        const deleteResult = await API.deleteFile(filePath);
                        if (deleteResult.code === 200 || deleteResult.success) {
                            Utils.showToast('删除成功', 'success');
                            State.clearCache();
                            loadFiles(State.currentPath);
                        } else {
                            Utils.showToast(deleteResult.message || '删除失败', 'error');
                        }
                    }
                    break;
            }
        });
    });
    
    window.addEventListener('authRequired', () => {
        document.getElementById('loginModal')?.classList.add('show');
    });
}

async function handleFileUpload(files) {
    const uploadList = document.getElementById('uploadList');
    
    for (const file of files) {
        const item = document.createElement('div');
        item.className = 'upload-item';
        item.innerHTML = `
            <span class="name">${Utils.escapeHtml(file.name)}</span>
            <div class="progress">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
            <span class="status">上传中...</span>
        `;
        uploadList.appendChild(item);
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', State.currentPath);
        
        try {
            const result = await API.uploadFile(formData, (progress) => {
                item.querySelector('.progress-bar').style.width = `${progress}%`;
            });
            
            if (result.code === 200 || result.success) {
                item.querySelector('.status').textContent = '完成';
                Utils.showToast(`${file.name} 上传成功`, 'success');
            } else {
                item.querySelector('.status').textContent = '失败';
                Utils.showToast(result.message || '上传失败', 'error');
            }
        } catch (error) {
            item.querySelector('.status').textContent = '失败';
            Utils.showToast('上传失败', 'error');
        }
    }
    
    State.clearCache();
    setTimeout(() => loadFiles(State.currentPath), 1000);
}
