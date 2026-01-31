# Veratheon Research Agent Refactor Plan

## Instructions for Implementation

**As you complete each task, mark the checkbox `[x]` to indicate completion.**

**Comments are optional** Add any notes, discoveries, blockers, or context that would help if a new conversation context is started. Comments should be added directly below the relevant task in a blockquote format:

```markdown
- [x] Task description
  > **Comment:** Implementation note or context for future sessions.
```

You are permitted to make changes to this plan as needed, but if you do, please add a comment explaining the change, and why. You are strictly not allowed to change the Vision Statement section.

You must complete each task, one at a time, and stop for me to confirm the results. Do not move on to the next task until I have confirmed the current task is complete.

**Commit Policy:** Once a section (e.g., Phase 0.1, Phase 1.2) has been successfully verified as complete, stage and commit your changes with a descriptive commit message summarizing what was implemented in that section.

---

## Vision Statement

### The Problem

Retail investors face a fundamental challenge: they don't know what they don't know. When considering an investment in a company like Apple (AAPL), they see a stock price and maybe a P/E ratio, but they lack the complete picture. What's actually happening with the company? Is the business thriving or struggling? Are there geopolitical risks? Regulatory threats? Is the valuation reasonable given the circumstances? What's the broader economic environment doing to this stock?

Without this context, most retail investors either:
1. Make uninformed decisions based on incomplete information
2. Give up and just buy SPY, missing potential opportunities

### The Solution

Veratheon is an **autonomous research agent** that seeks to dispel the unknowns around any company a user is interested in investing in. It answers three fundamental questions every investor needs answered:

1. **"What's going on with this company?"** (Qualitative) - Not the stock price or fundamentals, but what is the *actual company* doing? What's happening in their world? Are they launching products? Facing lawsuits? Dealing with regulatory pressure? Is China threatening to ban their products? What is going on with their leadership team? What happened last quarter? What's expected next quarter?

2. **"What is the financial health of the company?"** (Quantitative) - How are the fundamentals? Is the P/E ratio justified? How are margins trending? How does it compare to peers? Is it overvalued or undervalued given the circumstances? Did they beat or miss last quarter? What are analysts expecting for next quarter?

3. **"What is the market environment?"** (Macro Context) - What is CPI at? Where are interest rates headed? What's the 10-year yield doing? Is the Fed hawkish or dovish? Is the economy expanding or contracting? Is the VIX elevated? How is this company's sector performing?

Then, the agent synthesizes all three perspectives into actionable intelligence:
- A **detailed report** combining qualitative, quantitative, and macro analysis
- A **summary report** for quick consumption
- A **trade advice report** with specific recommendations

### The Quarterly Lens

All company-specific analysis is focused on **quarterly earnings**:

- **Past Quarter:** What happened? Did they beat or miss? What drove the results? Any surprises or guidance changes?
- **Next Quarter:** What are expectations? What could cause a beat or miss? What are the key variables to watch?

Annual data may be referenced for context (verifying progress vs. annual guidance, fiscal year-end considerations, YoY comparisons), but **the primary lens is always the current and upcoming quarter**. The goal is to help investors understand the near-term picture for their investment decision.

### The End Goal

A user passes in a stock symbol (e.g., `AAPL`). They receive:

1. **Complete situational awareness** - Everything material happening with the company and its environment, focused on the current and next quarter
2. **Full financial analysis** - Valuation, fundamentals, technicals, peer comparison, with emphasis on quarterly performance
3. **Macro context** - The broader economic environment and how it affects this specific investment
4. **Synthesized intelligence** - A clear narrative combining all three perspectives
5. **Actionable advice** - Buy/sell/hold recommendation with reasoning, entry/exit strategies, and key catalysts to watch

**The user walks away knowing whether their investment idea makes sense**, armed with the same quality of research that institutional investors have access to.

### Example Scenario

> *Hypothetically: AAPL is trading at $300 with a P/E of 60 (astronomically high). Sales are soaring as everyone loves the new iPhone. However, the Fed is considering interest rate hikes, and China is threatening to ban iOS devices outright. Last quarter they beat estimates by 5%, but guided conservatively for next quarter.*
>
> *Should this person invest in AAPL?*

The Veratheon agent would:
- **Qualitative:** Discover the China threat through news/X searches, find reports of supply chain concerns, note conservative management guidance
- **Quantitative:** Analyze the sky-high P/E against growth rates, compare to historical valuation, note the earnings beat but weak guidance
- **Macro:** Identify the Fed rate risk, note that high-multiple growth stocks suffer in rising rate environments, check sector performance
- **Synthesize:** Weigh the strong sales against the external risks and macro headwinds
- **Recommend:** Perhaps "AVOID - valuation doesn't compensate for geopolitical and rate risk" or "SMALL POSITION - strong fundamentals but size appropriately for volatility"

---

## Analysis Focus: Quarterly Earnings

### Time Horizon

All company-specific analysis should be focused on **quarterly earnings**:

- **Past Quarter:** What happened? Did they beat/miss? What drove the results? Any surprises?
- **Next Quarter:** What are expectations? What could cause a beat/miss? What are the key variables to watch?

### Use of Annual Data

Annual reports (10-K, full-year financials) may be referenced for:
- Verifying if the company is on track vs. annual guidance
- Understanding if this is the company's fiscal year-end quarter
- Providing longer-term trend context
- Comparing YoY performance

**However, the primary lens is always the current and upcoming quarter.** The goal is to help investors understand the near-term picture, not create a long-term investment thesis.

### Earnings Calendar Awareness

The agent should be aware of:
- When did the company last report earnings?
- When is the next earnings date?
- Are we in a blackout period?
- How does timing affect the relevance of current news/guidance?

---

## Architecture Overview

### Three-Pillar Design (Plus Macro Context)

```
                            User Query: "AAPL"
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  QUALITATIVE      │   │  QUANTITATIVE     │   │  MACRO ECONOMIC   │
│  AGENT            │   │  AGENT            │   │  AGENT            │
│  "What's going    │   │  "Financial       │   │  "Market context" │
│   on?"            │   │   health?"        │   │                   │
│                   │   │                   │   │  Checklist:       │
│  Tools:           │   │  Tools:           │   │  • CPI            │
│  • Web search     │   │  • Company ovrvw  │   │  • Payrolls/Jobs  │
│  • X/Twitter      │   │  • Financials     │   │  • 10-yr yield    │
│  • News sentiment │   │  • Earnings data  │   │  • Fed funds rate │
│  • Company news   │   │  • Estimates      │   │  • GDP growth     │
│  • SEC filings    │   │  • Technicals     │   │  • VIX            │
│                   │   │  • Peer compare   │   │  • Sector trends  │
│  Focus:           │   │                   │   │  • Market breadth │
│  Past quarter     │   │  Focus:           │   │                   │
│  Next quarter     │   │  Quarterly EPS    │   │  (No LLM needed   │
│                   │   │  QoQ/YoY trends   │   │   - data lookup)  │
└───────────────────┘   └───────────────────┘   └───────────────────┘
          │                        │                        │
          ▼                        ▼                        ▼
  Qualitative Report      Quantitative Report      Macro Report
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │   DETAILED REPORT AGENT   │
                    │   Synthesizes all three   │
                    │   into comprehensive      │
                    │   narrative               │
                    └───────────────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │   SUMMARY REPORT AGENT    │
                    │   Key points (~500 words) │
                    └───────────────────────────┘
                                   │
                                   ▼
                    ┌───────────────────────────┐
                    │   TRADE ADVICE AGENT      │
                    │   Actionable recommendation│
                    │   (considers macro context)│
                    └───────────────────────────┘
```

### Macro Economic Report

The Macro Economic Report provides essential market context. This is a **checklist-driven data lookup**, not an LLM analysis. It answers: "What is the current state of the economy and markets?"

**Indicators to fetch:**

| Category | Indicator | Why It Matters |
|----------|-----------|----------------|
| **Inflation** | CPI (latest) | Affects Fed policy, consumer spending |
| **Inflation** | PCE (latest) | Fed's preferred inflation measure |
| **Employment** | Non-Farm Payrolls | Economic health indicator |
| **Employment** | Unemployment Rate | Labor market tightness |
| **Interest Rates** | Fed Funds Rate | Cost of capital, valuations |
| **Interest Rates** | 10-Year Treasury Yield | Discount rate, growth vs value |
| **Interest Rates** | 2-Year Treasury Yield | Near-term rate expectations |
| **Growth** | GDP (latest quarter) | Economic expansion/contraction |
| **Volatility** | VIX | Market fear gauge |
| **Market** | S&P 500 trend | Broad market direction |
| **Sector** | Relevant sector ETF performance | Industry tailwinds/headwinds |
| **Sentiment** | AAII Sentiment | Retail investor mood |

**Output:** Simple structured data with current values, recent trends, and brief context (e.g., "CPI: 3.2% - down from 3.4% last month, trending toward Fed target")

### Model Strategy

- **Primary:** xAI Grok APIs (favor but don't lock in)
- **Fallback:** Not necessary at this time
- **Pattern:** Extend existing `litellm` abstraction in `src/lib/llm_model.py`

---

## Project Structure (Proposed Target State)

```
src/
├── agents/                              # NEW - All agent definitions
│   ├── __init__.py
│   ├── qualitative/
│   │   ├── __init__.py
│   │   ├── agent.py                     # Qualitative research agent
│   │   ├── models.py                    # Pydantic output models
│   │   └── prompts.py                   # Agent instructions
│   │
│   ├── quantitative/
│   │   ├── __init__.py
│   │   ├── agent.py                     # Quantitative research agent
│   │   ├── models.py                    # Pydantic output models
│   │   └── prompts.py                   # Agent instructions
│   │
│   ├── macro/
│   │   ├── __init__.py
│   │   ├── macro_report.py              # Checklist-driven data fetcher (no LLM)
│   │   └── models.py                    # Pydantic output models
│   │
│   └── synthesis/
│       ├── __init__.py
│       ├── detailed_report_agent.py
│       ├── summary_report_agent.py
│       ├── trade_advice_agent.py
│       └── models.py                    # All synthesis output models
│
├── tools/                               # NEW - Agent tools
│   ├── __init__.py
│   ├── web_search.py                    # Web search tool (xAI/Tavily)
│   ├── x_search.py                      # X/Twitter search tool
│   ├── alpha_vantage.py                 # All AV tools (refactored)
│   ├── macro_economic.py                # Economic indicators (FRED, etc.)
│   └── sec_filings.py                   # SEC EDGAR tools (optional)
│
├── flows/
│   ├── research_flow.py                 # KEEP - Legacy sequential flow
│   └── autonomous_flow.py               # NEW - Two-pillar autonomous flow
│
├── lib/
│   ├── llm_model.py                     # MODIFY - Extend for xAI models
│   ├── alpha_vantage_api.py             # KEEP - Raw API calls
│   ├── web_search_api.py                # NEW - Web search client
│   ├── x_api.py                         # NEW - X API client
│   └── clients/
│       └── ...
│
├── research/                            # KEEP - Legacy agents (reference)
│   └── ...
│
└── tasks/                               # KEEP - Legacy tasks (reference)
    └── ...
```

---

## Implementation Notes

**This is a first draft rough refactor.** Don't worry too much about perfect deliverables or extensive documentation. Focus on getting things working. Comments in the task list are optional and only needed for changes that require more consideration or context for future sessions.

For "review" tasks, a small summary of findings is expected (can be verbal or in comments).

---

## Implementation Phases

**Approach:** Build iteratively with a working workflow. After each phase, we should be able to run the workflow and see results. Add capabilities incrementally.

---

### Phase 0: Setup & Cleanup

#### 0.1 Model Support (COMPLETED)

**Model Selection:** Use only these two xAI Grok models:
- `grok-4-1-fast-reasoning` - **Primary/default.** Use for any task requiring analysis, synthesis, or decision-making.
- `grok-4-1-fast-non-reasoning` - Use only for simple tasks where reasoning would be wasteful (e.g., pure text extraction, formatting).

- [x] Review existing `src/lib/llm_model.py` implementation
  > **Comments:** Current implementation uses `LitellmModel` from agents SDK with `grok-4-fast-reasoning`. Needs update to `grok-4-1-fast-reasoning`. Uses `ContextVar` for async-safe model selection. XAI_API_KEY already configured. Need to add non-reasoning model option.

- [x] Update to use `grok-4-1-fast-reasoning` as primary model
  > **Comments:** Updated model from `grok-4-fast-reasoning` to `grok-4-1-fast-reasoning`. Set as default in context variable. Renamed variable to `xai_grok_4_1_fast_reasoning_model`.

- [x] Add `grok-4-1-fast-non-reasoning` option for simple tasks
  > **Comments:** Added `xai_grok_4_1_fast_non_reasoning_model` for simple tasks like text extraction and formatting. Updated `get_model()` to support both model choices.

- [x] Test model switching works correctly
  > **Comments:** All tests passed: default model selection, explicit model selection for both reasoning and non-reasoning, context switching via `set_model_context()`, and o4_mini fallback.

#### 0.2 Move Legacy Code

Move existing code to `legacy/` directory for reference. Keep `src/lib/` as it has useful API clients.

- [x] Create `legacy/` directory
  > **Comments:** Created at `/veratheon-research/legacy/`

- [x] Move `src/flows/` to `legacy/flows/`
  > **Comments:** Moved successfully.

- [x] Move `src/research/` to `legacy/research/`
  > **Comments:** Moved successfully.

- [x] Move `src/tasks/` to `legacy/tasks/`
  > **Comments:** Moved successfully.

- [x] Verify `src/lib/` remains intact (alpha_vantage_api.py, supabase_*, llm_model.py, etc.)
  > **Comments:** Verified. All lib files intact: alpha_vantage_agent_tools.py, alpha_vantage_api.py, llm_model.py, supabase_*.py, fiscal_year_utils.py, token_logger_hook.py, clients/.

- [x] Update any imports if needed (server.py, run.py)
  > **Comments:** Updated imports in run.py, server/api.py, all legacy/*.py files, and tests/unit/*.py. Used `legacy.flows/research/tasks` instead of `src.flows/research/tasks`. Verified imports work with `uv run python -c "from legacy.flows.research_flow import main_research_flow"`.

---

### Phase 1: Minimal Working Workflow

**Goal:** Create a simple end-to-end workflow that we can run with `uv run python run_autonomous.py AAPL`. Start minimal, add complexity later.

#### 1.1 Create Basic Workflow Structure

- [x] Create `src/agents/` directory structure
  > **Comments:** Created `src/agents/` with `__init__.py`.

- [x] Create `src/agents/workflow.py` - Main entry point
  > **Comments:** Created with `WorkflowResult` dataclass, stub functions for all agents (quantitative, qualitative, macro, synthesis), and `run_autonomous_workflow()` that runs agents in parallel using `asyncio.create_task()`.

- [x] Create `run_autonomous.py` - CLI runner script
  > **Comments:** Created with argparse for CLI args, supports `uv run python run_autonomous.py AAPL` syntax, includes `-v` verbose flag.

- [x] Test: Can run `uv run python run_autonomous.py AAPL` (even if output is minimal)
  > **Comments:** Verified working. Outputs formatted report with placeholder text for each section.

#### 1.2 Quantitative Agent (First Agent)

Start with quantitative since we have Alpha Vantage data already working.

- [x] Create `src/agents/quantitative_agent.py`
  > **Comments:** Created with 7 Alpha Vantage tools (overview, income statement, balance sheet, cash flow, earnings, earnings estimates, global quote) and comprehensive agent instructions.

- [x] Give agent access to existing Alpha Vantage tools from `src/lib/alpha_vantage_agent_tools.py`
  > **Comments:** Created new `@function_tool` decorated functions directly in quantitative_agent.py for cleaner encapsulation. Tools include: get_company_overview, get_income_statement, get_balance_sheet, get_cash_flow, get_earnings, get_earnings_estimates, get_global_quote.

- [x] Write basic prompt: "Analyze the financial health of {symbol}"
  > **Comments:** Wrote comprehensive QUANTITATIVE_AGENT_INSTRUCTIONS with structured output format: Executive Summary, Earnings Analysis, Valuation Assessment, Financial Strength, Key Metrics Table, Risks & Opportunities.

- [x] Test: Run workflow, verify agent calls AV tools and produces output
  > **Comments:** Verified working with `uv run python run_autonomous.py AAPL`. Agent successfully calls tools and produces detailed financial analysis with specific numbers.

#### 1.3 Qualitative Agent (Second Agent)

- [x] Research web search options (xAI Live Search, xAI X Search)
  > **Comments:** xAI provides server-side `web_search` and `x_search` tools via the `/v1/responses` endpoint. Use OpenAI SDK with `base_url="https://api.x.ai/v1"` and `client.responses.create()`. Model `grok-4-1-fast` is optimized for search tasks. Tools passed as `[{"type": "web_search"}, {"type": "x_search"}]`.

- [x] Add web search capability (simplest option first)
  > **Comments:** Used xAI's native server-side tools via OpenAI SDK with xAI base URL. Created `get_xai_client()` function for lazy initialization.

- [x] Create `src/agents/qualitative_agent.py`
  > **Comments:** Created with xAI web_search and x_search integration. Uses `/v1/responses` endpoint directly since these are server-side tools (different from function tools). Includes error handling for auth, rate limits, and API failures.

- [x] Write basic prompt: "Research what's happening with {symbol}"
  > **Comments:** Wrote comprehensive QUALITATIVE_AGENT_INSTRUCTIONS with structured output format: Executive Summary, Recent Developments, Market Sentiment, Upcoming Catalysts, Key Risks, Notable Social/X Posts.

- [x] Add .env toggle to disable web search because its expensive
  > **Comments:** Added `ENABLE_WEB_SEARCH` environment variable (default: true). When false, returns informative message explaining how to enable and that it incurs additional API costs.

- [x] Test: Run workflow, verify agent searches web and produces output
  > **Comments:** Verified working with `uv run python run_autonomous.py AAPL`. Agent successfully uses web_search and x_search tools, produces detailed qualitative analysis with inline citations, recent news (Q1 FY2026 earnings), analyst upgrades, and X posts.

#### 1.4 Macro Report (Data Fetch, No LLM)

- [x] Create `src/agents/macro_report.py`
  > **Comments:** Created with MacroReport and EconomicIndicator dataclasses, MacroReportFetcher class with batched API calls to avoid rate limiting. Includes sector ETF mapping for 12+ sectors.

- [x] Implement basic fetchers using Alpha Vantage economic endpoints
  > **Comments:** Implemented fetchers for CPI, INFLATION, UNEMPLOYMENT, NONFARM_PAYROLL, FEDERAL_FUNDS_RATE, TREASURY_YIELD (2y, 10y), REAL_GDP. Uses batched requests with 0.5s delays between batches to avoid Alpha Vantage rate limits.

- [x] Return structured data (CPI, rates, VIX, etc.)
  > **Comments:** Returns MacroReport dataclass with: CPI index, inflation rate, unemployment, non-farm payrolls, fed funds rate, 10-year/2-year treasury yields, real GDP (with annualized growth calculation), VIX (via VIXY ETF), S&P 500 (via SPY), and sector-specific ETF. Includes trend indicators and contextual interpretations (e.g., VIX levels, yield curve inversion detection).

- [x] Test: Macro data included in workflow output
  > **Comments:** Verified with `uv run python run_autonomous.py AAPL`. Macro report displays correctly with formatted output including all indicators, trends, and context. Workflow gets company sector via OVERVIEW endpoint to fetch relevant sector ETF.

#### 1.5 Synthesis Agent

- [x] Create `src/agents/synthesis_agent.py`
  > **Comments:** Created with comprehensive SYNTHESIS_AGENT_INSTRUCTIONS prompt that guides cross-reference analysis, time horizon considerations, and structured output (Executive Summary, Complete Picture, Key Insights, Risk Assessment, Catalysts & Timing, Investment Conclusion).

- [x] Takes outputs from quant + qual + macro
  > **Comments:** `run_synthesis_agent()` accepts quantitative_report (str), qualitative_report (str), and macro_report (MacroReport/dict/str). Formats macro report using `format_report()` method or `_format_macro_dict()` helper.

- [x] Produces unified research report
  > **Comments:** Uses grok-4-1-fast-reasoning model (via `get_model()`) with no tools (pure reasoning). Output includes: investment thesis, how three perspectives interact, contradictions/confirmations, risk categorization, and actionable recommendations with confidence levels.

- [x] Test: Full workflow produces complete report
  > **Comments:** Verified with `uv run python run_autonomous.py AAPL`. Synthesis successfully combined quantitative (earnings beats, margins, valuation), qualitative (noted disabled web search), and macro (GDP growth, VIX, inflation) into comprehensive investment narrative with Bullish/Medium confidence conclusion.

---

### Phase 2: Enhance & Polish

#### 2.1 Add Trade Advice (COMPLETED)

- [x] Create trade advice agent or add to synthesis
  > **Comments:** Created `src/agents/trade_advice_agent.py` as a separate agent (not part of synthesis) that takes the synthesis report and generates actionable trade ideas. Includes comprehensive prompt with structured output: Trade Setup Summary, Position Considerations, Entry Strategy, Position Sizing, Risk Management, Profit Targets, Catalysts & Timing, Alternative Approaches.

- [x] Include trade advice as advisory only and not a recommendation.
  > **Comments:** Added prominent disclaimers at multiple levels: (1) agent instructions emphasize "ADVISORY ONLY" and "NOT a financial recommendation", (2) output is prepended with warning notice box, (3) final disclaimer at end of output, (4) format_workflow_result displays section as "TRADE IDEAS (ADVISORY ONLY)".

#### 2.2 Add X/Twitter Search (COMPLETED)

- [x] Evaluate if X search adds value
  > **Comments:** X search adds significant value. Testing showed unique contributions including:
  > - Real-time market sentiment and reactions (e.g., post-earnings buzz)
  > - Influencer/analyst commentary with engagement metrics (likes, retweets)
  > - Breaking news often ahead of traditional media (CEO comments, supply constraints)
  > - Social proof signals from financial X accounts (@NewsFromWSB, @zerohedge, @DeItaone)
  > - Notable Social/X Posts section with specific tweet citations and links
  > - Example: Tim Cook's "supply chase mode" quote surfaced via X before news articles

- [x] Implement if worthwhile
  > **Comments:** X search was already integrated in Phase 1.3. Enhanced with:
  > - Added separate `ENABLE_X_SEARCH` toggle for independent control
  > - Defaults to follow `ENABLE_WEB_SEARCH` for backwards compatibility
  > - Users can now enable: web only, X only, both, or neither
  > - Updated prompts to adjust based on enabled search types
  > - Updated .env.example with new variable documentation

#### 2.3 Improve Prompts (COMPLETED)

- [x] Tune quantitative agent prompts based on output quality
  > **Comments:** Restructured to be table-driven and concise. Added: One-Line Thesis, Quarterly Scorecard table, Next Quarter Setup, Valuation Verdict, Financial Health Check, Key Numbers table, Watch List. Focuses on quarterly earnings lens per vision statement. Uses specific numbers and flags missing data.

- [x] Tune qualitative agent prompts based on output quality
  > **Comments:** Added structured search strategy (priority vs secondary searches), source credibility guidance, "Story in 30 Seconds" summary, Last Quarter Recap with management quotes, Upcoming Catalysts table, Sentiment Check, Risk Radar. Emphasizes actionable insights over verbose summaries.

- [x] Tune synthesis prompts
  > **Comments:** Reduced target length to 400-600 words. Added: Investment Thesis (2-3 sentences), condensed The Picture section, Key Insights (3-5 synthesized bullets), Risk/Reward Summary table, Near-Term Setup, Bottom Line verdict table. Includes explicit handling for missing qualitative data. Also tuned Trade Advice agent for consistency (table-driven entry/exit/stop, single key catalyst focus).

#### 2.4 Add Caching - NOT NEEDED FOR NOW - SKIP

- [ ] SKIP - Cache quantitative data (longer TTL)
  > **Comments:**

- [ ] SKIP - Cache qualitative data (shorter TTL - news changes)
  > **Comments:**

- [ ] SKIP - Cache macro data (medium TTL)
  > **Comments:**

---

### Phase 3: API Integration

#### 3.1 API Endpoint

- [x] Add `POST /research/autonomous` endpoint
  > **Comments:** Added endpoint in `server/api.py`. Takes `{"symbol": "AAPL"}` request body, creates job in Supabase, runs autonomous workflow in background task. Returns `job_id` for tracking via Realtime.

- [x] Wire up job tracking
  > **Comments:** Uses existing `JobTracker` with `job_type="autonomous_research"` and `job_name="main_flow"`. Converts `WorkflowResult` dataclass to dict for storage, including handling `MacroReport` dataclass serialization. Updates status through `pending` → `running` → `completed/failed`.

- [x] Test via curl/Postman
  > **Comments:** Verified with `curl -X POST http://localhost:8085/research/autonomous -H "Content-Type: application/json" -d '{"symbol": "AAPL"}'`. Returns `{"job_id": "uuid", "status": "pending", "message": "Autonomous research job started for AAPL"}`. Endpoint visible in `/openapi.json`.

#### 3.2 Cleanup (COMPLETED)

- [x] Delete `legacy/` directory once confirmed not needed
  > **Comments:** Deleted legacy/ directory with flows/, research/, tasks/. Updated server/api.py to remove legacy imports and deprecated endpoints (/research now uses autonomous workflow, removed /agent-debug). Updated run.py to use autonomous workflow with CLI args (symbol required). Deleted legacy test directories (earnings_projections, financial_statements, flows, historical_earnings, management_guidance, tasks, trade_ideas). Kept valid tests in clients/, lib/, and test_alpha_vantage_api.py (32 tests passing).

- [x] Update CLAUDE.md with new architecture
  > **Comments:** Rewrote CLAUDE.md to document three-pillar autonomous workflow architecture, new project structure (src/agents/), model configuration (xAI Grok), API endpoints, and updated environment variables (XAI_API_KEY, ENABLE_WEB_SEARCH, ENABLE_X_SEARCH).

---

## Environment Variables (New)

Add to `.env`:

```bash
# xAI API (Primary) - Already configured
XAI_API_KEY=your_xai_api_key (already configured)

# Web Search (choose one based on Phase 1.3 research)
We are using xAI Live Search (no additional key needed)

# X/Twitter API (optional - evaluate in Phase 2.2)
Use XAI X Search (no additional key needed)
```

---

## Notes & Decisions Log

*Add any major decisions, pivots, or discoveries here as implementation progresses.*

- 2026-01-30: Switched to iterative workflow approach. Moving legacy code to `legacy/` directory.

---

## Completion Checklist

- [x] Phase 0.1: Model support configured
- [x] Phase 0.2: Legacy code moved
- [x] Phase 1: Minimal working workflow
- [x] Phase 2: Enhancements (2.1 Trade Advice, 2.2 X Search, 2.3 Improved Prompts - 2.4 Caching skipped)
- [x] Phase 3: API integration (3.1 API Endpoint, 3.2 Cleanup)

---

### Phase 4: Frontend Integration

**Goal:** Update the frontend (veratheon-ui/) to work with the new autonomous workflow backend. The frontend is currently configured for a legacy implementation that no longer exists.

#### Current State Analysis

**Frontend expects (legacy):**
- `POST /research` → returns `{ job_id, message }`
- Job structure with `main_job_id` + 14 `sub_job_id` entries for progress tracking
- Result structure: `{ comprehensive_report: { comprehensive_analysis }, key_insights: { critical_insights } }`
- Supabase Realtime updates on `research_jobs` table
- `/report-status/{symbol}` endpoint
- `/ticker-search?query=` endpoint

**Backend now provides:**
- `POST /research/autonomous` → returns `{ job_id, status, message }`
- Single job with `WorkflowResult` containing: `quantitative_report`, `qualitative_report`, `macro_report`, `synthesis_report`, `trade_advice`
- 5 parallel agents instead of 14 sequential steps

**Key gaps to address:**
1. Endpoint path mismatch (`/research` vs `/research/autonomous`)
2. Result structure mismatch (frontend expects `comprehensive_report`/`key_insights`)
3. Progress tracking (frontend expects 14 sub-jobs, backend has 5 agents)
4. Job metadata structure differences

---

#### 4.1 Backend API Compatibility Layer

Update backend to match what frontend expects OR update frontend to match new backend. Recommend updating frontend since it's cleaner.

- [x] Rename `POST /research/autonomous` to `POST /research` (replace legacy endpoint)
  > **Comments:** Already named `/research` - endpoint was correctly configured in Phase 3.2 cleanup. No changes needed.

- [x] Update response structure to match frontend expectations
  > **Comments:** Response returns `{ job_id, status, message }`. Extra `status` field is backwards compatible with frontend expecting `{ job_id, message }`. No changes needed.

- [x] Verify `/report-status/{symbol}` endpoint exists and works
  > **Comments:** Endpoint exists. Updated to check for new `synthesis_report` field instead of legacy `comprehensive_report.comprehensive_analysis`. Returns `{ has_report, completed_at, symbol, job_id }`.

- [x] Verify `/ticker-search?query=` endpoint exists and works
  > **Comments:** Endpoint exists and works. Uses `call_alpha_vantage_symbol_search()` to return matching symbols.

- [x] Add `/jobs/{job_id}` endpoint for job status lookup
  > **Comments:** Added `GET /jobs/{job_id}` endpoint. Returns full job data: `{ job_id, symbol, status, created_at, updated_at, completed_at, failed_at, result, error, steps }`. Returns 404 if job not found.

- [x] Add `/jobs/symbol/{symbol}` endpoint for symbol-based lookup
  > **Comments:** Added `GET /jobs/symbol/{symbol}` endpoint. Fetches most recent job for symbol. Returns same structure as `/jobs/{job_id}`. Returns 404 if no job found for symbol.

---

#### 4.2 Result Structure Alignment

Update frontend to use the new `WorkflowResult` structure. Remove all legacy type definitions.

**New structure from backend:**
```typescript
interface WorkflowResult {
  symbol: string;
  quantitative_report: string;
  qualitative_report: string;
  macro_report: MacroReport;
  synthesis_report: string;
  trade_advice: string;
}
```

- [x] Remove legacy types from `/src/lib/research-types.ts`
  > **Comments:** Removed `ComprehensiveReport`, `KeyInsights`, and legacy `ResearchResult` interfaces. Updated `TradeValidationRequest` to use `WorkflowResult` instead.

- [x] Add new `WorkflowResult` type to `/src/lib/research-types.ts`
  > **Comments:** Added complete type hierarchy matching backend: `EconomicIndicator`, `MarketIndicator`, `MacroReport`, and `WorkflowResult` interfaces with proper nullable types.

- [x] Update all imports/usages of legacy types across frontend
  > **Comments:** Updated imports in: `useRealtimeResearch.ts`, `+page.svelte`, `ResearchReportDisplay.svelte`, `ResearchStatusHeader.svelte`, `ProcessDetailsModal.svelte`. Changed all `ResearchResult` references to `WorkflowResult`. Updated debug logging to reference new structure (`synthesis_report` instead of `comprehensive_report`). Rewrote `ResearchReportDisplay.svelte` with new collapsible section UI for synthesis, trade advice, quantitative, qualitative, and macro reports.

---

#### 4.3 Progress Tracking & Sub-Jobs

Frontend expects 14 sub-jobs with status tracking. New workflow has 5 agents running in parallel.

**New sub-job structure (5 agents):**
1. `quantitative_agent` - Financial analysis (Alpha Vantage)
2. `qualitative_agent` - News/sentiment (xAI search)
3. `macro_report` - Economic indicators (no LLM)
4. `synthesis_agent` - Combines all reports
5. `trade_advice_agent` - Trade recommendations

- [x] Update `JobTracker` to create sub-jobs for each agent
  > **Comments:** Added `create_sub_job()` and `update_sub_job_status()` helper methods to `src/lib/supabase_job_tracker.py`. These convenience methods simplify sub-job creation and status updates within the workflow.

- [x] Update workflow to emit progress events
  > **Comments:** Updated `src/agents/workflow.py` to accept optional `main_job_id` parameter. Added `run_with_tracking()` helper that wraps agent coroutines with sub-job status updates (pending → running → completed/failed). Creates sub-jobs for all 5 agents upfront, then tracks each agent's progress.

- [x] Update frontend `TOTAL_RESEARCH_STEPS` constant from 14 to 5
  > **Comments:** Updated constant in `veratheon-ui/src/routes/+page.svelte`. Added comment explaining the 5 agents: quantitative, qualitative, macro, synthesis, trade_advice.

- [x] Update `ResearchFlowsSection.svelte` to display new agent names
  > **Comments:** Added `AGENT_DISPLAY_NAMES` mapping and `getDisplayName()` function in `veratheon-ui/src/lib/components/ResearchFlowsSection.svelte`. Maps internal names to user-friendly labels: "Quantitative Analysis", "Qualitative Research", "Macro Economic", "Synthesis", "Trade Ideas".

---

#### 4.4 Frontend Component Updates (COMPLETED)

Rewrite UI components to display new `WorkflowResult` structure. Remove all legacy display logic.

- [x] Rewrite `ResearchReportDisplay.svelte` for new structure
  > **Comments:** Already completed in 4.2. Component now displays all 5 sections (synthesis, trade advice, quantitative, qualitative, macro) with collapsible accordion layout. Each section has appropriate icons and colors.

- [x] Create tabbed or accordion layout for report sections
  > **Comments:** Implemented as collapsible accordion sections. Synthesis is expanded by default. Each section can be toggled independently with expand/collapse arrows.

- [x] Add trade advice disclaimer styling
  > **Comments:** Trade advice section has warning badge ("Advisory Only"), yellow/orange border (`border-warning/30`), and yellow background (`bg-warning/10`) for visual distinction.

- [x] Update `+page.svelte` for new data flow
  > **Comments:** Already completed in 4.2. Uses `WorkflowResult` type, `TOTAL_RESEARCH_STEPS = 5`, and all legacy references removed.

- [x] Remove legacy component code
  > **Comments:** Updated `history/+page.svelte` to use `synthesis_report` instead of `key_insights.critical_insights`. All research workflow legacy code removed. Remaining `key_insights`/`critical_insights` references are in `HistoricalEarningsDisplay.svelte` which is a separate feature with its own types (unrelated to research workflow).

---

#### 4.5 API Client Updates (veratheon-ui) (COMPLETED)

Update SvelteKit API routes and client functions.

- [x] Update `/src/lib/api/research.ts` - `startResearch()` function
  > **Comments:**
  > Removed `forceRecompute` and `model` parameters. Backend only accepts `symbol` now. Also removed `forceRecompute` parameter from `saveJobToHistory()` function.

- [x] Update `/src/routes/api/research/start/+server.ts` proxy endpoint
  > **Comments:**
  > Removed `force_recompute` and `model` parameter handling. Only forwards `symbol` to backend `/research` endpoint.

- [x] Update `/src/routes/api/research/status/[symbol]/+server.ts`
  > **Comments:**
  > Already updated in 4.1. Uses new `/jobs/{job_id}` and `/jobs/symbol/{symbol}` endpoints. Works correctly with new structure.

- [x] Update `/src/routes/api/research/report-status/[symbol]/+server.ts`
  > **Comments:**
  > Already updated in 4.1. Simple proxy to backend `/report-status/{symbol}`. Works correctly.

- [x] Update `/src/lib/composables/useRealtimeResearch.ts`
  > **Comments:**
  > Already compatible with new structure. Uses `WorkflowResult` type from 4.2. Handles sub-jobs correctly. No changes needed.

- [x] Update frontend components that call `startResearch()`
  > **Comments:**
  > Updated `+page.svelte` to remove `forceRecompute` variable and `getPreferredModel()` function. Updated `ResearchInputCard.svelte` to remove "Recompute" checkbox UI. Simplified API calls to only pass `symbol`.

---

#### 4.6 Type Definitions (veratheon-ui) (COMPLETED)

Replace all legacy types with new data structures. No backwards compatibility.

- [x] Rewrite `/src/lib/research-types.ts` completely
  > **Comments:** Completed in 4.2 and further enhanced here. File now contains comprehensive type hierarchy:
  > - WorkflowResult with all report fields (quantitative_report, qualitative_report, macro_report, synthesis_report, trade_advice)
  > - MacroReport with nested structure (inflation, employment, interest_rates, growth, market) matching backend to_dict() output
  > - EconomicIndicator and MarketIndicator for macro data
  > - Trade-related types (TradeDetails, Trade, TradeResponse, TradeValidationRequest)
  > - Job tracking types (JobStatus, SubJob, JobStep) consolidated from useRealtimeResearch.ts

- [x] Update `SubJob` interface for new agent names
  > **Comments:** Interface uses generic `job_name: string` field which works for all agent names. Added documentation comment listing the 5 agent names: quantitative_agent, qualitative_agent, macro_report, synthesis_agent, trade_advice_agent.

- [x] Update `JobStatus` interface - result is now `WorkflowResult`
  > **Comments:** Already had `result?: WorkflowResult` field. Consolidated from useRealtimeResearch.ts to research-types.ts for better organization.

- [x] Remove any unused legacy type exports
  > **Comments:** All legacy types (ComprehensiveReport, KeyInsights, legacy ResearchResult) were removed in 4.2. No remaining legacy types found. All components verified to use new WorkflowResult structure.

---

#### 4.7 Testing & Verification - Completed by User

- [x] Test end-to-end flow: Start research → Track progress → Display results
  > **Comments:** Completed. Verified all 5 agents run sequentially and progress is tracked correctly.

- [x] Test Supabase Realtime updates work correctly
  > **Comments:** Completed. Verified Realtime subscription receives job status updates with sub-job progress.

- [x] Test polling fallback works if Realtime fails
  > **Comments:** Completed. Verified polling mechanism works as fallback when Realtime subscription fails.

- [x] Test cached report detection (`/report-status/{symbol}`)
  > **Comments:** Completed. Verified cached report detection works correctly with new WorkflowResult structure.

- [x] Test ticker search functionality
  > **Comments:** Completed. Verified ticker search works correctly with new API contract.

- [x] Verify mobile responsiveness of updated components
  > **Comments:** Completed. Verified mobile responsiveness of all updated components.

---

#### 4.8 Documentation Updates (COMPLETED)

- [x] Update veratheon-ui CLAUDE.md with new API contract
  > **Comments:** Created comprehensive CLAUDE.md for veratheon-ui documenting the autonomous workflow architecture, API contract (POST /research, WorkflowResult structure, 5 agents), frontend structure, data types, key components (ResearchReportDisplay, ResearchFlowsSection, useRealtimeResearch), environment variables, development guidelines, and deployment instructions.

- [x] Update any relevant comments in frontend code
  > **Comments:** Reviewed all frontend code. Comments are already accurate and up-to-date (references to 5 agents, autonomous workflow, WorkflowResult structure). Removed unused `/api/research/+server.ts` endpoint that still had legacy `force_recompute` parameter (frontend uses `/api/research/start` instead).

---

## Implementation Order Recommendation

For Phase 4, recommended implementation order:

1. **4.1 Backend API Compatibility** - Fix endpoints first
2. **4.2 Result Structure** - Decide and implement transformation approach
3. **4.6 Type Definitions** - Update types before components
4. **4.3 Progress Tracking** - Enable sub-job tracking in backend
5. **4.5 API Client Updates** - Update frontend API layer
6. **4.4 Frontend Components** - Update UI components
7. **4.7 Testing** - Verify everything works
8. **4.8 Documentation** - Update docs

---

## Completion Checklist

- [x] Phase 0.1: Model support configured
- [x] Phase 0.2: Legacy code moved
- [x] Phase 1: Minimal working workflow
- [x] Phase 2: Enhancements (2.1 Trade Advice, 2.2 X Search, 2.3 Improved Prompts - 2.4 Caching skipped)
- [x] Phase 3: API integration (3.1 API Endpoint, 3.2 Cleanup)
- [x] Phase 4: Frontend integration (4.1-4.8)

---

*Last Updated: 2026-01-31 (Phase 4 completed - all refactor phases complete)*
