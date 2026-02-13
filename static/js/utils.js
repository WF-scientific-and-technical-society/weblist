const Utils = {
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
    },
    
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    getFileIcon(filename, isFolder = false) {
        if (isFolder) return '📁';
        
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️',
            'mp4': '🎬', 'avi': '🎬', 'mkv': '🎬', 'mov': '🎬',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
            'txt': '📃', 'md': '📃',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨', 'json': '📋',
            'exe': '⚙️', 'msi': '⚙️'
        };
        return iconMap[ext] || '📄';
    },
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    showConfirm(title, message) {
        return new Promise((resolve) => {
            const modal = document.getElementById('confirmModal');
            const titleEl = document.getElementById('confirmTitle');
            const messageEl = document.getElementById('confirmMessage');
            const okBtn = document.getElementById('confirmOk');
            const cancelBtn = document.getElementById('confirmCancel');
            const closeBtn = document.getElementById('closeConfirmModal');
            
            titleEl.textContent = title;
            messageEl.textContent = message;
            modal.classList.add('show');
            
            const cleanup = () => {
                modal.classList.remove('show');
                okBtn.onclick = null;
                cancelBtn.onclick = null;
                closeBtn.onclick = null;
            };
            
            okBtn.onclick = () => {
                cleanup();
                resolve(true);
            };
            
            cancelBtn.onclick = () => {
                cleanup();
                resolve(false);
            };
            
            closeBtn.onclick = () => {
                cleanup();
                resolve(false);
            };
        });
    },
    
    parsePath(path) {
        const parts = path.split('/').filter(p => p);
        return {
            parts,
            name: parts[parts.length - 1] || '根目录',
            parent: '/' + parts.slice(0, -1).join('/')
        };
    },
    
    buildBreadcrumb(path) {
        const parts = path.split('/').filter(p => p);
        const items = [{ name: '根目录', path: '/' }];
        
        let currentPath = '';
        parts.forEach((part, index) => {
            currentPath += '/' + part;
            items.push({
                name: part,
                path: currentPath
            });
        });
        
        return items;
    },
    
    applyTheme(theme) {
        const root = document.documentElement;
        Object.entries(theme).forEach(([key, value]) => {
            const cssVar = key.replace(/_/g, '-');
            root.style.setProperty(`--${cssVar}`, value);
        });
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    copyToClipboard(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        }
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return Promise.resolve();
    }
};

window.Utils = Utils;
