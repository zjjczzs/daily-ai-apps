/**
 * VoxNote - 轻量级语音笔记应用
 * 基于Web Speech API，灵感来自voxtral.c项目
 */

// 全局状态
let isRecording = false;
let recognition = null;
let currentNoteId = null;
let notes = [];

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initSpeechRecognition();
    loadNotes();
    setupKeyboardShortcuts();
});

// 初始化语音识别
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        showStatus('您的浏览器不支持语音识别，请使用Chrome或Edge', 'error');
        document.getElementById('recordBtn').disabled = true;
        return;
    }
    
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    
    recognition.onstart = () => {
        isRecording = true;
        updateRecordButton();
        showStatus('正在录音...', 'recording');
    };
    
    recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        const editor = document.getElementById('noteEditor');
        if (finalTranscript) {
            editor.value += finalTranscript;
            autoSave();
        }
    };
    
    recognition.onerror = (event) => {
        console.error('语音识别错误:', event.error);
        if (event.error === 'not-allowed') {
            showStatus('请允许麦克风权限', 'error');
        } else if (event.error === 'network') {
            showStatus('网络错误，请检查连接', 'error');
        } else {
            showStatus('录音出错: ' + event.error, 'error');
        }
        stopRecording();
    };
    
    recognition.onend = () => {
        if (isRecording) {
            // 如果还在录音状态，自动重启
            try {
                recognition.start();
            } catch (e) {
                stopRecording();
            }
        } else {
            showStatus('录音已停止', '');
        }
    };
}

// 切换录音状态
function toggleRecording() {
    if (!recognition) {
        showStatus('语音识别未初始化', 'error');
        return;
    }
    
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// 开始录音
function startRecording() {
    const lang = document.getElementById('languageSelect').value;
    recognition.lang = lang;
    
    try {
        recognition.start();
    } catch (e) {
        showStatus('无法启动录音: ' + e.message, 'error');
    }
}

// 停止录音
function stopRecording() {
    isRecording = false;
    try {
        recognition.stop();
    } catch (e) {}
    updateRecordButton();
    autoSave();
}

// 更新录音按钮状态
function updateRecordButton() {
    const btn = document.getElementById('recordBtn');
    const icon = btn.querySelector('.mic-icon');
    const text = btn.querySelector('.record-text');
    
    if (isRecording) {
        btn.classList.add('recording');
        icon.textContent = '⏹️';
        text.textContent = '停止录音';
    } else {
        btn.classList.remove('recording');
        icon.textContent = '🎤';
        text.textContent = '开始录音';
    }
}

// 显示状态信息
function showStatus(message, type) {
    const status = document.getElementById('recordingStatus');
    status.textContent = message;
    status.style.color = type === 'error' ? 'var(--recording)' : 
                        type === 'recording' ? 'var(--success)' : 'var(--text-muted)';
    
    if (type !== 'recording' && type !== 'error') {
        setTimeout(() => {
            status.textContent = '';
        }, 3000);
    }
}

// 键盘快捷键
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // 空格键开始/停止录音（不在输入框时）
        if (e.code === 'Space' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'SELECT') {
            e.preventDefault();
            toggleRecording();
        }
        
        // Ctrl/Cmd + S 保存
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveCurrentNote();
        }
    });
    
    // 输入时自动保存
    document.getElementById('noteEditor').addEventListener('input', debounce(autoSave, 1000));
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 自动保存
function autoSave() {
    const content = document.getElementById('noteEditor').value.trim();
    if (!content) return;
    
    if (!currentNoteId) {
        currentNoteId = Date.now().toString();
    }
    
    const note = {
        id: currentNoteId,
        content: content,
        updatedAt: new Date().toISOString()
    };
    
    // 更新或添加笔记
    const index = notes.findIndex(n => n.id === currentNoteId);
    if (index >= 0) {
        notes[index] = note;
    } else {
        notes.unshift(note);
    }
    
    saveToStorage();
    renderNotesList();
}

// 保存当前笔记（手动）
function saveCurrentNote() {
    autoSave();
    showStatus('已保存', 'success');
}

// 保存到本地存储
function saveToStorage() {
    localStorage.setItem('voxnote_notes', JSON.stringify(notes));
}

// 从本地存储加载
function loadNotes() {
    const stored = localStorage.getItem('voxnote_notes');
    if (stored) {
        notes = JSON.parse(stored);
        renderNotesList();
    }
}

// 渲染笔记列表
function renderNotesList() {
    const list = document.getElementById('notesList');
    
    if (notes.length === 0) {
        list.innerHTML = '<div class="empty-state">暂无笔记，开始录音吧！</div>';
        return;
    }
    
    list.innerHTML = notes.map(note => {
        const date = new Date(note.updatedAt);
        const timeStr = date.toLocaleString('zh-CN', { 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        const preview = note.content.substring(0, 60) + (note.content.length > 60 ? '...' : '');
        const isActive = note.id === currentNoteId;
        
        return `
            <div class="note-item ${isActive ? 'active' : ''}" onclick="loadNote('${note.id}')">
                <div class="note-preview">${escapeHtml(preview)}</div>
                <div class="note-meta">
                    <span>${timeStr}</span>
                    <button class="delete-btn" onclick="event.stopPropagation(); deleteNote('${note.id}')">🗑️</button>
                </div>
            </div>
        `;
    }).join('');
}

// 加载指定笔记
function loadNote(id) {
    const note = notes.find(n => n.id === id);
    if (note) {
        currentNoteId = id;
        document.getElementById('noteEditor').value = note.content;
        renderNotesList();
    }
}

// 删除笔记
function deleteNote(id) {
    if (!confirm('确定要删除这条笔记吗？')) return;
    
    notes = notes.filter(n => n.id !== id);
    saveToStorage();
    
    if (currentNoteId === id) {
        currentNoteId = null;
        document.getElementById('noteEditor').value = '';
    }
    
    renderNotesList();
}

// 清空当前编辑区
function clearCurrent() {
    if (document.getElementById('noteEditor').value && !confirm('确定要清空当前内容吗？')) {
        return;
    }
    document.getElementById('noteEditor').value = '';
    currentNoteId = null;
    renderNotesList();
}

// 复制到剪贴板
function copyToClipboard() {
    const content = document.getElementById('noteEditor').value;
    if (!content) {
        showStatus('没有内容可复制', 'error');
        return;
    }
    
    navigator.clipboard.writeText(content).then(() => {
        showStatus('已复制到剪贴板', 'success');
    }).catch(() => {
        showStatus('复制失败', 'error');
    });
}

// 导出功能
let exportTarget = 'current'; // 'current' 或 'all'

function exportAllNotes() {
    exportTarget = 'all';
    document.getElementById('exportModal').classList.add('active');
}

function exportNotes(format) {
    const content = exportTarget === 'current' 
        ? document.getElementById('noteEditor').value
        : notes.map(n => n.content).join('\n\n---\n\n');
    
    let filename, mimeType, data;
    const timestamp = new Date().toISOString().split('T')[0];
    
    switch(format) {
        case 'md':
            filename = `voxnote-${timestamp}.md`;
            mimeType = 'text/markdown';
            data = `# VoxNote 导出\n\n${content}`;
            break;
        case 'txt':
            filename = `voxnote-${timestamp}.txt`;
            mimeType = 'text/plain';
            data = content;
            break;
        case 'json':
            filename = `voxnote-${timestamp}.json`;
            mimeType = 'application/json';
            data = JSON.stringify(exportTarget === 'all' ? notes : { content }, null, 2);
            break;
    }
    
    downloadFile(data, filename, mimeType);
    closeModal();
    showStatus('导出成功', 'success');
}

// 下载文件
function downloadFile(data, filename, mimeType) {
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 关闭模态框
function closeModal() {
    document.getElementById('exportModal').classList.remove('active');
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 语言切换时更新识别语言
document.getElementById('languageSelect')?.addEventListener('change', function() {
    if (recognition) {
        recognition.lang = this.value;
    }
    if (isRecording) {
        stopRecording();
        setTimeout(startRecording, 300);
    }
});
