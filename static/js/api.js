const API = {
    baseUrl: '/api',
    token: localStorage.getItem('token'),
    
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    },
    
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    },
    
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    },
    
    async request(method, endpoint, data = null) {
        const options = {
            method,
            headers: this.getHeaders()
        };
        
        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, options);
            const result = await response.json();
            
            if (response.status === 401) {
                this.clearToken();
                window.dispatchEvent(new CustomEvent('authRequired'));
            }
            
            return result;
        } catch (error) {
            console.error('API Error:', error);
            return { code: 500, message: '网络错误', data: null };
        }
    },
    
    get(endpoint) {
        return this.request('GET', endpoint);
    },
    
    post(endpoint, data) {
        return this.request('POST', endpoint, data);
    },
    
    put(endpoint, data) {
        return this.request('PUT', endpoint, data);
    },
    
    patch(endpoint, data) {
        return this.request('PATCH', endpoint, data);
    },
    
    delete(endpoint) {
        return this.request('DELETE', endpoint);
    },
    
    async getConfig() {
        return this.get('/config');
    },
    
    async getConfigSection(section) {
        return this.get(`/config/${section}`);
    },
    
    async updateConfig(data) {
        return this.put('/config', data);
    },
    
    async updateConfigSection(section, data) {
        return this.patch(`/config/${section}`, data);
    },
    
    async validateConfig(data) {
        return this.post('/config/validate', data);
    },
    
    async createBackup() {
        return this.post('/config/backup');
    },
    
    async getBackups() {
        return this.get('/config/backups');
    },
    
    async restoreBackup(backupId) {
        return this.post(`/config/restore/${backupId}`);
    },
    
    async login(username, password) {
        const response = await fetch(`${this.baseUrl}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const result = await response.json();
        if (result.code === 200 && result.data?.token) {
            this.setToken(result.data.token);
        }
        return result;
    },
    
    async logout() {
        this.clearToken();
        return { code: 200, message: '已退出登录' };
    },
    
    async checkAuth() {
        if (!this.token) return { code: 401 };
        return this.get('/auth/check');
    },
    
    async listFiles(path = '/') {
        const params = new URLSearchParams({ path });
        return this.get(`/files?${params}`);
    },
    
    async uploadFile(formData, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', `${this.baseUrl}/upload`);
            if (this.token) {
                xhr.setRequestHeader('Authorization', `Bearer ${this.token}`);
            }
            
            xhr.upload.onprogress = (e) => {
                if (onProgress && e.lengthComputable) {
                    onProgress(Math.round((e.loaded / e.total) * 100));
                }
            };
            
            xhr.onload = () => {
                try {
                    resolve(JSON.parse(xhr.responseText));
                } catch {
                    resolve({ code: 500, message: '上传失败' });
                }
            };
            
            xhr.onerror = () => reject(new Error('上传失败'));
            xhr.send(formData);
        });
    },
    
    async downloadFile(path) {
        return this.get(`/download?path=${encodeURIComponent(path)}`);
    },
    
    async deleteFile(path) {
        return this.delete(`/files?path=${encodeURIComponent(path)}`);
    },
    
    async createFolder(parentPath, name) {
        return this.post('/folder', { parentPath, name });
    },
    
    async shareFile(path) {
        return this.post('/share', { path });
    },
    
    async searchFiles(keyword, path = '/') {
        return this.get(`/search?keyword=${encodeURIComponent(keyword)}&path=${encodeURIComponent(path)}`);
    },
    
    async getLogs(page = 1, pageSize = 20) {
        return this.get(`/logs?page=${page}&page_size=${pageSize}`);
    }
};

window.API = API;
