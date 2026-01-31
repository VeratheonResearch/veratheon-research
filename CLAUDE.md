# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Package Manager**: This repository uses `uv` (Astral's package manager). Do NOT use `pip` or `pipenv`.

**Run autonomous research for a stock**:
```bash
uv run python run.py AAPL
uv run python run.py MSFT -v  # verbose mode
```

**Run the FastAPI server**:
```bash
uv run python server.py
```

**Run with Docker Compose** (includes API and UI):
```bash
docker-compose up
```

**Note**: Supabase should be running separately (see Supabase setup below)

**Run tests**:
```bash
uv run python -m pytest tests/unit/ -v
```

**Run tests with coverage**:
```bash
uv run python -m pytest --cov=src
```

**Install dependencies**:
```bash
uv sync
```

## Architecture

This is a **Veratheon Research Agent** for stock analysis using a three-pillar autonomous workflow with OpenAI Agents SDK, featuring a FastAPI backend and SvelteKit UI frontend.

### Three-Pillar Autonomous Workflow

The agent uses three parallel research pillars that are synthesized into a comprehensive report:

```
                        User Query: "AAPL"
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│  QUANTITATIVE     │ │  QUALITATIVE      │ │  MACRO ECONOMIC   │
│  AGENT            │ │  AGENT            │ │  REPORT           │
│                   │ │                   │ │                   │
│  Tools:           │ │  Tools:           │ │  (No LLM - data   │
│  • Alpha Vantage  │ │  • xAI web_search │ │   lookup only)    │
│    - Overview     │ │  • xAI x_search   │ │                   │
│    - Financials   │ │                   │ │  Indicators:      │
│    - Earnings     │ │  Focus:           │ │  • CPI, Inflation │
│    - Estimates    │ │  • Recent news    │ │  • Unemployment   │
│    - Quote        │ │  • Market buzz    │ │  • Fed Funds Rate │
│                   │ │  • Social/X posts │ │  • Treasury Yields│
│  Focus:           │ │  • Analyst views  │ │  • VIX, GDP       │
│  Quarterly EPS    │ │  • Upcoming events│ │  • Sector ETF     │
│  Valuation        │ │                   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                ┌───────────────────────────┐
                │   SYNTHESIS AGENT         │
                │   Combines all three      │
                │   perspectives            │
                └───────────────────────────┘
                               │
                               ▼
                ┌───────────────────────────┐
                │   TRADE ADVICE AGENT      │
                │   Actionable ideas        │
                │   (Advisory only)         │
                └───────────────────────────┘
```

### Project Structure

```
src/
├── agents/                      # Autonomous workflow agents
│   ├── workflow.py              # Main entry point
│   ├── quantitative_agent.py    # Financial analysis (Alpha Vantage)
│   ├── qualitative_agent.py     # News/sentiment (xAI search)
│   ├── macro_report.py          # Economic indicators (no LLM)
│   ├── synthesis_agent.py       # Combines all reports
│   └── trade_advice_agent.py    # Trade ideas (advisory)
│
├── lib/                         # Shared utilities
│   ├── llm_model.py             # Model abstraction (xAI Grok)
│   ├── alpha_vantage_api.py     # Alpha Vantage API client
│   ├── supabase_cache.py        # Caching layer
│   └── supabase_job_tracker.py  # Job tracking
│
server/
└── api.py                       # FastAPI endpoints
```

### Model Configuration

- **Primary Model**: xAI Grok `grok-4-1-fast-reasoning` for analysis and synthesis
- **Non-Reasoning Model**: `grok-4-1-fast-non-reasoning` for simple extraction tasks
- Model abstraction via `src/lib/llm_model.py`

### API Endpoints

- `GET /health` - Health check
- `POST /research` - Start autonomous research job (returns job_id for tracking)
- `GET /report-status/{symbol}` - Check if report exists for symbol
- `GET /ticker-search?query=...` - Search for stock symbols

### Environment Variables

Required in `.env` file:
- `XAI_API_KEY`: xAI API key for Grok models
- `ALPHA_VANTAGE_API_KEY`: For financial data

Optional in `.env` file:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8085)
- `ENABLE_WEB_SEARCH`: Enable xAI web search (default: true, costs extra)
- `ENABLE_X_SEARCH`: Enable xAI X/Twitter search (default: follows ENABLE_WEB_SEARCH)
- `SUPABASE_URL`: Supabase project URL (e.g., http://127.0.0.1:54321 for local)
- `SUPABASE_ANON_KEY`: Supabase anonymous/publishable key
- `SUPABASE_SERVICE_KEY`: Supabase service role key (for server-side operations)

### Supabase Setup

The application uses Supabase for:
- **Job Tracking**: `research_jobs` table tracks research job status and metadata
- **Caching**: `research_cache` table caches analysis results with TTL via `expires_at`
- **RAG (Retrieval Augmented Generation)**: `research_docs` table stores research reports with vector embeddings
- **User History**: `user_research_history` table tracks user research activity
- **System Logs**: `system_logs` table for centralized error tracking

For local development, run Supabase in a separate directory and use `supabase status` to get connection details.

**Enable Realtime for research_jobs table** (required for frontend live updates):
```sql
alter publication supabase_realtime add table research_jobs;
```

### Testing Strategy

- Uses `pytest` with path configuration in `pyproject.toml`
- Test files in `tests/unit/` directory
- Mocks external API calls to avoid hitting real APIs during tests
- Supabase client is automatically mocked in all tests via `conftest.py` fixtures

## Development Guidelines

- Agent logic lives in `src/agents/`
- Shared utilities and API clients go in `src/lib/`
- Use `uv run` prefix for all Python commands
- API endpoints follow REST conventions and return structured JSON responses
- All external API calls should be mocked in tests to avoid hitting real services

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
