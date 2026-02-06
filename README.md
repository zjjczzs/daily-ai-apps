# 🎙️ VoxNote - 轻量级本地语音笔记

一个基于Web Speech API的轻量级语音转文字应用，灵感来自voxtral.c项目——证明语音处理可以在本地高效运行。

## ✨ 功能特性

- 🎤 **实时录音**：浏览器直接录音，无需上传服务器
- 📝 **语音转文字**：使用浏览器原生Web Speech API，支持中英文
- 💾 **本地存储**：所有数据保存在浏览器本地，保护隐私
- 📤 **导出功能**：支持导出为Markdown、TXT、JSON格式
- ⌨️ **快捷键支持**：空格键快速开始/停止录音
- 🎨 **简洁界面**：专注写作的极简设计

## 🚀 快速开始

### 环境要求

- Python 3.7+
- 现代浏览器（Chrome/Edge/Safari，需支持Web Speech API）

### 安装运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 打开浏览器访问
http://localhost:5000
```

## 🛠️ 技术栈

- **后端**：Python Flask（轻量级，仅提供静态文件和API）
- **前端**：原生 HTML5 + CSS3 + JavaScript（无框架依赖）
- **语音识别**：Web Speech API（浏览器原生）
- **数据存储**：LocalStorage（纯前端）

## 📖 使用说明

1. **开始录音**：点击麦克风按钮或按空格键
2. **停止录音**：再次点击或按空格键，文字自动保存
3. **查看历史**：左侧边栏显示所有笔记历史
4. **导出笔记**：点击导出按钮选择格式（MD/TXT/JSON）
5. **删除笔记**：悬停在笔记上点击删除图标

## 🔒 隐私说明

- 所有语音处理在浏览器本地完成
- 数据仅存储在浏览器LocalStorage中
- 无需注册账号，无需联网（除语音识别API调用）

## 🌟 项目灵感

本项目灵感来自 **voxtral.c** — Redis作者@antirez的纯C语音模型实现，证明了语音处理可以轻量、高效、本地化。

## 📄 许可证

MIT License

---

*Created by Daily AI Trends App | 2026-02-06*
