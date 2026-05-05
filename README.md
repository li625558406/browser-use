# Browser-Use WebUI

> 基于 [browser-use](https://github.com/browser-use/browser-use) 的 Web 可视化界面，提供定时任务数据采集和 AI 浏览器自动化功能

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.5+-green.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 特性

- 🤖 **AI 驱动的浏览器自动化** - 利用 LLM 理解网页并执行复杂操作
- 📋 **任务管理** - 创建、编辑、删除自动化任务
- 📝 **Prompt 管理** - 灵活配置和管理任务提示词模板
- ⚙️ **LLM 配置** - 支持多种大模型（DeepSeek、OpenAI、Anthropic、Ollama 等）
- 📊 **执行监控** - 实时查看任务执行状态和结果
- 📤 **数据导出** - 导出执行结果为多种格式
- 🔄 **定时执行** - 支持定时任务调度
- 🔐 **域名登录状态管理** - 记住已登录域名，避免重复登录

## 🏗️ 架构

```
browser-use-webui/
├── backend/           # FastAPI 后端
│   ├── api/          # API 路由
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # 业务逻辑
│   ├── database.py   # 数据库配置
│   └── main.py       # 应用入口
├── frontend/         # Vue 3 前端
│   ├── src/
│   │   ├── api/      # API 客户端
│   │   ├── components/  # Vue 组件
│   │   ├── views/     # 页面视图
│   │   └── router/   # 路由配置
│   └── package.json
└── browser_use/      # browser-use 核心库
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Chrome 浏览器（用于 CDP 连接）

### 安装

1. **克隆仓库**
```bash
git clone https://github.com/li625558406/browser-use.git
cd browser-use
```

2. **后端设置**
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
uv sync
```

3. **前端设置**
```bash
cd frontend
npm install
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的参数
```

### 运行

**启动后端**：
```bash
python -m backend.main
```

**启动前端**（新终端）：
```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 查看应用界面。

## 📖 使用指南

### 1. 配置 LLM

在 **LLM 配置** 页面添加你想要使用的大模型配置：

- **DeepSeek** - 需要提供 API Key 和 Base URL
- **OpenAI** - 需要提供 API Key
- **Anthropic** - 需要提供 API Key
- **Ollama** - 本地模型，需要提供 Base URL（默认：http://localhost:11434）

### 2. 创建 Prompt

在 **Prompt 管理** 页面创建任务提示词模板：

```markdown
# 任务标题

你是一个专业的数据采集专家。你的任务是从 {{url}} 采集以下信息：

- 项目名称
- Star 数
- 编程语言

请高效完成任务，最大采集 {{max_items}} 个项目。
```

### 3. 创建任务

在 **任务管理** 页面创建新任务：

- **任务名称**: 任务描述
- **目标 URL**: 要访问的网址
- **Prompt 模板**: 选择已创建的 Prompt
- **LLM 配置**: 选择要使用的模型
- **需要登录**: 是否需要登录（已登录域名会自动跳过）
- **最大采集数**: 限制采集的项目数量

### 4. 执行任务

- 点击任务卡片上的 **执行** 按钮开始任务
- 在 **执行记录** 页面查看执行进度
- 执行完成后可查看详细日志和输出结果

### 5. 导出数据

在 **数据查看** 页面：
- 查看所有执行结果
- 导出为 JSON、CSV、Markdown 等格式

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | SQLite 数据库路径 | `sqlite:///./data/database.db` |
| `CORS_ORIGINS` | CORS 允许的源 | `http://localhost:5173` |
| `CHROME_PATH` | Chrome 可执行文件路径 | 自动检测 |

### 支持的 LLM 提供商

| 提供商 | 模型示例 | 配置要求 |
|--------|----------|----------|
| DeepSeek | deepseek-chat, deepseek-reasoner | api_key, base_url |
| OpenAI | gpt-4o, gpt-4o-mini | api_key |
| Anthropic | claude-3-5-sonnet-20241022 | api_key |
| Ollama | deepseek-r1:14b, llama3.1 | base_url（可选） |
| Groq | llama-3.3-8b-free | api_key, base_url |

## 📁 项目结构

### 后端 API

- `/api/tasks` - 任务管理 CRUD
- `/api/prompts` - Prompt 管理 CRUD
- `/api/llm-configs` - LLM 配置 CRUD
- `/api/executions` - 执行记录查询和控制

### 核心服务

- `TaskExecutor` - 任务执行器，负责初始化浏览器会话和运行 Agent
- `DomainRegistry` - 域名登录状态管理
- `BrowserProfile` - 浏览器配置文件管理

### 前端页面

- `/tasks` - 任务管理
- `/prompts` - Prompt 管理
- `/llm-configs` - LLM 配置
- `/executions` - 执行记录
- `/data` - 数据查看

## 🛠️ 开发

### 类型检查

```bash
# 后端类型检查
uv run pyright

# 前端类型检查
cd frontend
npm run type-check
```

### 代码格式化

```bash
# Python 代码格式化
uv run ruff check --fix
uv run ruff format

# 前端代码格式化
cd frontend
npm run lint
```

### 运行测试

```bash
# 运行所有测试
uv run pytest -vxs tests/

# 运行 CI 测试
uv run pytest -vxs tests/ci
```

## 🐛 调试

### Chrome CDP 调试

项目提供了两个脚本用于启动可调试的 Chrome：

```bash
# Windows (批处理)
start-chrome-debug.bat

# Windows (PowerShell)
start-chrome-debug.ps1
```

这将以远程调试模式启动 Chrome，便于开发调试。

### 日志级别

后端日志级别可通过环境变量或配置文件设置。

## 📝 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

本项目基于以下优秀的开源项目：

- [browser-use](https://github.com/browser-use/browser-use) - AI 浏览器自动化核心库
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库

## 📮 联系方式

- 项目地址: [https://github.com/li625558406/browser-use](https://github.com/li625558406/browser-use)
- 问题反馈: [Issues](https://github.com/li625558406/browser-use/issues)

## 🔄 更新日志

### v1.0.0 (2025-05-05)

- ✅ 基础 WebUI 功能实现
- ✅ 支持 DeepSeek、OpenAI、Anthropic、Ollama 等多种 LLM
- ✅ 任务管理和执行功能
- ✅ Prompt 模板管理
- ✅ 域名登录状态管理
- ✅ 数据导出功能
- ✅ Ollama 本地模型支持优化
- ✅ UTF-8 编码支持（emoji 字符）
- ✅ CDP 初始化竞态条件修复
