# Browser-Use WebUI 设计文档

**项目名称**: Browser-Use WebUI - 定时任务数据采集系统
**创建日期**: 2026-05-04
**作者**: Claude Code
**状态**: 设计阶段

---

## 一、项目概述

### 1.1 项目目标

基于 browser-use 开源项目，开发一个带有 Web 界面的定时任务数据采集系统，实现：

- 定时执行浏览器自动化任务
- 动态配置 LLM（支持 DeepSeek、本地模型等）
- 复用用户真实浏览器（已登录状态）
- 数据采集后生成 MD 文档并分类存储
- Web 界面查看和管理

### 1.2 部署环境

- **目标环境**: 仅本地电脑（Windows）
- **后端**: Docker 容器化（可选）
- **前端**: 本地开发服务器

### 1.3 用户故事

作为用户，我希望：
1. 设置定时任务，每天自动采集特定网站的数据
2. 使用我已登录的 Chrome 浏览器，无需重复登录
3. 在 Web 界面上查看分类好的采集数据
4. 配置不同的 LLM 用于不同任务
5. 导出采集结果为 Markdown 文档

---

## 二、技术架构

### 2.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + Vite | 现代化前端框架 |
| **UI 组件** | Element Plus | Vue 3 组件库 |
| **状态管理** | Pinia | Vue 状态管理 |
| **HTTP 客户端** | Axios | API 请求 |
| **后端** | FastAPI | Python 异步 Web 框架 |
| **ORM** | SQLAlchemy | 数据库 ORM |
| **数据库** | SQLite | 轻量级本地数据库 |
| **任务调度** | APScheduler | Python 定时任务库 |
| **浏览器** | browser-use + CDP | 浏览器自动化 |
| **实时通信** | WebSocket (FastAPI) | 实时状态推送 |
| **容器** | Docker (仅后端) | 后端服务容器化 |

### 2.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         Windows 主机                              │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Vue 前端  │  │  FastAPI    │  │   Chrome    │             │
│  │  端口 5173  │  │  端口 8000  │  │  CDP :9222  │             │
│  │             │  │  (可选Docker)│  │             │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                 │                    │
│         │   HTTP/WebSocket│                 │                    │
│         └────────────────┼─────────────────┘                    │
│                          │                                      │
│                   ┌──────┴──────┐                               │
│                   │ browser-use │                               │
│                   │  任务执行   │                               │
│                   └──────┬──────┘                               │
│                          │                                      │
│                   ┌──────┴──────┐                               │
│                   │   SQLite    │                               │
│                   │   数据库    │                               │
│                   └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 项目目录结构

```
browser-use/
├── browser_use/           # 原 browser-use 核心代码
├── backend/               # 新增：后端服务
│   ├── main.py           # FastAPI 入口
│   ├── database.py       # 数据库配置
│   ├── config.py         # 配置管理
│   ├── api/              # API 路由
│   │   ├── __init__.py
│   │   ├── tasks.py      # 任务管理 API
│   │   ├── prompts.py    # Prompt 管理 API
│   │   ├── llm.py        # LLM 配置 API
│   │   ├── data.py       # 数据查询 API
│   │   ├── executions.py # 执行记录 API
│   │   └── browser.py    # 浏览器配置 API
│   ├── models/           # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── prompt.py
│   │   ├── llm_config.py
│   │   ├── execution.py
│   │   └── browser_config.py
│   ├── schemas/          # Pydantic 数据模型
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── prompt.py
│   │   ├── llm_config.py
│   │   ├── execution.py
│   │   └── browser_config.py
│   ├── services/         # 业务逻辑
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── llm_factory.py
│   │   ├── browser_service.py
│   │   ├── agent_service.py
│   │   └── scheduler_service.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       ├── security.py   # 加密解密
│       └── logger.py     # 日志配置
├── frontend/             # 新增：Vue 前端
│   ├── src/
│   │   ├── main.ts       # 入口文件
│   │   ├── App.vue       # 根组件
│   │   ├── components/   # Vue 组件
│   │   │   ├── layout/
│   │   │   │   ├── Header.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   └── MainLayout.vue
│   │   │   ├── tasks/
│   │   │   │   ├── TaskList.vue
│   │   │   │   ├── TaskCard.vue
│   │   │   │   ├── TaskForm.vue
│   │   │   │   └── TaskDetail.vue
│   │   │   ├── prompts/
│   │   │   │   ├── PromptList.vue
│   │   │   │   └── PromptEditor.vue
│   │   │   ├── llm/
│   │   │   │   ├── LLMConfigList.vue
│   │   │   │   └── LLMConfigForm.vue
│   │   │   ├── data/
│   │   │   │   ├── DataView.vue
│   │   │   │   └── DataDetail.vue
│   │   │   ├── executions/
│   │   │   │   ├── ExecutionList.vue
│   │   │   │   └── ExecutionDetail.vue
│   │   │   └── common/
│   │   │       ├── SchedulePicker.vue
│   │   │       └── LogViewer.vue
│   │   ├── views/        # 页面视图
│   │   │   ├── Tasks.vue
│   │   │   ├── Prompts.vue
│   │   │   ├── LLMConfigs.vue
│   │   │   ├── DataView.vue
│   │   │   ├── Executions.vue
│   │   │   └── Settings.vue
│   │   ├── api/          # API 调用封装
│   │   │   ├── index.ts
│   │   │   ├── tasks.ts
│   │   │   ├── prompts.ts
│   │   │   ├── llm.ts
│   │   │   ├── data.ts
│   │   │   └── executions.ts
│   │   ├── stores/       # Pinia 状态管理
│   │   │   ├── index.ts
│   │   │   ├── tasks.ts
│   │   │   ├── prompts.ts
│   │   │   ├── llm.ts
│   │   │   └── executions.ts
│   │   ├── router/       # 路由配置
│   │   │   └── index.ts
│   │   ├── styles/       # 样式文件
│   │   │   ├── main.css
│   │   │   └── variables.css
│   │   └── types/        # TypeScript 类型定义
│   │       └── index.ts
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── data/                 # 数据目录
│   ├── database.db       # SQLite 数据库
│   └── exports/          # 导出的 MD 文档
├── logs/                 # 日志目录
├── docker/
│   ├── Dockerfile        # 后端 Docker 配置
│   └── docker-compose.yml
├── .env.example          # 环境变量模板
├── .gitignore
├── CLAUDE.md
└── README.md
```

---

## 三、数据库设计

### 3.1 数据表

#### tasks（任务表）

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,           -- 任务名称
    description TEXT,                      -- 任务描述
    target_url VARCHAR(500),               -- 目标网站
    prompt_id INTEGER,                     -- 关联 Prompt
    llm_config_id INTEGER,                 -- 关联 LLM 配置
    schedule_type VARCHAR(20),             -- once/daily/weekly/custom
    schedule_config JSON,                  -- 调度配置
    browser_mode VARCHAR(20),              -- connect/profile
    profile_name VARCHAR(100),             -- Chrome Profile 名称
    is_enabled BOOLEAN DEFAULT 1,          -- 是否启用
    depends_on INTEGER,                    -- 依赖的任务 ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id),
    FOREIGN KEY (llm_config_id) REFERENCES llm_configs(id),
    FOREIGN KEY (depends_on) REFERENCES tasks(id)
);
```

#### prompts（Prompt 表）

```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,            -- Prompt 名称
    description TEXT,                      -- 描述
    content TEXT NOT NULL,                 -- Prompt 内容
    category VARCHAR(50),                  -- 分类
    variables JSON,                        -- 可用变量列表
    version INTEGER DEFAULT 1,             -- 版本号
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### llm_configs（LLM 配置表）

```sql
CREATE TABLE llm_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,            -- 配置名称
    provider VARCHAR(50) NOT NULL,         -- deepseek/openai/anthropic/ollama/openai_compatible
    api_key TEXT,                          -- API Key（加密存储）
    base_url VARCHAR(500),                 -- API Base URL
    model VARCHAR(100),                    -- 模型名称
    temperature FLOAT DEFAULT 0.7,         -- 温度参数
    max_tokens INTEGER DEFAULT 4096,       -- 最大 Token
    is_default BOOLEAN DEFAULT 0,          -- 是否默认
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### task_executions（任务执行记录表）

```sql
CREATE TABLE task_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,              -- 关联任务
    status VARCHAR(20),                    -- pending/running/success/failed
    started_at DATETIME,
    completed_at DATETIME,
    error_message TEXT,                    -- 错误信息
    log_content TEXT,                      -- 执行日志
    screenshot_path VARCHAR(500),          -- 截图路径
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

#### execution_data（采集数据表）

```sql
CREATE TABLE execution_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id INTEGER NOT NULL,         -- 关联执行记录
    data_type VARCHAR(50),                 -- 数据类型
    content TEXT,                          -- 数据内容（JSON/Markdown）
    source_url VARCHAR(500),               -- 来源 URL
    metadata JSON,                         -- 额外元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (execution_id) REFERENCES task_executions(id)
);
```

#### browser_configs（浏览器配置表）

```sql
CREATE TABLE browser_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,            -- 配置名称
    mode VARCHAR(20) NOT NULL,             -- connect/profile/standalone
    profile_path VARCHAR(500),             -- Profile 路径
    headless BOOLEAN DEFAULT 1,            -- 是否无头模式
    proxy_url VARCHAR(500),                -- 代理 URL
    cdp_port INTEGER,                      -- CDP 端口
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 ER 关系图

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    tasks     │     │   prompts    │     │ llm_configs  │
│──────────────│     │──────────────│     │──────────────│
│ id           │───  │ id           │     │ id           │
│ name         │     │ name         │     │ name         │
│ prompt_id    │───  │ content      │     │ provider     │
│ llm_config_id│     │              │     │              │
│ is_enabled   │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
        │
        │ depends_on
        ↓
┌──────────────┐
│    tasks     │
│ (self refer) │
└──────────────┘
        │
        ↓
┌──────────────┐
│task_executions│
└──────────────┘
        │
        ↓
┌──────────────┐
│execution_data│
└──────────────┘
```

---

## 四、API 设计

### 4.1 RESTful API

#### 任务管理 API

```
GET    /api/tasks                    # 获取任务列表
POST   /api/tasks                    # 创建任务
GET    /api/tasks/{id}               # 获取任务详情
PUT    /api/tasks/{id}               # 更新任务
DELETE /api/tasks/{id}               # 删除任务
POST   /api/tasks/{id}/run           # 立即执行任务
POST   /api/tasks/{id}/toggle        # 启用/停用任务
GET    /api/tasks/{id}/executions    # 获取任务执行历史
```

#### Prompt 管理 API

```
GET    /api/prompts                  # 获取 Prompt 列表
POST   /api/prompts                  # 创建 Prompt
GET    /api/prompts/{id}             # 获取 Prompt 详情
PUT    /api/prompts/{id}             # 更新 Prompt
DELETE /api/prompts/{id}             # 删除 Prompt
GET    /api/prompts/{id}/versions    # 获取版本历史
```

#### LLM 配置 API

```
GET    /api/llm-configs              # 获取配置列表
POST   /api/llm-configs              # 创建配置
GET    /api/llm-configs/{id}         # 获取配置详情
PUT    /api/llm-configs/{id}         # 更新配置
DELETE /api/llm-configs/{id}         # 删除配置
POST   /api/llm-configs/{id}/set-default  # 设为默认
POST   /api/llm-configs/{id}/test    # 测试连接
```

#### 数据与执行 API

```
GET    /api/executions               # 获取执行历史
GET    /api/executions/{id}          # 获取执行详情
GET    /api/executions/{id}/log      # 获取执行日志
GET    /api/data                     # 获取采集数据
GET    /api/data/{id}                # 获取数据详情
GET    /api/data/{id}/export         # 导出为 MD
DELETE /api/data/{id}                # 删除数据
```

#### 浏览器配置 API

```
GET    /api/browser/profiles         # 获取可用 Profile
GET    /api/browser/status           # 获取浏览器状态
POST   /api/browser/test-connection  # 测试连接
```

### 4.2 响应格式

#### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

#### 错误响应

```json
{
  "code": 1001,
  "message": "Task not found",
  "data": null
}
```

### 4.3 WebSocket API

```
WS /api/ws/task/{task_id}

消息类型：
- task.started      # 任务开始
- task.progress     # 进度更新
- task.completed    # 任务完成
- task.failed       # 任务失败
- log.line          # 日志行
```

---

## 五、功能模块设计

### 5.1 任务管理模块

**功能**：
- 创建/编辑/删除定时任务
- 配置任务基本信息（名称、描述、目标 URL）
- 选择 Prompt 模板
- 设置执行时间（友好时间选择：每天、每周、自定义）
- 配置浏览器模式（连接 Chrome / 复用 Profile）
- 启用/停用任务
- 手动立即执行
- 任务依赖配置

**友好时间选择器**：
- 每天执行 → 选择时间
- 每周执行 → 选择星期 + 时间
- 每月执行 → 选择日期 + 时间
- 间隔执行 → 每隔 N 小时/天
- 自定义 Cron 表达式

### 5.2 Prompt 管理模块

**功能**：
- 创建/编辑/删除 Prompt 模板
- Prompt 变量占位符（如 `{url}`, `{date}`, `{keywords}`）
- 分类管理（按用途分类）
- 支持 Prompt 版本历史

**变量系统**：
- `{url}` - 任务目标 URL
- `{date}` - 当前日期
- `{datetime}` - 当前日期时间
- `{keywords}` - 用户自定义关键词
- `{task_name}` - 任务名称

### 5.3 LLM 配置模块

**支持的 Provider**：

| Provider | 说明 | 配置项 |
|----------|------|--------|
| `deepseek` | DeepSeek API | api_key, base_url, model |
| `openai` | OpenAI API | api_key, base_url(可选), model |
| `anthropic` | Claude API | api_key, base_url(可选), model |
| `ollama` | Ollama 本地模型 | base_url, model |
| `openai_compatible` | 其他兼容 OpenAI API 的服务 | base_url, model, api_key(可选) |

**预设配置**（系统初始化时创建）：
- DeepSeek V4 Flash
- Ollama 本地
- 本地 OpenAI 兼容

### 5.4 浏览器管理模块

**两种浏览器模式**：

1. **连接现有 Chrome**：
   - 用户 Chrome 需以 `--remote-debugging-port=9222` 启动
   - browser-use 通过 CDP 连接
   - 复用所有登录状态

2. **复用 Chrome Profile**：
   - browser-use 启动独立 Chrome 实例
   - 加载用户 Chrome 的用户数据
   - 不需要特殊启动方式

**Profile 检测**：
```python
# Windows: C:\Users\{用户}\AppData\Local\Google\Chrome\User Data\{Profile}
# macOS: ~/Library/Application Support/Google/Chrome/{Profile}
# Linux: ~/.config/google-chrome/{Profile}
```

### 5.5 任务执行模块

**执行流程**：
1. 调度器触发任务
2. 加载任务配置（Prompt、LLM、浏览器）
3. 初始化浏览器连接
4. 创建 Agent 并执行
5. 采集数据并存储
6. 推送执行结果

**错误处理**：

| 错误类型 | 处理方式 |
|----------|----------|
| 网络错误 | 自动重试 3 次，间隔 5 秒 |
| LLM API 错误 | 记录日志，标记失败 |
| 浏览器崩溃 | 重启浏览器，重试 1 次 |
| 超时 | 保存中间状态，标记超时 |
| 数据解析失败 | 保存原始内容，记录错误 |

### 5.6 数据查看模块

**功能**：
- 按任务浏览数据
- 按日期浏览数据
- 查看数据详情
- 导出为 Markdown 文档
- 删除数据

**MD 导出格式**：
```markdown
# 采集结果 - {任务名称}

**采集时间**: 2026-05-04 09:00:00
**来源**: {URL}

## 采集内容

{数据内容}

## 元数据

- 任务ID: {task_id}
- 执行ID: {execution_id}
- 采集时间: {timestamp}
```

---

## 六、前端界面设计

### 6.1 界面风格

- 简洁实用风格（类似 Notion）
- 清晰的导航结构
- 卡片式任务展示
- 暗色/亮色主题切换（可选）

### 6.2 主要页面

#### 主布局

```
┌─────────────────────────────────────────────────────────┐
│  Logo   搜索框                    用户图标    设置      │
├──────┬──────────────────────────────────────────────────┤
│      │                                                  │
│ 侧边 │  内容区域                                         │
│ 导航 │  (动态加载各页面)                                 │
│      │                                                  │
│ ● 任务│                                                  │
│ ● Prompt│                                                │
│ ● LLM │                                                  │
│ ● 数据│                                                  │
│ ● 历史│                                                  │
│ ● 设置│                                                  │
└──────┴──────────────────────────────────────────────────┘
```

#### 任务管理页面

```
┌─────────────────────────────────────────────────────────┐
│  ← 任务管理                             [+ 新建任务]    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐    │
│  │任务1│ │任务2│ │任务3│ │任务4│ │任务5│ │+新建│    │
│  │每天9│ │每周1│ │手动 │ │暂停 │ │运行中│ │     │    │
│  │ ✓   │ │ ✓   │ │ ○   │ │ ❌  │ │ ⟳   │ │     │    │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘    │
│                                                         │
│  最近执行                                               │
│  • 任务1 - 2分钟前 - 成功 ✓                             │
│  • 任务2 - 1小时前 - 失败 ✗ (查看详情)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 新建任务表单

```
┌─────────────────────────────────────────────────────────┐
│  ← 新建任务                              保存  取消      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  基本信息                                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 任务名称: [___________________________]          │   │
│  │ 描    述: [___________________________]          │   │
│  │ 目标URL:  [https://___________________]          │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  执行配置                                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Prompt模板: [选择Prompt ▼]                       │   │
│  │ LLM配置:  [默认配置 ▼]                           │   │
│  │ 浏览器模式: ○ 连接Chrome  ● 复用Profile          │   │
│  │ Profile:  [Default ▼]                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  调度设置                                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 执行频率: [每天 ▼]                               │   │
│  │          时间: [09:00]                           │   │
│  │ 依赖任务: [无 ▼]                                 │   │
│  │ 启用任务: [✓]                                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 数据查看页面

```
┌─────────────────────────────────────────────────────────┐
│  ← 数据查看                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  筛选: [任务 ▼] [日期 ▼]    [导出全部]                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 📄 2026-05-04 - 采集任务1                        │   │
│  │    来源: https://example.com                     │   │
│  │    时间: 09:00:00                                │   │
│  │    [查看] [导出] [删除]                           │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ 📄 2026-05-03 - 采集任务1                        │   │
│  │    来源: https://example.com                     │   │
│  │    时间: 09:00:00                                │   │
│  │    [查看] [导出] [删除]                           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 七、Docker 部署

### 7.1 部署策略

采用**方案 1**：后端 Docker 化，Chrome 和 browser-use 在主机运行。

### 7.2 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/logs /app/exports

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.3 docker-compose.yml

```yaml
services:
  backend:
    build: .
    container_name: browser-use-backend
    ports:
      - "8000:8000"
    volumes:
      # 数据持久化
      - ./data:/app/data
      - ./logs:/app/logs
      - ./exports:/app/exports
    environment:
      - DATABASE_URL=sqlite:///data/database.db
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - CHROME_PROFILE_PATH=${CHROME_PROFILE_PATH}
    restart: unless-stopped
    networks:
      - browser-use-net

networks:
  browser-use-net:
    driver: bridge
```

### 7.4 路径兼容处理

```python
# backend/services/browser_service.py

import platform
from pathlib import Path

def get_chrome_profile_path(profile_name: str = "Default") -> Path:
    """跨平台获取 Chrome Profile 路径"""
    system = platform.system()

    if system == "Windows":
        base = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    elif system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:  # Linux
        base = Path.home() / ".config" / "google-chrome"

    return base / profile_name
```

---

## 八、安全设计

### 8.1 API Key 加密存储

使用 Fernet 对称加密：

```python
from cryptography.fernet import Fernet

# 加密密钥存环境变量
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
fernet = Fernet(ENCRYPTION_KEY)

# 存储
encrypted = fernet.encrypt(api_key.encode())

# 读取
api_key = fernet.decrypt(encrypted).decode()
```

### 8.2 CORS 配置

```python
# 只允许本地访问
CORSMiddleware(
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 8.3 .gitignore

```
# 敏感配置
.env
.env.local
*.key

# 数据库
data/*.db
data/*.db-journal

# 日志
logs/*.log

# 导出文件
data/exports/*
!data/exports/.gitkeep

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
frontend/dist/

# IDE
.vscode/
.idea/
*.swp
```

---

## 九、环境变量

### 9.1 .env.example

```bash
# 加密密钥（生成后不要修改）
ENCRYPTION_KEY=your-encryption-key-here

# 数据库
DATABASE_URL=sqlite:///data/database.db

# 后端配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 前端配置（开发模式）
VITE_API_BASE_URL=http://localhost:8000

# Chrome 配置
CHROME_PROFILE_PATH=
CHROME_CDP_PORT=9242

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs

# 调度器配置
SCHEDULER_MAX_WORKERS=3
```

---

## 十、实施计划

### 10.1 开发阶段

1. **阶段一：项目初始化**
   - 创建项目结构
   - 配置开发环境
   - 初始化数据库

2. **阶段二：后端开发**
   - API 路由开发
   - 数据库模型实现
   - 业务逻辑实现
   - 任务调度器集成

3. **阶段三：前端开发**
   - 页面组件开发
   - API 集成
   - 状态管理

4. **阶段四：集成测试**
   - 端到端测试
   - 性能优化

5. **阶段五：部署准备**
   - Docker 配置
   - 文档完善

### 10.2 技术依赖

**后端依赖**（requirements.txt）：
```
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
pydantic==2.9.2
pydantic-settings==2.6.0
apscheduler==3.10.4
websockets==13.1
python-multipart==0.0.12
cryptography==44.0.0
aiofiles==24.1.0
browser-use  # 来自本地
```

**前端依赖**（package.json）：
```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.6.0",
    "vite": "^5.4.0",
    "vue-tsc": "^2.1.0"
  }
}
```

---

## 十一、待确认事项

1. ~~部署环境~~ ✅ 已确认：仅本地
2. ~~界面风格~~ ✅ 已确认：简洁实用
3. ~~定时任务调度方式~~ ✅ 已确认：友好时间选择
4. ~~数据存储方式~~ ✅ 已确认：纯数据库 + MD 导出
5. ~~浏览器模式~~ ✅ 已确认：两者都支持
6. ~~Docker 方案~~ ✅ 已确认：后端容器化
7. ~~LLM 配置~~ ✅ 已确认：支持 DeepSeek 和本地模型

---

## 十二、版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-05-04 | 初始设计文档 |
