# Browser-Use WebUI 文件结构

## 后端文件结构

```
backend/
├── main.py                           # FastAPI 应用入口
├── database.py                       # 数据库连接配置
├── config.py                         # 应用配置
├── dependencies.py                   # 依赖注入
├── __init__.py
│
├── api/                              # API 路由
│   ├── __init__.py
│   ├── tasks.py                      # 任务管理 API
│   ├── prompts.py                    # Prompt 管理 API
│   ├── llm.py                        # LLM 配置 API
│   ├── data.py                       # 数据查询 API
│   ├── executions.py                 # 执行记录 API
│   ├── browser.py                    # 浏览器配置 API
│   └── websocket.py                  # WebSocket 连接
│
├── models/                           # SQLAlchemy ORM 模型
│   ├── __init__.py
│   ├── task.py                       # 任务模型
│   ├── prompt.py                     # Prompt 模型
│   ├── llm_config.py                 # LLM 配置模型
│   ├── execution.py                  # 执行记录模型
│   └── browser_config.py             # 浏览器配置模型
│
├── schemas/                          # Pydantic 数据模型（请求/响应）
│   ├── __init__.py
│   ├── task.py                       # 任务 Schema
│   ├── prompt.py                     # Prompt Schema
│   ├── llm_config.py                 # LLM 配置 Schema
│   ├── execution.py                  # 执行记录 Schema
│   └── browser_config.py             # 浏览器配置 Schema
│
├── services/                         # 业务逻辑层
│   ├── __init__.py
│   ├── task_service.py               # 任务服务
│   ├── llm_factory.py                # LLM 工厂（创建不同 LLM 实例）
│   ├── browser_service.py            # 浏览器服务
│   ├── agent_service.py              # Agent 执行服务
│   ├── scheduler_service.py          # 任务调度服务
│   └── data_service.py               # 数据处理服务
│
└── utils/                            # 工具函数
    ├── __init__.py
    ├── security.py                   # 加密/解密
    ├── logger.py                     # 日志配置
    └── chrome.py                     # Chrome 路径检测
```

## 前端文件结构

```
frontend/
├── src/
│   ├── main.ts                       # 应用入口
│   ├── App.vue                       # 根组件
│   │
│   ├── components/                   # 可复用组件
│   │   ├── layout/
│   │   │   ├── AppHeader.vue         # 顶部导航栏
│   │   │   ├── AppSidebar.vue        # 侧边栏
│   │   │   └── AppLayout.vue         # 主布局组件
│   │   │
│   │   ├── tasks/
│   │   │   ├── TaskList.vue          # 任务列表
│   │   │   ├── TaskCard.vue          # 任务卡片
│   │   │   ├── TaskForm.vue          # 任务表单
│   │   │   └── TaskDetail.vue        # 任务详情
│   │   │
│   │   ├── prompts/
│   │   │   ├── PromptList.vue        # Prompt 列表
│   │   │   └── PromptEditor.vue      # Prompt 编辑器
│   │   │
│   │   ├── llm/
│   │   │   ├── LLMConfigList.vue     # LLM 配置列表
│   │   │   └── LLMConfigForm.vue     # LLM 配置表单
│   │   │
│   │   ├── data/
│   │   │   ├── DataView.vue          # 数据视图
│   │   │   └── DataDetail.vue        # 数据详情
│   │   │
│   │   ├── executions/
│   │   │   ├── ExecutionList.vue     # 执行记录列表
│   │   │   ├── ExecutionCard.vue     # 执行记录卡片
│   │   │   └── LogViewer.vue         # 日志查看器
│   │   │
│   │   └── common/
│   │       ├── SchedulePicker.vue    # 调度时间选择器
│   │       └── ConfirmDialog.vue     # 确认对话框
│   │
│   ├── views/                        # 页面视图
│   │   ├── Tasks.vue                 # 任务管理页面
│   │   ├── Prompts.vue               # Prompt 管理页面
│   │   ├── LLMConfigs.vue            # LLM 配置页面
│   │   ├── DataView.vue              # 数据查看页面
│   │   ├── Executions.vue            # 执行记录页面
│   │   └── Settings.vue              # 设置页面
│   │
│   ├── api/                          # API 调用封装
│   │   ├── index.ts                  # Axios 实例配置
│   │   ├── types.ts                  # API 类型定义
│   │   ├── tasks.ts                  # 任务 API
│   │   ├── prompts.ts                # Prompt API
│   │   ├── llm.ts                    # LLM API
│   │   ├── data.ts                   # 数据 API
│   │   └── executions.ts             # 执行记录 API
│   │
│   ├── stores/                       # Pinia 状态管理
│   │   ├── index.ts                  # Store 入口
│   │   ├── tasks.ts                  # 任务状态
│   │   ├── prompts.ts                # Prompt 状态
│   │   ├── llm.ts                    # LLM 状态
│   │   └── executions.ts             # 执行记录状态
│   │
│   ├── router/                       # 路由配置
│   │   └── index.ts                  # 路由定义
│   │
│   ├── styles/                       # 样式文件
│   │   ├── main.css                  # 主样式
│   │   └── variables.css             # CSS 变量
│   │
│   └── types/                        # TypeScript 类型
│       └── index.ts                  # 全局类型定义
│
├── public/
│   └── favicon.ico
│
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── env.d.ts
```

## 配置文件

```
browser-use/
├── .env                              # 环境变量（不提交）
├── .env.example                      # 环境变量模板
├── requirements.txt                  # Python 依赖
├── docker/
│   ├── Dockerfile                    # 后端 Docker 镜像
│   └── docker-compose.yml            # Docker Compose 配置
└── data/                             # 数据目录
    ├── database.db                   # SQLite 数据库
    └── exports/                      # 导出的 MD 文档
```
