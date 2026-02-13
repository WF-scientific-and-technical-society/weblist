let originalConfig = null;
let currentConfig = null;

document.addEventListener('DOMContentLoaded', async () => {
    await initSettings();
    setupSettingsListeners();
});

async function initSettings() {
    const token = localStorage.getItem('token');
    if (!token) {
        document.getElementById('loginModal')?.classList.add('show');
        return;
    }
    
    await loadSettings();
}

async function loadSettings() {
    const result = await API.getConfig();
    
    if (result.code === 200 && result.data) {
        originalConfig = JSON.parse(JSON.stringify(result.data));
        currentConfig = result.data;
        populateSettings(result.data);
        applyTheme(result.data.theme);
    } else {
        Utils.showToast(result.message || '加载配置失败', 'error');
    }
}

function populateSettings(config) {
    document.querySelectorAll('[data-config]').forEach(el => {
        const path = el.dataset.config.split('.');
        let value = config;
        
        for (const key of path) {
            value = value?.[key];
        }
        
        if (value !== undefined) {
            if (el.type === 'checkbox') {
                el.checked = value;
            } else if (Array.isArray(value)) {
                el.value = value.join(', ');
            } else {
                el.value = value;
            }
            
            if (el.type === 'color') {
                const textInput = document.getElementById(el.id + 'Text');
                if (textInput) textInput.value = value;
            }
        }
    });
    
    updateFileSizeDisplay();
}

function setupSettingsListeners() {
    document.querySelectorAll('.settings-nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            
            document.querySelectorAll('.settings-nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            document.querySelectorAll('.settings-section').forEach(s => s.style.display = 'none');
            document.getElementById(section).style.display = 'block';
        });
    });
    
    document.querySelectorAll('[data-config]').forEach(el => {
        el.addEventListener('change', () => {
            updateConfigFromInput(el);
        });
        
        el.addEventListener('input', () => {
            if (el.type === 'color') {
                const textInput = document.getElementById(el.id + 'Text');
                if (textInput) textInput.value = el.value;
                updateConfigFromInput(el);
            }
        });
    });
    
    document.querySelectorAll('.color-input input[type="text"]').forEach(el => {
        el.addEventListener('change', () => {
            const colorInput = document.getElementById(el.id.replace('Text', ''));
            if (colorInput && /^#[0-9A-Fa-f]{6}$/.test(el.value)) {
                colorInput.value = el.value;
                updateConfigFromInput(colorInput);
            }
        });
    });
    
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = btn.dataset.preset;
            applyPreset(preset);
        });
    });
    
    document.getElementById('saveBtn')?.addEventListener('click', saveSettings);
    document.getElementById('resetBtn')?.addEventListener('click', resetSettings);
    document.getElementById('createBackupBtn')?.addEventListener('click', createBackup);
    document.getElementById('restoreDefaultBtn')?.addEventListener('click', restoreDefault);
    
    document.getElementById('maxFileSize')?.addEventListener('input', updateFileSizeDisplay);
    
    document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        const result = await API.login(username, password);
        
        if (result.code === 200) {
            Utils.showToast('登录成功', 'success');
            document.getElementById('loginModal')?.classList.remove('show');
            loadSettings();
        } else {
            Utils.showToast(result.message || '登录失败', 'error');
        }
    });
    
    document.getElementById('closeLoginModal')?.addEventListener('click', () => {
        document.getElementById('loginModal')?.classList.remove('show');
    });
    
    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        await API.logout();
        Utils.showToast('已退出登录', 'success');
        setTimeout(() => window.location.reload(), 500);
    });
}

function updateConfigFromInput(el) {
    const path = el.dataset.config.split('.');
    const value = el.type === 'checkbox' ? el.checked : el.value;
    
    let obj = currentConfig;
    for (let i = 0; i < path.length - 1; i++) {
        obj = obj[path[i]];
    }
    
    const lastKey = path[path.length - 1];
    
    if (el.dataset.config.includes('allowed_types') || el.dataset.config.includes('keywords')) {
        obj[lastKey] = value.split(',').map(s => s.trim()).filter(s => s);
    } else if (el.type === 'number') {
        obj[lastKey] = parseInt(value) || 0;
    } else {
        obj[lastKey] = value;
    }
    
    if (el.dataset.config.startsWith('theme.')) {
        applyTheme(currentConfig.theme);
    }
}

function applyTheme(theme) {
    if (!theme) return;
    
    Utils.applyTheme(theme);
    
    const previewBox = document.getElementById('themePreview');
    if (previewBox) {
        previewBox.style.setProperty('--primary-color', theme.primary_color);
        previewBox.style.setProperty('--background-color', theme.background_color);
        previewBox.style.setProperty('--text-color', theme.text_color);
    }
}

function applyPreset(preset) {
    const presets = {
        default: {
            primary_color: '#1890ff',
            secondary_color: '#52c41a',
            background_color: '#f5f5f5',
            text_color: '#333333',
            border_color: '#d9d9d9',
            hover_color: '#40a9ff'
        },
        green: {
            primary_color: '#52c41a',
            secondary_color: '#1890ff',
            background_color: '#f6ffed',
            text_color: '#333333',
            border_color: '#b7eb8f',
            hover_color: '#73d13d'
        },
        purple: {
            primary_color: '#722ed1',
            secondary_color: '#eb2f96',
            background_color: '#f9f0ff',
            text_color: '#333333',
            border_color: '#d3adf7',
            hover_color: '#9254de'
        },
        dark: {
            primary_color: '#177ddc',
            secondary_color: '#49aa19',
            background_color: '#141414',
            text_color: '#e0e0e0',
            border_color: '#434343',
            hover_color: '#3c9ae8'
        }
    };
    
    const theme = presets[preset];
    if (theme) {
        currentConfig.theme = { ...currentConfig.theme, ...theme };
        populateSettings(currentConfig);
        applyTheme(theme);
    }
}

function updateFileSizeDisplay() {
    const input = document.getElementById('maxFileSize');
    const display = document.getElementById('maxFileSizeDisplay');
    if (input && display) {
        display.textContent = Utils.formatFileSize(parseInt(input.value) || 0);
    }
}

async function saveSettings() {
    const validation = await API.validateConfig(currentConfig);
    
    if (!validation.data?.valid) {
        Utils.showToast(validation.data?.errors?.join(', ') || '配置验证失败', 'error');
        return;
    }
    
    const result = await API.updateConfig(currentConfig);
    
    if (result.code === 200) {
        Utils.showToast('设置保存成功', 'success');
        originalConfig = JSON.parse(JSON.stringify(currentConfig));
        applyTheme(currentConfig.theme);
    } else {
        Utils.showToast(result.message || '保存失败', 'error');
    }
}

function resetSettings() {
    if (originalConfig) {
        currentConfig = JSON.parse(JSON.stringify(originalConfig));
        populateSettings(currentConfig);
        applyTheme(currentConfig.theme);
        Utils.showToast('已重置为上次保存的设置', 'success');
    }
}

async function createBackup() {
    const result = await API.createBackup();
    
    if (result.code === 200) {
        Utils.showToast('备份创建成功', 'success');
        loadBackups();
    } else {
        Utils.showToast(result.message || '备份失败', 'error');
    }
}

async function loadBackups() {
    const result = await API.getBackups();
    const backupList = document.getElementById('backupList');
    
    if (result.code === 200 && result.data?.backups) {
        if (result.data.backups.length === 0) {
            backupList.innerHTML = '<p class="empty-state">暂无备份</p>';
            return;
        }
        
        backupList.innerHTML = result.data.backups.map(backup => `
            <div class="backup-item">
                <div class="backup-info">
                    <div>${backup.backup_id}</div>
                    <div class="backup-time">${Utils.formatDate(backup.created_at)}</div>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="restoreBackup('${backup.backup_id}')">恢复</button>
            </div>
        `).join('');
    }
}

async function restoreBackup(backupId) {
    const confirmed = await Utils.showConfirm('确认恢复', '恢复备份将覆盖当前配置，确定要继续吗？');
    
    if (confirmed) {
        const result = await API.restoreBackup(backupId);
        
        if (result.code === 200) {
            Utils.showToast('配置已恢复', 'success');
            loadSettings();
        } else {
            Utils.showToast(result.message || '恢复失败', 'error');
        }
    }
}

async function restoreDefault() {
    const confirmed = await Utils.showConfirm('确认恢复', '确定要恢复默认设置吗？');
    
    if (confirmed) {
        const defaultConfig = {
            site: {
                title: '个人网盘',
                description: '基于123网盘的个人文件管理系统',
                keywords: ['网盘', '文件管理', '云存储']
            },
            theme: {
                primary_color: '#1890ff',
                secondary_color: '#52c41a',
                background_color: '#f5f5f5',
                text_color: '#333333',
                border_color: '#d9d9d9',
                hover_color: '#40a9ff'
            },
            upload: {
                max_file_size: 2147483648,
                allowed_types: ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'zip', 'rar']
            }
        };
        
        currentConfig = defaultConfig;
        populateSettings(currentConfig);
        applyTheme(currentConfig.theme);
        Utils.showToast('已恢复默认设置，请点击保存按钮生效', 'success');
    }
}

window.restoreBackup = restoreBackup;
