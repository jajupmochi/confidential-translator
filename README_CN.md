# 机密翻译器 🛡️

[![CI](https://github.com/jajupmochi/confidential-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/jajupmochi/confidential-translator/actions/workflows/ci.yml)
[![Docker](https://github.com/jajupmochi/confidential-translator/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/jajupmochi/confidential-translator/actions/workflows/docker-publish.yml)
[![文档](https://img.shields.io/badge/docs-在线文档-blue?logo=readthedocs)](https://jajupmochi.github.io/confidential-translator/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [English / 英文版](./README.md)

一个**完全离线、隐私优先**的文档翻译系统，由本地大语言模型（通过 [Ollama](https://ollama.com)）驱动。您的数据永远不会离开您的设备。

基于 **Python 3.12 (FastAPI)** + **Vue 3 (Vite + TailwindCSS v4)** 打造，拥有精美的毛玻璃界面和暗色模式。

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🔒 **100% 离线 & 安全** | 完全在本地运行 — 无需联网 |
| 🤖 **本地大模型** | 使用 Qwen 3 / 2.5（或任意 Ollama 模型）实现高质量翻译 |
| 📄 **多格式支持** | PDF、DOCX、XLSX、CSV、Markdown、TXT 及图片（OCR） |
| 🌍 **多语言** | 英语、中文、德语、法语 + 自定义语言输入（AI 验证） |
| ⚡ **实时流式输出** | 通过 SSE 逐 token 查看翻译进度 |
| 📊 **仪表盘 & 分析** | 翻译历史、耗时统计、tokens/秒 报告 |
| 📖 **术语表系统** | 定义领域专用术语映射，确保翻译一致性 |
| 🎨 **现代界面** | 毛玻璃风格设计、暗色模式、国际化（中/英）、响应式布局 |
| 💾 **原生文件对话框** | 跨平台 OS 原生保存/打开对话框（Linux/macOS/Windows） |
| 🐳 **Docker 就绪** | 一行命令部署：`docker compose up` |

## 🚀 快速开始

### Docker（推荐）

```bash
git clone https://github.com/jajupmochi/confidential-translator.git
cd confidential-translator
docker compose up -d
# 打开 http://localhost:8000
```

### 从源码运行

```bash
git clone https://github.com/jajupmochi/confidential-translator.git
cd confidential-translator

# 构建前端
npm install -C frontend
npm run build -C frontend
cp -r frontend/dist/* backend/app/static/

# 运行后端
cd backend && uv sync && uv run python -m app.main
```

### 独立可执行文件

从 [Releases 页面](https://github.com/jajupmochi/confidential-translator/releases) 下载 — 双击即用！

## 🏗️ 架构

```
┌──────────────────┐    REST + SSE    ┌──────────────────┐    Ollama API    ┌─────────────┐
│   Vue 3 前端     │ ───────────────► │  FastAPI 后端     │ ──────────────► │  本地大模型   │
│   (Vite + TS)    │                  │  (Python 3.12)    │                 │  (Ollama)    │
└──────────────────┘                  └────────┬─────────┘                 └─────────────┘
                                               │
                                      ┌────────┴─────────┐
                                      │   SQLite + 文件    │
                                      └──────────────────┘
```

## 🛠️ 技术栈

- **后端**: Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2, `uv`
- **前端**: Vue 3, Vite, TypeScript, Pinia, Vue Router, TailwindCSS v4, vue-i18n
- **文件处理**: PyMuPDF, Tesseract OCR, python-docx, openpyxl, pandas
- **打包**: Docker, PyInstaller, GitHub Actions CI/CD

## 📚 文档

完整文档: **[jajupmochi.github.io/confidential-translator](https://jajupmochi.github.io/confidential-translator/)**

## 📄 许可证

MIT 许可证。详见 [LICENSE](./LICENSE)。
