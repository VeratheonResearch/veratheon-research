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

- [ ] Create `src/agents/quantitative_agent.py`
  > **Comments:**

- [ ] Give agent access to existing Alpha Vantage tools from `src/lib/alpha_vantage_agent_tools.py`
  > **Comments:**

- [ ] Write basic prompt: "Analyze the financial health of {symbol}"
  > **Comments:**

- [ ] Test: Run workflow, verify agent calls AV tools and produces output
  > **Comments:**

#### 1.3 Qualitative Agent (Second Agent)

- [ ] Research web search options (xAI Live Search, Tavily, etc.)
  > **Comments:**

- [ ] Add web search capability (simplest option first)
  > **Comments:**

- [ ] Create `src/agents/qualitative_agent.py`
  > **Comments:**

- [ ] Write basic prompt: "Research what's happening with {symbol}"
  > **Comments:**

- [ ] Test: Run workflow, verify agent searches web and produces output
  > **Comments:**

#### 1.4 Macro Report (Data Fetch, No LLM)

- [ ] Create `src/agents/macro_report.py`
  > **Comments:**

- [ ] Implement basic fetchers using Alpha Vantage economic endpoints
  > **Comments:**

- [ ] Return structured data (CPI, rates, VIX, etc.)
  > **Comments:**

- [ ] Test: Macro data included in workflow output
  > **Comments:**

#### 1.5 Synthesis Agent

- [ ] Create `src/agents/synthesis_agent.py`
  > **Comments:**

- [ ] Takes outputs from quant + qual + macro
  > **Comments:**

- [ ] Produces unified research report
  > **Comments:**

- [ ] Test: Full workflow produces complete report
  > **Comments:**

---

### Phase 2: Enhance & Polish

#### 2.1 Add Trade Advice

- [ ] Create trade advice agent or add to synthesis
  > **Comments:**

- [ ] Include buy/sell/hold recommendation with reasoning
  > **Comments:**

#### 2.2 Add X/Twitter Search (if valuable)

- [ ] Evaluate if X search adds value
  > **Comments:**

- [ ] Implement if worthwhile
  > **Comments:**

#### 2.3 Improve Prompts

- [ ] Tune quantitative agent prompts based on output quality
  > **Comments:**

- [ ] Tune qualitative agent prompts based on output quality
  > **Comments:**

- [ ] Tune synthesis prompts
  > **Comments:**

#### 2.4 Add Caching

- [ ] Cache quantitative data (longer TTL)
  > **Comments:**

- [ ] Cache qualitative data (shorter TTL - news changes)
  > **Comments:**

- [ ] Cache macro data (medium TTL)
  > **Comments:**

---

### Phase 3: API Integration

#### 3.1 API Endpoint

- [ ] Add `POST /research/autonomous` endpoint
  > **Comments:**

- [ ] Wire up job tracking
  > **Comments:**

- [ ] Test via curl/Postman
  > **Comments:**

#### 3.2 Cleanup

- [ ] Delete `legacy/` directory once confirmed not needed
  > **Comments:**

- [ ] Update CLAUDE.md with new architecture
  > **Comments:**

---

## Environment Variables (New)

Add to `.env`:

```bash
# xAI API (Primary) - Already configured
XAI_API_KEY=your_xai_api_key

# Web Search (choose one based on Phase 1.3 research)
TAVILY_API_KEY=your_tavily_key  # If using Tavily
# OR use xAI Live Search (no additional key needed)

# X/Twitter API (optional - evaluate in Phase 2.2)
X_BEARER_TOKEN=your_x_bearer_token
```

---

## Notes & Decisions Log

*Add any major decisions, pivots, or discoveries here as implementation progresses.*

- 2026-01-30: Switched to iterative workflow approach. Moving legacy code to `legacy/` directory.

---

## Completion Checklist

- [x] Phase 0.1: Model support configured
- [x] Phase 0.2: Legacy code moved
- [ ] Phase 1: Minimal working workflow
- [ ] Phase 2: Enhancements
- [ ] Phase 3: API integration

---

*Last Updated: 2026-01-30*
