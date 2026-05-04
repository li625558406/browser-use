# Browser-Use WebUI

A web-based UI for browser-use - AI-powered browser automation with scheduled task execution.

## Features

- 📅 **Scheduled Tasks**: Set up recurring browser automation tasks with friendly time selection
- 🤖 **Multi-LLM Support**: Configure DeepSeek, OpenAI, Claude, Ollama, or custom OpenAI-compatible models
- 📝 **Prompt Templates**: Manage reusable prompt templates with variable substitution
- 🌐 **Browser Integration**: Use your existing Chrome browser (with logged-in accounts) or Chrome profiles
- 📊 **Data Export**: Automatically generate Markdown documents from collected data
- 🐳 **Docker Support**: Easy containerized deployment

## Architecture

- **Backend**: FastAPI + SQLAlchemy + APScheduler
- **Frontend**: Vue 3 + Vite + Element Plus + Pinia
- **Database**: SQLite (easily upgradeable to PostgreSQL)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Chrome/Chromium browser (for browser automation)

### Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/browser-use/browser-use.git
   cd browser-use
   ```

2. **Install backend dependencies**:
   ```bash
   uv venv --python 3.11
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables**:
   ```bash
   # Generate encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

   # Create .env file
   cat > .env << EOF
   ENCRYPTION_KEY=<generated-key>
   DATABASE_URL=sqlite:///data/database.db
   BACKEND_HOST=0.0.0.0
   BACKEND_PORT=8000
   EOF
   ```

5. **Start the backend**:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```

6. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

7. **Open your browser**:
   - Frontend: http://localhost:5173
   - API docs: http://localhost:8000/docs

## Docker Deployment

### Quick Start

```bash
docker-compose up -d
```

The backend will be available at http://localhost:8000.

### Build your own image

```bash
docker build -t browser-use-webui .
docker run -p 8000:8000 -v $(pwd)/data:/app/data browser-use-webui
```

## Usage

### 1. Configure LLM

First, set up your LLM provider:

1. Go to "LLM 配置" (LLM Configurations)
2. Click "新建配置" (New Configuration)
3. Fill in:
   - Name: e.g., "DeepSeek Chat"
   - Provider: deepseek/openai/anthropic/ollama/openai_compatible
   - API Key: Your API key
   - Base URL: API endpoint (or use default)
   - Model: Model name
4. Click "测试连接" (Test Connection) to verify
5. Set as default if needed

### 2. Create Prompt Template

1. Go to "Prompt 管理" (Prompt Management)
2. Click "新建 Prompt" (New Prompt)
3. Fill in:
   - Name: e.g., "Product Scraper"
   - Description: What this prompt does
   - Content: Your prompt template with variables like `{{url}}`
   - Category: e.g., "ecommerce"
   - Variables: List variable names used
4. Save

### 3. Create Scheduled Task

1. Go to "任务管理" (Task Management)
2. Click "新建任务" (New Task)
3. Configure:
   - **Basic Info**: Name, description, target URL
   - **Prompt**: Select a template or enter custom prompt
   - **LLM**: Select your LLM configuration
   - **Schedule**: Choose when to run
     - Once: Run at specific date/time
     - Daily: Run every day at specified time
     - Weekly: Run on specific day of week
     - Custom: Use cron expression
   - **Browser**:
     - Connect: Connect to existing Chrome with CDP
     - Profile: Use specific Chrome profile
4. Save and enable the task

### 4. View Results

- Go to "执行记录" (Execution Records) to see task history
- Go to "数据查看" (Data View) to browse exported Markdown files

## Browser Modes

### Connect to Existing Chrome

1. Start Chrome with remote debugging:
   ```bash
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9242

   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9242

   # Linux
   google-chrome --remote-debugging-port=9242
   ```

2. In WebUI, select "Connect" mode with CDP port 9242

### Use Chrome Profile

1. Go to "设置" > "Browser" to see available profiles
2. Select the profile name in task configuration
3. The browser will use that profile's cookies, logins, and extensions

## Project Structure

```
browser-use/
├── backend/               # FastAPI backend
│   ├── api/              # API routes
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── frontend/             # Vue 3 frontend
│   └── src/
│       ├── api/          # API client
│       ├── components/   # Vue components
│       ├── stores/       # Pinia stores
│       ├── views/        # Page views
│       └── router/       # Vue Router config
├── data/                 # SQLite database + exports
├── logs/                 # Application logs
└── docker-compose.yml    # Docker deployment
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENCRYPTION_KEY` | Key for encrypting sensitive data | Auto-generated |
| `DATABASE_URL` | Database connection string | `sqlite:///data/database.db` |
| `BACKEND_HOST` | Backend bind address | `0.0.0.0` |
| `BACKEND_PORT` | Backend port | `8000` |
| `CHROME_CDP_PORT` | Chrome CDP port | `9242` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SCHEDULER_MAX_WORKERS` | Max concurrent task executions | `3` |

## Development

### Backend Development

```bash
# Run with auto-reload
uv run uvicorn backend.main:app --reload

# Run tests
uv run pytest tests/

# Type checking
uv run pyright
```

### Frontend Development

```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

## Troubleshooting

### Chrome won't connect

1. Make sure Chrome is running with `--remote-debugging-port=9242`
2. Check that port 9242 is not in use by another process
3. Try "Profile" mode instead of "Connect" mode

### Task execution fails

1. Check the execution record for error messages
2. Verify your LLM API key is valid
3. Check that the target URL is accessible
4. Review the logs in `logs/webui.log`

### Database errors

1. Ensure the `data/` directory exists
2. Check that you have write permissions
3. Try deleting `data/database.db` and restarting to reinitialize

## Contributing

Contributions are welcome! Please read the [browser-use contribution guide](CONTRIBUTING.md).

## License

This project is part of [browser-use](https://github.com/browser-use/browser-use) and follows the same license.

## Acknowledgments

- [browser-use](https://github.com/browser-use/browser-use) - Core browser automation library
- [FastAPI](https://fastapi.tiangolo.com/) - Backend web framework
- [Vue 3](https://vuejs.org/) - Frontend framework
- [Element Plus](https://element-plus.org/) - UI component library
