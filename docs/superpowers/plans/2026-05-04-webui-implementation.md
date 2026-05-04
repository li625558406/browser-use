# Browser-Use WebUI 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-step. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个带 Web 界面的定时任务数据采集系统，支持复用真实浏览器、配置多种 LLM、定时执行任务并生成 MD 文档。

**架构:** 前后端分离架构 - Vue 3 前端 + FastAPI 后端 + SQLite 数据库。后端容器化部署，browser-use 在主机运行。通过 WebSocket 实现实时状态推送。

**Tech Stack:**
- 后端: FastAPI + SQLAlchemy + APScheduler + browser-use
- 前端: Vue 3 + Vite + Element Plus + Pinia
- 数据库: SQLite
- 容器: Docker（后端）

---

## 阶段一：项目初始化

### Task 1.1: 创建项目目录结构

**Files:**
- Create: `backend/__init__.py`
- Create: `backend/api/__init__.py`
- Create: `backend/models/__init__.py`
- Create: `backend/schemas/__init__.py`
- Create: `backend/services/__init__.py`
- Create: `backend/utils/__init__.py`
- Create: `frontend/src/`
- Create: `data/`
- Create: `logs/`
- Create: `docs/superpowers/plans/`

- [ ] **Step 1: 创建后端目录结构**

```bash
cd D:/AI/ai-scout/browser-use

# 创建后端目录
mkdir -p backend/api backend/models backend/schemas backend/services backend/utils

# 创建 __init__.py 文件
touch backend/__init__.py
touch backend/api/__init__.py
touch backend/models/__init__.py
touch backend/schemas/__init__.py
touch backend/services/__init__.py
touch backend/utils/__init__.py
```

- [ ] **Step 2: 创建前端目录结构**

```bash
# 创建前端目录
mkdir -p frontend/src/{components/{layout,tasks,prompts,llm,data,executions,common},views,api,stores,router,styles,types}
mkdir -p frontend/public
mkdir -p data/exports
mkdir -p logs
mkdir -p docs/superpowers/plans
```

- [ ] **Step 3: 创建占位文件**

```bash
# 创建空文件确保目录被 Git 跟踪
touch data/exports/.gitkeep
touch logs/.gitkeep
```

- [ ] **Step 4: 提交**

```bash
git add backend frontend data logs docs
git commit -m "chore: create project directory structure"
```

---

### Task 1.2: 配置后端依赖

**Files:**
- Create: `requirements.txt`
- Create: `backend/requirements.txt`
- Modify: `.gitignore`

- [ ] **Step 1: 创建根目录 requirements.txt**

```txt
# D:/AI/ai-scout/browser-use/requirements.txt

# Web Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
websockets==13.1

# Database
sqlalchemy==2.0.36
aiosqlite==0.20.0

# Validation
pydantic==2.9.2
pydantic-settings==2.6.0
python-multipart==0.0.12

# Scheduler
apscheduler==3.10.4

# Security
cryptography==44.0.0

# Utilities
aiofiles==24.1.0
python-dotenv==1.0.1
```

- [ ] **Step 2: 创建后端 requirements.txt**

```txt
# D:/AI/ai-scout/browser-use/backend/requirements.txt

-r ../requirements.txt
```

- [ ] **Step 3: 更新 .gitignore**

```gitignore
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

- [ ] **Step 4: 提交**

```bash
git add requirements.txt backend/requirements.txt .gitignore
git commit -m "chore: add backend dependencies"
```

---

### Task 1.3: 配置前端项目

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/index.html`
- Create: `frontend/env.d.ts`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/styles/main.css`
- Create: `frontend/src/styles/variables.css`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "browser-use-webui",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "pinia": "^2.2.8",
    "element-plus": "^2.9.1",
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "typescript": "^5.7.3",
    "vue-tsc": "^2.2.0",
    "vite": "^6.0.7",
    "@types/node": "^22.10.5"
  }
}
```

- [ ] **Step 2: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
```

- [ ] **Step 3: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: 创建 tsconfig.node.json**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Browser-Use WebUI</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 6: 创建 env.d.ts**

```typescript
/// <reference types="vite/client" />

declare const __API_BASE_URL__: string
declare const __WS_BASE_URL__: string

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_WS_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

- [ ] **Step 7: 创建 main.ts**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/main.css'
import './styles/variables.css'

const app = createApp(App)
const pinia = createPinia()

// Register all icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

- [ ] **Step 8: 创建 App.vue**

```vue
<template>
  <router-view />
</template>

<script setup lang="ts">
// Main app component
</script>
```

- [ ] **Step 9: 创建 main.css**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
}
```

- [ ] **Step 10: 创建 variables.css**

```css
:root {
  --color-primary: #409eff;
  --color-success: #67c23a;
  --color-warning: #e6a23c;
  --color-danger: #f56c6c;
  --color-info: #909399;

  --bg-color: #f5f7fa;
  --bg-color-page: #ffffff;
  --text-color-primary: #303133;
  --text-color-regular: #606266;
  --text-color-secondary: #909399;
  --text-color-placeholder: #c0c4cc;

  --border-color: #dcdfe6;
  --border-color-light: #e4e7ed;
  --border-color-lighter: #ebeef5;

  --shadow-light: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --shadow-base: 0 2px 4px rgba(0, 0, 0, 0.12);
}
```

- [ ] **Step 11: 提交**

```bash
git add frontend/
git commit -m "chore: initialize Vue 3 frontend project"
```

---

### Task 1.4: 配置环境变量

**Files:**
- Create: `.env.example`
- Create: `backend/config.py`

- [ ] **Step 1: 创建 .env.example**

```bash
# D:/AI/ai-scout/browser-use/.env.example

# 加密密钥（生成后不要修改）
ENCRYPTION_KEY=generate-with-python-cryptography

# 数据库
DATABASE_URL=sqlite:///data/database.db

# 后端配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000

# Chrome 配置
CHROME_PROFILE_PATH=
CHROME_CDP_PORT=9242

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs

# 调度器配置
SCHEDULER_MAX_WORKERS=3
```

- [ ] **Step 2: 创建 backend/config.py**

```python
# D:/AI/ai-scout/browser-use/backend/config.py

import os
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_encryption_key() -> str:
    """获取或生成加密密钥"""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        print(f"Generated new encryption key: {key}")
        print("Please add this to your .env file as ENCRYPTION_KEY")
    return key


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 加密
    encryption_key: str = Field(default_factory=get_encryption_key)

    # 数据库
    database_url: str = "sqlite:///data/database.db"

    # 后端
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # Chrome
    chrome_profile_path: str = ""
    chrome_cdp_port: int = 9242

    # 日志
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_dir: str = "logs"

    # 调度器
    scheduler_max_workers: int = 3

    @property
    def data_dir(self) -> Path:
        return Path("data")

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def logs_dir(self) -> Path:
        return Path(self.log_dir)


settings = Settings()
```

- [ ] **Step 3: 创建 .env 文件**

```bash
# 生成加密密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 复制输出到 .env
cat > .env << EOF
ENCRYPTION_KEY=<生成的密钥>
DATABASE_URL=sqlite:///data/database.db
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
CHROME_CDP_PORT=9242
LOG_LEVEL=INFO
LOG_DIR=logs
SCHEDULER_MAX_WORKERS=3
EOF
```

- [ ] **Step 4: 提交**

```bash
git add .env.example backend/config.py
git commit -m "chore: add configuration management"
```

---

### Task 1.5: 配置数据库连接

**Files:**
- Create: `backend/database.py`
- Create: `backend/utils/logger.py`

- [ ] **Step 1: 创建 database.py**

```python
# D:/AI/ai-scout/browser-use/backend/database.py

import asyncio
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import settings


class Base(DeclarativeBase):
    """ORM 基类"""
    pass


# 创建异步引擎
# SQLite 需要使用 aiosqlite
database_url = settings.database_url.replace("sqlite://", "sqlite+aiosqlite://")

engine = create_async_engine(
    database_url,
    echo=settings.log_level == "DEBUG",
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """初始化数据库"""
    # 确保数据目录存在
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    # 导入所有模型以确保它们被注册
    from backend.models import task, prompt, llm_config, execution, browser_config

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话（依赖注入）"""
    async with async_session_maker() as session:
        yield session
```

- [ ] **Step 2: 创建 utils/logger.py**

```python
# D:/AI/ai-scout/browser-use/backend/utils/logger.py

import logging
import sys
from pathlib import Path

from backend.config import settings


def setup_logger(name: str = "browser-use-webui") -> logging.Logger:
    """配置日志"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))

    # 清除现有处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))

    # 格式化
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    log_dir = Path(settings.logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_dir / "webui.log", encoding="utf-8")
    file_handler.setLevel(getattr(logging, settings.log_level))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 全局日志实例
logger = setup_logger()
```

- [ ] **Step 3: 提交**

```bash
git add backend/database.py backend/utils/logger.py
git commit -m "feat: add database connection and logger"
```

---

## 阶段二：数据库模型

### Task 2.1: 创建任务模型

**Files:**
- Create: `backend/models/task.py`
- Create: `backend/schemas/task.py`

- [ ] **Step 1: 创建 models/task.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/task.py

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Task(Base):
    """任务模型"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 外键关联
    prompt_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("prompts.id"), nullable=True)
    llm_config_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("llm_configs.id"), nullable=True)

    # 调度配置
    schedule_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=False)  # once/daily/weekly/custom
    schedule_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # 浏览器配置
    browser_mode: Mapped[Optional[str]] = mapped_column(String(20), nullable=False)  # connect/profile
    profile_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # 状态
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # 任务依赖
    depends_on: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    prompt = relationship("Prompt", back_populates="tasks", foreign_keys=[prompt_id])
    llm_config = relationship("LLMConfig", back_populates="tasks")
    executions = relationship("TaskExecution", back_populates="task", cascade="all, delete-orphan")

    # 自引用（任务依赖）
    depends_on_task = relationship("Task", remote_side=[id], foreign_keys=[depends_on])
    dependent_tasks = relationship("Task", remote_side=[depends_on], foreign_keys=[id])

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name='{self.name}', enabled={self.is_enabled})>"
```

- [ ] **Step 2: 创建 schemas/task.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/task.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleConfig(BaseModel):
    """调度配置"""
    type: str = Field(..., description="once/daily/weekly/custom")
    time: Optional[str] = Field(None, description="HH:MM 格式的时间")
    day_of_week: Optional[int] = Field(None, description="0-6, 0=周一")
    interval: Optional[int] = Field(None, description="间隔（分钟/小时/天）")
    cron: Optional[str] = Field(None, description="Cron 表达式")


class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_url: Optional[str] = None
    prompt_id: Optional[int] = None
    llm_config_id: Optional[int] = None
    schedule: ScheduleConfig
    browser_mode: str = Field("profile", pattern="^(connect|profile)$")
    profile_name: Optional[str] = "Default"
    depends_on: Optional[int] = None


class TaskUpdate(BaseModel):
    """更新任务请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    target_url: Optional[str] = None
    prompt_id: Optional[int] = None
    llm_config_id: Optional[int] = None
    schedule: Optional[ScheduleConfig] = None
    browser_mode: Optional[str] = Field(None, pattern="^(connect|profile)$")
    profile_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    depends_on: Optional[int] = None


class TaskResponse(BaseModel):
    """任务响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    target_url: Optional[str]
    prompt_id: Optional[int]
    llm_config_id: Optional[int]
    schedule_type: str
    schedule_config: Optional[dict]
    browser_mode: str
    profile_name: Optional[str]
    is_enabled: bool
    depends_on: Optional[int]
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/task.py backend/schemas/task.py
git commit -m "feat: add task model and schema"
```

---

### Task 2.2: 创建 Prompt 模型

**Files:**
- Create: `backend/models/prompt.py`
- Create: `backend/schemas/prompt.py`

- [ ] **Step 1: 创建 models/prompt.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/prompt.py

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Prompt(Base):
    """Prompt 模板模型"""

    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    variables: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    version: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tasks = relationship("Task", back_populates="prompt", foreign_keys="Task.prompt_id")

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, name='{self.name}', category='{self.category}')>"
```

- [ ] **Step 2: 创建 schemas/prompt.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/prompt.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PromptCreate(BaseModel):
    """创建 Prompt 请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    variables: Optional[list[str]] = Field(default_factory=list)


class PromptUpdate(BaseModel):
    """更新 Prompt 请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    variables: Optional[list[str]] = None


class PromptResponse(BaseModel):
    """Prompt 响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    content: str
    category: Optional[str]
    variables: Optional[list]
    version: int
    created_at: datetime
    updated_at: datetime
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/prompt.py backend/schemas/prompt.py
git commit -m "feat: add prompt model and schema"
```

---

### Task 2.3: 创建 LLM 配置模型

**Files:**
- Create: `backend/models/llm_config.py`
- Create: `backend/schemas/llm_config.py`

- [ ] **Step 1: 创建 models/llm_config.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/llm_config.py

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class LLMConfig(Base):
    """LLM 配置模型"""

    __tablename__ = "llm_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # deepseek/openai/anthropic/ollama/openai_compatible
    api_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    tasks = relationship("Task", back_populates="llm_config")

    def __repr__(self) -> str:
        return f"<LLMConfig(id={self.id}, name='{self.name}', provider='{self.provider}', model='{self.model}')>"
```

- [ ] **Step 2: 创建 schemas/llm_config.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/llm_config.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LLMConfigCreate(BaseModel):
    """创建 LLM 配置请求"""
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., pattern="^(deepseek|openai|anthropic|ollama|openai_compatible)$")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = Field(..., min_length=1, max_length=100)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(4096, ge=1, le=128000)
    is_default: bool = False


class LLMConfigUpdate(BaseModel):
    """更新 LLM 配置请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, pattern="^(deepseek|openai|anthropic|ollama|openai_compatible)$")
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_default: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    """LLM 配置响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider: str
    api_key: Optional[str]  # 返回时只显示前几位
    base_url: Optional[str]
    model: str
    temperature: float
    max_tokens: int
    is_default: bool
    created_at: datetime
    updated_at: datetime


class LLMConfigTestRequest(BaseModel):
    """测试 LLM 配置请求"""
    provider: str
    api_key: Optional[str]
    base_url: Optional[str]
    model: str
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/llm_config.py backend/schemas/llm_config.py
git commit -m "feat: add llm config model and schema"
```

---

### Task 2.4: 创建执行记录模型

**Files:**
- Create: `backend/models/execution.py`
- Create: `backend/schemas/execution.py`

- [ ] **Step 1: 创建 models/execution.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/execution.py

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class TaskExecution(Base):
    """任务执行记录模型"""

    __tablename__ = "task_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")  # pending/running/success/failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    log_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 关系
    task = relationship("Task", back_populates="executions")
    data_records = relationship("ExecutionData", back_populates="execution", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TaskExecution(id={self.id}, task_id={self.task_id}, status='{self.status}')>"


class ExecutionData(Base):
    """采集数据模型"""

    __tablename__ = "execution_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[int] = mapped_column(Integer, ForeignKey("task_executions.id"), nullable=False)
    data_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # 关系
    execution = relationship("TaskExecution", back_populates="data_records")

    def __repr__(self) -> str:
        return f"<ExecutionData(id={self.id}, execution_id={self.execution_id}, type='{self.data_type}')>"
```

- [ ] **Step 2: 创建 schemas/execution.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/execution.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TaskExecutionResponse(BaseModel):
    """任务执行响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    screenshot_path: Optional[str]


class ExecutionDataResponse(BaseModel):
    """采集数据响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    execution_id: int
    data_type: Optional[str]
    content: Optional[str]
    source_url: Optional[str]
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/execution.py backend/schemas/execution.py
git commit -m "feat: add execution models and schemas"
```

---

### Task 2.5: 创建浏览器配置模型

**Files:**
- Create: `backend/models/browser_config.py`
- Create: `backend/schemas/browser_config.py`

- [ ] **Step 1: 创建 models/browser_config.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/browser_config.py

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class BrowserConfig(Base):
    """浏览器配置模型"""

    __tablename__ = "browser_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)  # connect/profile/standalone
    profile_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    headless: Mapped[bool] = mapped_column(Boolean, default=True)
    proxy_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cdp_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BrowserConfig(id={self.id}, name='{self.name}', mode='{self.mode}')>"
```

- [ ] **Step 2: 创建 schemas/browser_config.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/browser_config.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BrowserConfigCreate(BaseModel):
    """创建浏览器配置请求"""
    name: str = Field(..., min_length=1, max_length=100)
    mode: str = Field(..., pattern="^(connect|profile|standalone)$")
    profile_path: Optional[str] = None
    headless: bool = True
    proxy_url: Optional[str] = None
    cdp_port: Optional[int] = Field(None, ge=1, le=65535)


class BrowserConfigResponse(BaseModel):
    """浏览器配置响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    mode: str
    profile_path: Optional[str]
    headless: bool
    proxy_url: Optional[str]
    cdp_port: Optional[int]
    created_at: datetime


class ChromeProfileInfo(BaseModel):
    """Chrome Profile 信息"""
    name: str
    path: str
    avatar: Optional[str] = None


class BrowserStatusResponse(BaseModel):
    """浏览器状态响应"""
    is_connected: bool
    cdp_url: Optional[str] = None
    profiles: list[ChromeProfileInfo]
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/browser_config.py backend/schemas/browser_config.py
git commit -m "feat: add browser config model and schema"
```

---

### Task 2.6: 更新模型 __init__.py

**Files:**
- Modify: `backend/models/__init__.py`
- Modify: `backend/schemas/__init__.py`

- [ ] **Step 1: 更新 models/__init__.py**

```python
# D:/AI/ai-scout/browser-use/backend/models/__init__.py

from backend.models.browser_config import BrowserConfig
from backend.models.execution import ExecutionData, TaskExecution
from backend.models.llm_config import LLMConfig
from backend.models.prompt import Prompt
from backend.models.task import Task

__all__ = [
    "Task",
    "Prompt",
    "LLMConfig",
    "TaskExecution",
    "ExecutionData",
    "BrowserConfig",
]
```

- [ ] **Step 2: 更新 schemas/__init__.py**

```python
# D:/AI/ai-scout/browser-use/backend/schemas/__init__.py

from backend.schemas.browser_config import (
    BrowserConfigCreate,
    BrowserConfigResponse,
    BrowserStatusResponse,
    ChromeProfileInfo,
)
from backend.schemas.execution import ExecutionDataResponse, TaskExecutionResponse
from backend.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigResponse,
    LLMConfigTestRequest,
    LLMConfigUpdate,
)
from backend.schemas.prompt import PromptCreate, PromptResponse, PromptUpdate
from backend.schemas.task import ScheduleConfig, TaskCreate, TaskResponse, TaskUpdate

__all__ = [
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "ScheduleConfig",
    "PromptCreate",
    "PromptUpdate",
    "PromptResponse",
    "LLMConfigCreate",
    "LLMConfigUpdate",
    "LLMConfigResponse",
    "LLMConfigTestRequest",
    "TaskExecutionResponse",
    "ExecutionDataResponse",
    "BrowserConfigCreate",
    "BrowserConfigResponse",
    "BrowserStatusResponse",
    "ChromeProfileInfo",
]
```

- [ ] **Step 3: 提交**

```bash
git add backend/models/__init__.py backend/schemas/__init__.py
git commit -m "chore: update model and schema imports"
```

---

## 阶段三：后端 API 路由

### Task 3.1: 创建 API 基础设施

**Files:**
- Create: `backend/dependencies.py`
- Create: `backend/api/__init__.py`

- [ ] **Step 1: 创建 dependencies.py**

```python
# D:/AI/ai-scout/browser-use/backend/dependencies.py

from typing import AsyncGenerator

from backend.database import async_session_maker, get_session as _get_session


async def get_session() -> AsyncGenerator:
    """获取数据库会话（FastAPI 依赖）"""
    async for session in _get_session():
        yield session


async def get_db():
    """获取数据库（别名）"""
    async for session in _get_session():
        yield session
```

- [ ] **Step 2: 更新 api/__init__.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/__init__.py

from fastapi import APIRouter

api_router = APIRouter()

# 导入子路由（稍后添加）
# from backend.api import tasks, prompts, llm, data, executions, browser
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
# api_router.include_router(llm.router, prefix="/llm-configs", tags=["llm"])
# api_router.include_router(data.router, prefix="/data", tags=["data"])
# api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
# api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
```

- [ ] **Step 3: 提交**

```bash
git add backend/dependencies.py backend/api/__init__.py
git commit -m "chore: add API infrastructure"
```

---

### Task 3.2: 创建统一响应格式

**Files:**
- Create: `backend/api/response.py`

- [ ] **Step 1: 创建 response.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/response.py

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应格式"""

    code: int = 0
    message: str = "success"
    data: T | None = None

    @classmethod
    def success(cls, data: T | None = None, message: str = "success") -> "ApiResponse[T]":
        return cls(code=0, message=message, data=data)

    @classmethod
    def error(cls, code: int, message: str, data: T | None = None) -> "ApiResponse[T]":
        return cls(code=code, message=message, data=data)


# 常用错误码
class ErrorCode:
    SUCCESS = 0
    INVALID_PARAMS = 1001
    NOT_FOUND = 1002
    ALREADY_EXISTS = 1003
    INTERNAL_ERROR = 5000
```

- [ ] **Step 2: 提交**

```bash
git add backend/api/response.py
git commit -m "feat: add unified API response format"
```

---

### Task 3.3: 创建任务管理 API

**Files:**
- Create: `backend/api/tasks.py`

- [ ] **Step 1: 创建 tasks.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/tasks.py

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse, ErrorCode
from backend.dependencies import get_session
from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate, ScheduleConfig

router = APIRouter()


@router.get("", response_model=ApiResponse[List[TaskResponse]])
async def list_tasks(
    is_enabled: bool | None = None,
    session: AsyncSession = Depends(get_session),
):
    """获取任务列表"""
    query = select(Task)

    if is_enabled is not None:
        query = query.where(Task.is_enabled == is_enabled)

    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    return ApiResponse.success(data=[TaskResponse.model_validate(t) for t in tasks])


@router.post("", response_model=ApiResponse[TaskResponse])
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建任务"""
    # 检查依赖任务是否存在
    if task_data.depends_on is not None:
        dep_task = await session.get(Task, task_data.depends_on)
        if dep_task is None:
            raise HTTPException(status_code=400, detail="Dependent task not found")

    # 转换 schedule
    schedule_config = task_data.schedule.model_dump()

    task = Task(
        name=task_data.name,
        description=task_data.description,
        target_url=task_data.target_url,
        prompt_id=task_data.prompt_id,
        llm_config_id=task_data.llm_config_id,
        schedule_type=task_data.schedule.type,
        schedule_config=schedule_config,
        browser_mode=task_data.browser_mode,
        profile_name=task_data.profile_name,
        depends_on=task_data.depends_on,
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.get("/{task_id}", response_model=ApiResponse[TaskResponse])
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取任务详情"""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.put("/{task_id}", response_model=ApiResponse[TaskResponse])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新任务"""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 更新字段
    update_data = task_data.model_dump(exclude_unset=True)

    # 处理 schedule
    if "schedule" in update_data and update_data["schedule"] is not None:
        schedule = update_data.pop("schedule")
        task.schedule_type = schedule.type
        task.schedule_config = schedule.model_dump()

    for field, value in update_data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)

    return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.delete("/{task_id}", response_model=ApiResponse[None])
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除任务"""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()

    return ApiResponse.success(message="Task deleted")


@router.post("/{task_id}/toggle", response_model=ApiResponse[TaskResponse])
async def toggle_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """启用/停用任务"""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_enabled = not task.is_enabled
    await session.commit()
    await session.refresh(task)

    return ApiResponse.success(data=TaskResponse.model_validate(task))


@router.post("/{task_id}/run", response_model=ApiResponse[dict])
async def run_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
):
    """立即执行任务"""
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # TODO: 触发任务执行
    # 这里需要调用调度服务

    return ApiResponse.success(data={"message": "Task execution started", "execution_id": None})
```

- [ ] **Step 2: 注册路由**

```python
# D:/AI/ai-scout/browser-use/backend/api/__init__.py

from fastapi import APIRouter
from backend.api import tasks  # 新增

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
```

- [ ] **Step 3: 提交**

```bash
git add backend/api/tasks.py backend/api/__init__.py
git commit -m "feat: add tasks API endpoints"
```

---

### Task 3.4: 创建 Prompt 管理 API

**Files:**
- Create: `backend/api/prompts.py`

- [ ] **Step 1: 创建 prompts.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/prompts.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse
from backend.dependencies import get_session
from backend.models.prompt import Prompt
from backend.schemas.prompt import PromptCreate, PromptResponse, PromptUpdate

router = APIRouter()


@router.get("", response_model=ApiResponse[List[PromptResponse]])
async def list_prompts(
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """获取 Prompt 列表"""
    query = select(Prompt)

    if category:
        query = query.where(Prompt.category == category)

    query = query.order_by(Prompt.created_at.desc())

    result = await session.execute(query)
    prompts = result.scalars().all()

    return ApiResponse.success(data=[PromptResponse.model_validate(p) for p in prompts])


@router.post("", response_model=ApiResponse[PromptResponse])
async def create_prompt(
    prompt_data: PromptCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建 Prompt"""
    prompt = Prompt(**prompt_data.model_dump())

    session.add(prompt)
    await session.commit()
    await session.refresh(prompt)

    return ApiResponse.success(data=PromptResponse.model_validate(prompt))


@router.get("/{prompt_id}", response_model=ApiResponse[PromptResponse])
async def get_prompt(
    prompt_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取 Prompt 详情"""
    prompt = await session.get(Prompt, prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return ApiResponse.success(data=PromptResponse.model_validate(prompt))


@router.put("/{prompt_id}", response_model=ApiResponse[PromptResponse])
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新 Prompt"""
    prompt = await session.get(Prompt, prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    update_data = prompt_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    # 更新版本号
    if "content" in update_data:
        prompt.version += 1

    await session.commit()
    await session.refresh(prompt)

    return ApiResponse.success(data=PromptResponse.model_validate(prompt))


@router.delete("/{prompt_id}", response_model=ApiResponse[None])
async def delete_prompt(
    prompt_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除 Prompt"""
    prompt = await session.get(Prompt, prompt_id)
    if prompt is None:
        raise HTTPException(status_code=404, detail="Prompt not found")

    await session.delete(prompt)
    await session.commit()

    return ApiResponse.success(message="Prompt deleted")
```

- [ ] **Step 2: 注册路由**

```python
# 更新 backend/api/__init__.py

from backend.api import prompts  # 新增
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
```

- [ ] **Step 3: 提交**

```bash
git add backend/api/prompts.py backend/api/__init__.py
git commit -m "feat: add prompts API endpoints"
```

---

### Task 3.5: 创建 LLM 配置 API

**Files:**
- Create: `backend/api/llm.py`

- [ ] **Step 1: 创建 llm.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/llm.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.response import ApiResponse
from backend.dependencies import get_session
from backend.models.llm_config import LLMConfig
from backend.schemas.llm_config import (
    LLMConfigCreate,
    LLMConfigResponse,
    LLMConfigTestRequest,
    LLMConfigUpdate,
)

router = APIRouter()


@router.get("", response_model=ApiResponse[List[LLMConfigResponse]])
async def list_llm_configs(
    session: AsyncSession = Depends(get_session),
):
    """获取 LLM 配置列表"""
    result = await session.execute(select(LLMConfig).order_by(LLMConfig.created_at.desc()))
    configs = result.scalars().all()

    # 隐藏 API Key 的大部分内容
    response_data = []
    for config in configs:
        config_dict = LLMConfigResponse.model_validate(config).model_dump()
        if config_dict.get("api_key"):
            api_key = config_dict["api_key"]
            config_dict["api_key"] = api_key[:8] + "..." if len(api_key) > 8 else "***"
        response_data.append(LLMConfigResponse(**config_dict))

    return ApiResponse.success(data=response_data)


@router.post("", response_model=ApiResponse[LLMConfigResponse])
async def create_llm_config(
    config_data: LLMConfigCreate,
    session: AsyncSession = Depends(get_session),
):
    """创建 LLM 配置"""
    # 如果设为默认，取消其他默认配置
    if config_data.is_default:
        await session.execute(select(LLMConfig).where(LLMConfig.is_default == True))
        existing_defaults = (await session.execute(select(LLMConfig).where(LLMConfig.is_default == True))).scalars().all()
        for config in existing_defaults:
            config.is_default = False

    config = LLMConfig(**config_data.model_dump())
    session.add(config)
    await session.commit()
    await session.refresh(config)

    return ApiResponse.success(data=LLMConfigResponse.model_validate(config))


@router.get("/{config_id}", response_model=ApiResponse[LLMConfigResponse])
async def get_llm_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """获取 LLM 配置详情"""
    config = await session.get(LLMConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="LLM config not found")

    return ApiResponse.success(data=LLMConfigResponse.model_validate(config))


@router.put("/{config_id}", response_model=ApiResponse[LLMConfigResponse])
async def update_llm_config(
    config_id: int,
    config_data: LLMConfigUpdate,
    session: AsyncSession = Depends(get_session),
):
    """更新 LLM 配置"""
    config = await session.get(LLMConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="LLM config not found")

    update_data = config_data.model_dump(exclude_unset=True)

    # 如果设为默认，取消其他默认配置
    if update_data.get("is_default"):
        result = await session.execute(select(LLMConfig).where(LLMConfig.is_default == True))
        existing_defaults = result.scalars().all()
        for c in existing_defaults:
            c.is_default = False

    for field, value in update_data.items():
        setattr(config, field, value)

    await session.commit()
    await session.refresh(config)

    return ApiResponse.success(data=LLMConfigResponse.model_validate(config))


@router.delete("/{config_id}", response_model=ApiResponse[None])
async def delete_llm_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """删除 LLM 配置"""
    config = await session.get(LLMConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="LLM config not found")

    await session.delete(config)
    await session.commit()

    return ApiResponse.success(message="LLM config deleted")


@router.post("/{config_id}/set-default", response_model=ApiResponse[LLMConfigResponse])
async def set_default_llm_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """设为默认配置"""
    config = await session.get(LLMConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # 取消所有默认配置
    result = await session.execute(select(LLMConfig))
    all_configs = result.scalars().all()
    for c in all_configs:
        c.is_default = False

    # 设置当前为默认
    config.is_default = True
    await session.commit()
    await session.refresh(config)

    return ApiResponse.success(data=LLMConfigResponse.model_validate(config))


@router.post("/{config_id}/test", response_model=ApiResponse[dict])
async def test_llm_config(
    config_id: int,
    session: AsyncSession = Depends(get_session),
):
    """测试 LLM 配置"""
    config = await session.get(LLMConfig, config_id)
    if config is None:
        raise HTTPException(status_code=404, detail="LLM config not found")

    # TODO: 实际测试连接
    # 这里需要调用 LLM 服务

    return ApiResponse.success(data={"status": "success", "message": "Connection successful"})
```

- [ ] **Step 2: 注册路由**

```python
# 更新 backend/api/__init__.py

from backend.api import llm  # 新增
api_router.include_router(llm.router, prefix="/llm-configs", tags=["llm"])
```

- [ ] **Step 3: 提交**

```bash
git add backend/api/llm.py backend/api/__init__.py
git commit -m "feat: add llm config API endpoints"
```

---

## 阶段四：后端业务服务

### Task 4.1: 创建 LLM 工厂服务

**Files:**
- Create: `backend/services/llm_factory.py`

- [ ] **Step 1: 创建 llm_factory.py**

```python
# D:/AI/ai-scout/browser-use/backend/services/llm_factory.py

from browser_use.llm import ChatAnthropic, ChatOllama, ChatOpenAI

from backend.models.llm_config import LLMConfig


def create_llm(config: LLMConfig):
    """根据配置创建 LLM 实例"""
    provider = config.provider

    if provider == "deepseek":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "",
            base_url=config.base_url or "https://api.deepseek.com",
        )

    elif provider == "openai":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "",
            base_url=config.base_url or "https://api.openai.com/v1",
        )

    elif provider == "anthropic":
        return ChatAnthropic(
            model=config.model,
            api_key=config.api_key or "",
            base_url=config.base_url,
        )

    elif provider == "ollama":
        return ChatOllama(
            model=config.model,
            base_url=config.base_url or "http://localhost:11434",
        )

    elif provider == "openai_compatible":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "dummy",
            base_url=config.base_url,
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

- [ ] **Step 2: 提交**

```bash
git add backend/services/llm_factory.py
git commit -m "feat: add LLM factory service"
```

---

### Task 4.2: 创建浏览器服务

**Files:**
- Create: `backend/services/browser_service.py`
- Create: `backend/utils/chrome.py`

- [ ] **Step 1: 创建 utils/chrome.py**

```python
# D:/AI/ai-scout/browser-use/backend/utils/chrome.py

import platform
from pathlib import Path
from typing import List


def get_chrome_user_data_path() -> Path:
    """获取 Chrome 用户数据目录"""
    system = platform.system()

    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
    else:  # Linux
        return Path.home() / ".config" / "google-chrome"


def get_available_profiles() -> List[dict]:
    """获取可用的 Chrome Profile 列表"""
    user_data_path = get_chrome_user_data_path()

    if not user_data_path.exists():
        return []

    profiles = []

    # 添加 Default Profile
    default_path = user_data_path / "Default"
    if default_path.exists():
        profiles.append({
            "name": "Default",
            "path": str(default_path),
        })

    # 查找其他 Profile (Profile 1, Profile 2, ...)
    for i in range(1, 100):
        profile_name = f"Profile {i}"
        profile_path = user_data_path / profile_name
        if profile_path.exists():
            profiles.append({
                "name": profile_name,
                "path": str(profile_path),
            })
        else:
            break

    return profiles
```

- [ ] **Step 2: 创建 browser_service.py**

```python
# D:/AI/ai-scout/browser-use/backend/services/browser_service.py

from browser_use import Browser
from browser_use.browser.profile import BrowserProfile

from backend.models.browser_config import BrowserConfig
from backend.utils.chrome import get_available_profiles
from backend.utils.logger import logger


class BrowserService:
    """浏览器服务"""

    @staticmethod
    def get_profiles() -> List[dict]:
        """获取可用的 Chrome Profile 列表"""
        return get_available_profiles()

    @staticmethod
    async def create_browser(config: BrowserConfig) -> Browser:
        """根据配置创建浏览器实例"""
        profile = BrowserProfile()

        # 配置 Profile
        if config.mode == "profile" and config.profile_path:
            profile.user_data_dir = config.profile_path

        # 配置 CDP
        if config.mode == "connect" and config.cdp_port:
            # 连接现有 Chrome
            pass  # browser-use 支持通过 CDP URL 连接

        # Headless 模式
        if config.headless:
            # browser-use 默认使用 headless
            pass

        # 代理
        if config.proxy_url:
            profile.proxy = config.proxy_url

        browser = Browser(
            browser_profile=profile,
        )

        return browser

    @staticmethod
    async def test_connection(cdp_port: int = 9242) -> bool:
        """测试 Chrome CDP 连接"""
        try:
            import httpx

            response = await httpx.AsyncClient().get(f"http://localhost:{cdp_port}/json/version")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to connect to Chrome CDP: {e}")
            return False
```

- [ ] **Step 3: 提交**

```bash
git add backend/services/browser_service.py backend/utils/chrome.py
git commit -m "feat: add browser service"
```

---

## 阶段五：后端主应用

### Task 5.1: 创建 FastAPI 主应用

**Files:**
- Create: `backend/main.py`

- [ ] **Step 1: 创建 main.py**

```python
# D:/AI/ai-scout/browser-use/backend/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api_router
from backend.config import settings
from backend.database import init_db
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Starting Browser-Use WebUI...")
    await init_db()
    logger.info("Database initialized")

    yield

    # 关闭时
    logger.info("Shutting down Browser-Use WebUI...")


# 创建应用
app = FastAPI(
    title="Browser-Use WebUI",
    description="定时任务数据采集系统",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "Browser-Use WebUI",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
```

- [ ] **Step 2: 提交**

```bash
git add backend/main.py
git commit -m "feat: create FastAPI main application"
```

---

### Task 5.2: 创建浏览器配置 API

**Files:**
- Create: `backend/api/browser.py`

- [ ] **Step 1: 创建 browser.py**

```python
# D:/AI/ai-scout/browser-use/backend/api/browser.py

from fastapi import APIRouter, Depends, HTTPException

from backend.api.response import ApiResponse
from backend.schemas.browser_config import (
    BrowserConfigResponse,
    BrowserStatusResponse,
    ChromeProfileInfo,
)
from backend.services.browser_service import BrowserService
from backend.utils.chrome import get_available_profiles
from backend.utils.logger import logger

router = APIRouter()


@router.get("/profiles", response_model=ApiResponse[list[ChromeProfileInfo]])
async def list_profiles():
    """获取可用的 Chrome Profile 列表"""
    profiles = get_available_profiles()

    response_data = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    return ApiResponse.success(data=response_data)


@router.get("/status", response_model=ApiResponse[BrowserStatusResponse])
async def get_browser_status():
    """获取浏览器状态"""
    profiles = get_available_profiles()

    profile_infos = [
        ChromeProfileInfo(
            name=p["name"],
            path=p["path"],
        )
        for p in profiles
    ]

    # 测试 CDP 连接
    is_connected = await BrowserService.test_connection()

    return ApiResponse.success(
        data=BrowserStatusResponse(
            is_connected=is_connected,
            cdp_url=f"http://localhost:9242" if is_connected else None,
            profiles=profile_infos,
        )
    )


@router.post("/test-connection", response_model=ApiResponse[dict])
async def test_connection(cdp_port: int = 9242):
    """测试 CDP 连接"""
    result = await BrowserService.test_connection(cdp_port)

    return ApiResponse.success(
        data={
            "success": result,
            "message": "Connection successful" if result else "Connection failed",
        }
    )
```

- [ ] **Step 2: 注册路由**

```python
# 更新 backend/api/__init__.py

from backend.api import browser  # 新增
api_router.include_router(browser.router, prefix="/browser", tags=["browser"])
```

- [ ] **Step 3: 提交**

```bash
git add backend/api/browser.py backend/api/__init__.py
git commit -m "feat: add browser configuration API"
```

---

## 阶段六：前端基础

### Task 6.1: 创建前端路由

**Files:**
- Create: `frontend/src/router/index.ts`

- [ ] **Step 1: 创建 router/index.ts**

```typescript
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    redirect: '/tasks',
  },
  {
    path: '/tasks',
    name: 'tasks',
    component: () => import('@/views/Tasks.vue'),
    meta: { title: '任务管理' }
  },
  {
    path: '/prompts',
    name: 'prompts',
    component: () => import('@/views/Prompts.vue'),
    meta: { title: 'Prompt 管理' }
  },
  {
    path: '/llm',
    name: 'llm',
    component: () => import('@/views/LLMConfigs.vue'),
    meta: { title: 'LLM 配置' }
  },
  {
    path: '/data',
    name: 'data',
    component: () => import('@/views/DataView.vue'),
    meta: { title: '数据查看' }
  },
  {
    path: '/executions',
    name: 'executions',
    component: () => import('@/views/Executions.vue'),
    meta: { title: '执行记录' }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - Browser-Use WebUI`
  }
  next()
})

export default router
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: add frontend router"
```

---

### Task 6.2: 创建前端 API 客户端

**Files:**
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/api/types.ts`
- Create: `frontend/src/api/tasks.ts`

- [ ] **Step 1: 创建 api/index.ts**

```typescript
import axios, type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error)
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<any, AxiosResponse<{ code: number; message: string; data: T }>>(url, config)
    return response.data.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<any, AxiosResponse<{ code: number; message: string; data: T }>>(url, data, config)
    return response.data.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<any, AxiosResponse<{ code: number; message: string; data: T }>>(url, data, config)
    return response.data.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<any, AxiosResponse<{ code: number; message: string; data: T }>>(url, config)
    return response.data.data
  }
}

export const api = new ApiClient()
```

- [ ] **Step 2: 创建 api/types.ts**

```typescript
export interface Task {
  id: number
  name: string
  description: string | null
  target_url: string | null
  prompt_id: number | null
  llm_config_id: number | null
  schedule_type: string
  schedule_config: any
  browser_mode: string
  profile_name: string | null
  is_enabled: boolean
  depends_on: number | null
  created_at: string
  updated_at: string
}

export interface Prompt {
  id: number
  name: string
  description: string | null
  content: string
  category: string | null
  variables: string[] | null
  version: number
  created_at: string
  updated_at: string
}

export interface LLMConfig {
  id: number
  name: string
  provider: string
  api_key: string | null
  base_url: string | null
  model: string
  temperature: number
  max_tokens: number
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface TaskExecution {
  id: number
  task_id: number
  status: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  screenshot_path: string | null
}
```

- [ ] **Step 3: 创建 api/tasks.ts**

```typescript
import { api } from './index'
import type { Task } from './types'

export interface TaskCreate {
  name: string
  description?: string
  target_url?: string
  prompt_id?: number
  llm_config_id?: number
  schedule: {
    type: string
    time?: string
    day_of_week?: number
    interval?: number
    cron?: string
  }
  browser_mode: 'connect' | 'profile'
  profile_name?: string
  depends_on?: number
}

export const tasksApi = {
  list: (isEnabled?: boolean) =>
    api.get<Task[]>('/tasks', { params: { is_enabled: isEnabled } }),

  get: (id: number) =>
    api.get<Task>(`/tasks/${id}`),

  create: (data: TaskCreate) =>
    api.post<Task>('/tasks', data),

  update: (id: number, data: Partial<TaskCreate>) =>
    api.put<Task>(`/tasks/${id}`, data),

  delete: (id: number) =>
    api.delete<void>(`/tasks/${id}`),

  toggle: (id: number) =>
    api.post<Task>(`/tasks/${id}/toggle`),

  run: (id: number) =>
    api.post<{ message: string; execution_id: number | null }>(`/tasks/${id}/run`)
}
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/api/index.ts frontend/src/api/types.ts frontend/src/api/tasks.ts
git commit -m "feat: add frontend API client"
```

---

### Task 6.3: 创建 Pinia Store

**Files:**
- Create: `frontend/src/stores/tasks.ts`

- [ ] **Step 1: 创建 stores/tasks.ts**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi, type TaskCreate } from '@/api/tasks'
import type { Task } from '@/api/types'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const enabledTasks = computed(() => tasks.value.filter(t => t.is_enabled))
  const disabledTasks = computed(() => tasks.value.filter(t => !t.is_enabled))

  // Actions
  async function fetchTasks(isEnabled?: boolean) {
    loading.value = true
    error.value = null
    try {
      tasks.value = await tasksApi.list(isEnabled)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch tasks'
      console.error('Fetch tasks error:', e)
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: TaskCreate) {
    loading.value = true
    error.value = null
    try {
      const newTask = await tasksApi.create(data)
      tasks.value.unshift(newTask)
      return newTask
    } catch (e: any) {
      error.value = e.message || 'Failed to create task'
      console.error('Create task error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTask(id: number, data: Partial<TaskCreate>) {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await tasksApi.update(id, data)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (e: any) {
      error.value = e.message || 'Failed to update task'
      console.error('Update task error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(id: number) {
    loading.value = true
    error.value = null
    try {
      await tasksApi.delete(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete task'
      console.error('Delete task error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function toggleTask(id: number) {
    loading.value = true
    error.value = null
    try {
      const updatedTask = await tasksApi.toggle(id)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updatedTask
      }
      return updatedTask
    } catch (e: any) {
      error.value = e.message || 'Failed to toggle task'
      console.error('Toggle task error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  async function runTask(id: number) {
    loading.value = true
    error.value = null
    try {
      const result = await tasksApi.run(id)
      return result
    } catch (e: any) {
      error.value = e.message || 'Failed to run task'
      console.error('Run task error:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    tasks,
    loading,
    error,
    enabledTasks,
    disabledTasks,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    runTask
  }
})
```

- [ ] **Step 2: 更新 stores/index.ts**

```typescript
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

export * from './tasks'
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/stores/tasks.ts frontend/src/stores/index.ts
git commit -m "feat: add tasks store"
```

---

### Task 6.4: 创建主布局组件

**Files:**
- Create: `frontend/src/components/layout/AppHeader.vue`
- Create: `frontend/src/components/layout/AppSidebar.vue`
- Create: `frontend/src/components/layout/AppLayout.vue`

- [ ] **Step 1: 创建 AppHeader.vue**

```vue
<template>
  <header class="app-header">
    <div class="header-left">
      <h1 class="app-title">Browser-Use WebUI</h1>
    </div>
    <div class="header-right">
      <el-button :icon="Setting" circle @click="$router.push('/settings')" />
    </div>
  </header>
</template>

<script setup lang="ts">
import { Setting } from '@element-plus/icons-vue'
</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: var(--bg-color-page);
  border-bottom: 1px solid var(--border-color);
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
}

.header-right {
  display: flex;
  gap: 12px;
}
</style>
```

- [ ] **Step 2: 创建 AppSidebar.vue**

```vue
<template>
  <aside class="app-sidebar">
    <nav class="sidebar-nav">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        active-class="nav-item-active"
      >
        <component :is="item.icon" class="nav-icon" />
        <span class="nav-label">{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  List,
  Document,
  ChatLineSquare,
  FolderOpened,
  Clock,
  Setting
} from '@element-plus/icons-vue'

interface MenuItem {
  path: string
  label: string
  icon: any
}

const menuItems = ref<MenuItem[]>([
  { path: '/tasks', label: '任务管理', icon: List },
  { path: '/prompts', label: 'Prompt', icon: Document },
  { path: '/llm', label: 'LLM 配置', icon: ChatLineSquare },
  { path: '/data', label: '数据查看', icon: FolderOpened },
  { path: '/executions', label: '执行记录', icon: Clock },
  { path: '/settings', label: '设置', icon: Setting }
])
</script>

<style scoped>
.app-sidebar {
  width: 200px;
  height: 100%;
  background-color: var(--bg-color-page);
  border-right: 1px solid var(--border-color);
  padding: 20px 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: var(--text-color-regular);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background-color: var(--bg-color);
}

.nav-item-active {
  background-color: var(--color-primary);
  color: white;
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.nav-label {
  font-size: 14px;
}
</style>
```

- [ ] **Step 3: 创建 AppLayout.vue**

```vue
<template>
  <div class="app-layout">
    <AppHeader />
    <div class="layout-body">
      <AppSidebar />
      <main class="layout-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.layout-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg-color);
}
</style>
```

- [ ] **Step 4: 更新 App.vue**

```vue
<template>
  <AppLayout />
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
</script>
```

- [ ] **Step 5: 提交**

```bash
git add frontend/src/components/layout/ frontend/src/App.vue
git commit -m "feat: add layout components"
```

---

### Task 6.5: 创建任务管理页面

**Files:**
- Create: `frontend/src/views/Tasks.vue`

- [ ] **Step 1: 创建 Tasks.vue**

```vue
<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>任务管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建任务
      </el-button>
    </div>

    <div class="tasks-grid">
      <task-card
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @edit="handleEdit"
        @toggle="handleToggle"
        @run="handleRun"
        @delete="handleDelete"
      />
    </div>

    <el-empty v-if="!loading && tasks.length === 0" description="暂无任务" />

    <!-- 创建/编辑对话框 -->
    <task-form
      v-model="showCreateDialog"
      :task="editingTask"
      @saved="handleSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useTasksStore } from '@/stores'
import type { Task, TaskCreate } from '@/api/types'
import TaskCard from '@/components/tasks/TaskCard.vue'
import TaskForm from '@/components/tasks/TaskForm.vue'

const tasksStore = useTasksStore()
const tasks = ref<Task[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const editingTask = ref<Task | null>(null)

onMounted(async () => {
  await loadTasks()
})

async function loadTasks() {
  loading.value = true
  try {
    await tasksStore.fetchTasks()
    tasks.value = tasksStore.tasks
  } finally {
    loading.value = false
  }
}

function handleEdit(task: Task) {
  editingTask.value = task
  showCreateDialog.value = true
}

async function handleToggle(task: Task) {
  try {
    await tasksStore.toggleTask(task.id)
    await loadTasks()
    ElMessage.success(task.is_enabled ? '任务已停用' : '任务已启用')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleRun(task: Task) {
  try {
    await tasksStore.runTask(task.id)
    ElMessage.success('任务已开始执行')
  } catch (error) {
    ElMessage.error('执行失败')
  }
}

async function handleDelete(task: Task) {
  try {
    await ElMessageBox.confirm(`确定要删除任务 "${task.name}" 吗？`, '确认删除', {
      type: 'warning'
    })
    await tasksStore.deleteTask(task.id)
    await loadTasks()
    ElMessage.success('任务已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleSaved() {
  showCreateDialog.value = false
  editingTask.value = null
  await loadTasks()
  ElMessage.success(editingTask.value ? '任务已更新' : '任务已创建')
}
</script>

<style scoped>
.tasks-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color-primary);
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/views/Tasks.vue
git commit -m "feat: add tasks page"
```

---

### Task 6.6: 创建任务卡片组件

**Files:**
- Create: `frontend/src/components/tasks/TaskCard.vue`

- [ ] **Step 1: 创建 TaskCard.vue**

```vue
<template>
  <el-card class="task-card" :class="{ 'task-disabled': !task.is_enabled }">
    <template #header>
      <div class="card-header">
        <span class="task-name">{{ task.name }}</span>
        <el-tag :type="task.is_enabled ? 'success' : 'info'" size="small">
          {{ task.is_enabled ? '启用' : '停用' }}
        </el-tag>
      </div>
    </template>

    <div class="card-body">
      <p v-if="task.description" class="task-description">{{ task.description }}</p>

      <div class="task-info">
        <div class="info-item">
          <span class="info-label">调度:</span>
          <span class="info-value">{{ scheduleText }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">浏览器:</span>
          <span class="info-value">{{ browserModeText }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="card-footer">
        <el-button-group>
          <el-button size="small" @click="$emit('edit', task)">编辑</el-button>
          <el-button
            size="small"
            :type="task.is_enabled ? 'warning' : 'success'"
            @click="$emit('toggle', task)"
          >
            {{ task.is_enabled ? '停用' : '启用' }}
          </el-button>
          <el-button
            size="small"
            type="primary"
            :disabled="!task.is_enabled"
            @click="$emit('run', task)"
          >
            运行
          </el-button>
          <el-button size="small" type="danger" @click="$emit('delete', task)">删除</el-button>
        </el-button-group>
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Task } from '@/api/types'

const props = defineProps<{
  task: Task
}>()

defineEmits<{
  edit: [task: Task]
  toggle: [task: Task]
  run: [task: Task]
  delete: [task: Task]
}>()

const scheduleText = computed(() => {
  const config = props.task.schedule_config
  switch (props.task.schedule_type) {
    case 'daily':
      return `每天 ${config?.time || '未设置'}`
    case 'weekly':
      return `每周${['日', '一', '二', '三', '四', '五', '六'][config?.day_of_week || 0]} ${config?.time || ''}`
    case 'once':
      return '手动执行'
    default:
      return '自定义'
  }
})

const browserModeText = computed(() => {
  return props.task.browser_mode === 'connect' ? '连接 Chrome' : `Profile: ${props.task.profile_name || 'Default'}`
})
</script>

<style scoped>
.task-card {
  transition: all 0.2s;
}

.task-card:hover {
  box-shadow: var(--shadow-light);
}

.task-disabled {
  opacity: 0.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  font-weight: 600;
  color: var(--text-color-primary);
}

.card-body {
  min-height: 80px;
}

.task-description {
  color: var(--text-color-secondary);
  font-size: 14px;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item {
  display: flex;
  font-size: 13px;
}

.info-label {
  color: var(--text-color-secondary);
  width: 60px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-color-regular);
}

.card-footer {
  display: flex;
  justify-content: center;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
git add frontend/src/components/tasks/TaskCard.vue
git commit -m "feat: add task card component"
```

---

## 阶段七：Docker 配置

### Task 7.1: 创建 Dockerfile

**Files:**
- Create: `docker/Dockerfile`

- [ ] **Step 1: 创建 Dockerfile**

```dockerfile
# D:/AI/ai-scout/browser-use/docker/Dockerfile

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

- [ ] **Step 2: 提交**

```bash
git add docker/Dockerfile
git commit -m "chore: add Dockerfile"
```

---

### Task 7.2: 创建 docker-compose.yml

**Files:**
- Create: `docker/docker-compose.yml`

- [ ] **Step 1: 创建 docker-compose.yml**

```yaml
# D:/AI/ai-scout/browser-use/docker/docker-compose.yml

version: '3.8'

services:
  backend:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: browser-use-backend
    ports:
      - "8000:8000"
    volumes:
      # 数据持久化
      - ../data:/app/data
      - ../logs:/app/logs
      - ../exports:/app/exports
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

- [ ] **Step 2: 提交**

```bash
git add docker/docker-compose.yml
git commit -m "chore: add docker-compose configuration"
```

---

## 阶段八：初始化数据

### Task 8.1: 创建默认数据初始化脚本

**Files:**
- Create: `backend/scripts/init_default_data.py`

- [ ] **Step 1: 创建初始化脚本**

```python
# D:/AI/ai-scout/browser-use/backend/scripts/init_default_data.py

import asyncio
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from backend.database import async_session_maker
from backend.models import LLMConfig, Prompt
from backend.utils.logger import logger


async def init_default_prompts():
    """初始化默认 Prompt"""
    async with async_session_maker() as session:
        # 检查是否已存在
        result = await session.execute(select(Prompt))
        if result.scalars().first():
            logger.info("Prompts already exist, skipping initialization")
            return

        prompts = [
            Prompt(
                name="通用数据采集",
                description="用于采集网站内容的通用 Prompt",
                content="""请访问 {url} 并采集以下信息：

1. 页面标题
2. 主要内容
3. 相关链接

请以结构化的方式返回结果。""",
                category="data",
                variables=["url"],
            ),
            Prompt(
                name="新闻采集",
                description="专门用于采集新闻文章",
                content="""请访问 {url} 并采集新闻内容：

1. 新闻标题
2. 发布时间
3. 作者
4. 正文内容
5. 相关标签

请以 Markdown 格式返回。""",
                category="news",
                variables=["url"],
            ),
            Prompt(
                name="价格监控",
                description="用于监控商品价格",
                content="""请访问 {url} 并获取以下信息：

1. 商品名称
2. 当前价格
3. 原价（如有）
4. 库存状态
5. 商品图片 URL

请以 JSON 格式返回。""",
                category="ecommerce",
                variables=["url"],
            ),
        ]

        for prompt in prompts:
            session.add(prompt)

        await session.commit()
        logger.info(f"Created {len(prompts)} default prompts")


async def init_default_llm_configs():
    """初始化默认 LLM 配置"""
    async with async_session_maker() as session:
        # 检查是否已存在
        result = await session.execute(select(LLMConfig))
        if result.scalars().first():
            logger.info("LLM configs already exist, skipping initialization")
            return

        configs = [
            LLMConfig(
                name="DeepSeek V4 Flash",
                provider="deepseek",
                base_url="https://api.deepseek.com",
                model="deepseek-v4-flash",
                api_key="",  # 用户需要自己填入
                is_default=True,
            ),
            LLMConfig(
                name="Ollama 本地",
                provider="ollama",
                base_url="http://localhost:11434",
                model="llama3.2",
                is_default=False,
            ),
            LLMConfig(
                name="本地 OpenAI 兼容",
                provider="openai_compatible",
                base_url="http://localhost:1234/v1",
                model="deepseek-coder",
                is_default=False,
            ),
        ]

        for config in configs:
            session.add(config)

        await session.commit()
        logger.info(f"Created {len(configs)} default LLM configs")


async def main():
    """主函数"""
    logger.info("Initializing default data...")

    await init_default_prompts()
    await init_default_llm_configs()

    logger.info("Default data initialization completed")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: 提交**

```bash
git add backend/scripts/init_default_data.py
git commit -m "feat: add default data initialization script"
```

---

## 阶段九：文档和总结

### Task 9.1: 更新 README

**Files:**
- Create: `README.md` (更新或创建项目说明)

- [ ] **Step 1: 创建/更新 README**

```markdown
# Browser-Use WebUI

基于 browser-use 的定时任务数据采集系统，支持 Web 界面管理。

## 功能特性

- ✅ 定时任务管理（友好时间选择）
- ✅ 复用真实浏览器（已登录状态）
- ✅ 多 LLM 配置（DeepSeek、OpenAI、Claude、Ollama 等）
- ✅ Prompt 模板管理
- ✅ 数据采集与导出（Markdown）
- ✅ 执行历史查看

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Chrome/Chromium

### 安装

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..

# 复制环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要配置

# 生成加密密钥
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# 将输出添加到 .env 的 ENCRYPTION_KEY

# 初始化默认数据
python backend/scripts/init_default_data.py
```

### 启动开发环境

```bash
# 启动后端（终端 1）
uvicorn backend.main:app --reload

# 启动前端（终端 2）
cd frontend
npm run dev
```

访问 http://localhost:5173

### Docker 部署

```bash
cd docker
docker-compose up -d
```

## 项目结构

```
browser-use/
├── backend/               # FastAPI 后端
│   ├── api/              # API 路由
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 业务逻辑
│   └── utils/            # 工具函数
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── components/   # 组件
│       ├── views/        # 页面
│       ├── api/          # API 封装
│       └── stores/       # 状态管理
├── data/                 # 数据目录
├── logs/                 # 日志目录
└── docker/               # Docker 配置
```

## 配置说明

### LLM 配置

系统支持以下 LLM Provider：

- `deepseek` - DeepSeek API
- `openai` - OpenAI API
- `anthropic` - Claude API
- `ollama` - Ollama 本地模型
- `openai_compatible` - 其他兼容 OpenAI API 的服务

### 浏览器模式

1. **连接 Chrome**：需要 Chrome 以 `--remote-debugging-port=9222` 启动
2. **复用 Profile**：加载现有 Chrome 的用户数据

## 开发

### 后端开发

```bash
# 运行测试
pytest tests/

# 类型检查
pyright backend/

# 代码格式化
ruff check backend/ --fix
ruff format backend/
```

### 前端开发

```bash
cd frontend

# 开发
npm run dev

# 构建
npm run build

# 预览
npm run preview
```

## License

MIT
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add project README"
```

---

## 计划总结

本实施计划包含 **9 个阶段，共 38 个任务**，覆盖了：

1. ✅ 项目初始化（5 个任务）
2. ✅ 数据库模型（6 个任务）
3. ✅ 后端 API（5 个任务）
4. ✅ 业务服务（2 个任务）
5. ✅ 主应用（2 个任务）
6. ✅ 前端基础（6 个任务）
7. ✅ Docker 配置（2 个任务）
8. ✅ 初始化数据（1 个任务）
9. ✅ 文档（1 个任务）

**未完成的功能（待后续实现）**：
- 任务调度服务（APScheduler 集成）
- Agent 执行服务
- WebSocket 实时推送
- 其他 API（data、executions）
- 其他页面组件（Prompts、LLMConfigs、DataView、Executions、Settings）
- TaskForm 表单组件
- SchedulePicker 组件

这些功能可以在基础框架完成后逐步添加。
