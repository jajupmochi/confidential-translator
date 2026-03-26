# 本地机密翻译系统 🛡️ (Confidential Translator)

[![CI](https://github.com/example/confidential-translator/actions/workflows/ci.yml/badge.svg)](https://github.com/example/confidential-translator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [English README](./README.md)

一个完全离线、隐私优先的本地文档翻译系统。由本地大语言模型（如 Qwen 系列，通过 Ollama 部署）驱动。

使用 **Python 3.12 (FastAPI)** 和 **Vue 3 (Vite + TailwindCSS)** 构建，具有毛玻璃风格的现代 UI 界面。

## ✨ 核心特性

- **100% 离线安全**: 您的数据永远不会离开本地机器。
- **本地大模型支持**: 默认使用 `qwen3:14b-q4_K_M`，支持根据硬件自动推荐和切换任何 Ollama 模型。
- **丰富的格式支持**: 支持翻译普通文本、PDF、图片（OCR）、DOCX、Markdown、Excel表格 (XLSX, CSV)。
- **原格式导出**: 翻译后可直接导出为原始文件格式。
- **现代 UI 界面**: 基于 Vue 3 的毛玻璃效果设计，支持深色模式。
- **历史与统计**: 内置 SQLite 数据库，记录所有翻译历史、耗时、模型推断速度（Tokens/s）。
- **跨平台**: 提供 Linux (AppImage/Deb), Windows (Exe), macOS (Dmg) 的一键安装包。

## 🚀 快速开始

### 独立安装包（推荐）
从 [Releases 页面](https://github.com/example/confidential-translator/releases) 下载适用于您系统的最新版独立执行程序。

1. 双击运行下载的程序。
2. **这就够了！** 翻译系统会自动在后台尝试启动 `ollama`，并在您的默认浏览器中自动打开界面 (`http://127.0.0.1:8000`)。

*（如果您尚未安装 Ollama 模型引擎，浏览器界面将指引您完成轻量化安装配置）*

### 从源码运行

```bash
# 下载源码
git clone https://github.com/example/confidential-translator.git
cd confidential-translator

# 编译运行 (需要 `uv` 和 `npm`)
npm install -C frontend
npm run build -C frontend
cp -r frontend/dist/* backend/app/static/

cd backend
uv sync

# 运行程序（会自动启动 Ollama 服务并打开浏览器！）
uv run python -m app.main
```

## 📚 项目文档

完整的开发与使用文档请参考 [MkDocs 文档页](https://example.github.io/confidential-translator/)。

## 📄 许可证

MIT License. 详情参见 `LICENSE` 文件。
