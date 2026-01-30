# Veratheon Research Agent Refactor Plan

## Instructions for Implementation

**As you complete each task, mark the checkbox `[x]` to indicate completion.**

**Comments are optional** Add any notes, discoveries, blockers, or context that would help if a new conversation context is started. Comments should be added directly below the relevant task in a blockquote format:

```markdown
- [x] Task description
  > **Comment:** Implementation note or context for future sessions.
```

You are permitted to make changes to this plan as needed, but if you do, please add a comment explaining the change, and why. You are strictly not allowed to change the Vision Statement section.

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

## Implementation Phases

### Phase 1: Infrastructure (Tools & Clients)

#### 1.1 Extend Model Support

- [ ] Review existing `src/lib/llm_model.py` implementation
  > **Comments:**

- [ ] Add additional xAI Grok model options (grok-2, grok-2-mini, etc.)
  > **Comments:**

- [ ] Ensure fallback to OpenAI works correctly
  > **Comments:**

- [ ] Test model switching between xAI and OpenAI
  > **Comments:**

- [ ] Document supported models and their use cases
  > **Comments:**

#### 1.2 Create Web Search Tool

- [ ] Create `src/lib/web_search_api.py` - Raw API client
  > **Comments:**

- [ ] Research and select web search provider (xAI native, Tavily, SerpAPI)
  > **Comments:**

- [ ] Implement search function with proper error handling
  > **Comments:**

- [ ] Create `src/tools/web_search.py` with `@function_tool` decorator
  > **Comments:**

- [ ] Test web search tool independently
  > **Comments:**

#### 1.3 Create X/Twitter Search Tool

- [ ] Create `src/lib/x_api.py` - X API client
  > **Comments:**

- [ ] Implement X API authentication (OAuth or API key)
  > **Comments:**

- [ ] Implement search function for recent tweets by ticker/company
  > **Comments:**

- [ ] Create `src/tools/x_search.py` with `@function_tool` decorator
  > **Comments:**

- [ ] Test X search tool independently
  > **Comments:**

#### 1.4 Refactor Alpha Vantage as Tools

- [ ] Create `src/tools/__init__.py`
  > **Comments:**

- [ ] Create `src/tools/alpha_vantage.py`
  > **Comments:**

- [ ] Convert `get_company_overview` to `@function_tool`
  > **Comments:**

- [ ] Convert `get_financial_statements` (income, balance, cash flow) to tools
  > **Comments:**

- [ ] Convert `get_earnings_history` to `@function_tool`
  > **Comments:**

- [ ] Convert `get_analyst_estimates` to `@function_tool`
  > **Comments:**

- [ ] Convert `get_stock_quote` to `@function_tool`
  > **Comments:**

- [ ] Convert `get_news_sentiment` to `@function_tool`
  > **Comments:**

- [ ] Convert technical indicators (RSI, MACD, Bollinger) to tools
  > **Comments:**

- [ ] Test all Alpha Vantage tools independently
  > **Comments:**

#### 1.5 Create Macro Economic Data Tools

- [ ] Research data sources for economic indicators (FRED API, Alpha Vantage economic indicators, etc.)
  > **Comments:**

- [ ] Create `src/lib/macro_api.py` - Raw API client for economic data
  > **Comments:**

- [ ] Implement fetchers for inflation data (CPI, PCE)
  > **Comments:**

- [ ] Implement fetchers for employment data (Non-Farm Payrolls, Unemployment Rate)
  > **Comments:**

- [ ] Implement fetchers for interest rates (Fed Funds, 10-yr, 2-yr Treasury)
  > **Comments:**

- [ ] Implement fetchers for GDP data
  > **Comments:**

- [ ] Implement fetchers for market indicators (VIX, S&P 500, sector ETFs)
  > **Comments:**

- [ ] Create `src/tools/macro_economic.py` with tool wrappers
  > **Comments:**

- [ ] Test all macro data fetchers independently
  > **Comments:**

#### 1.6 (Optional) SEC Filings Tool

- [ ] Research SEC EDGAR API
  > **Comments:**

- [ ] Create `src/lib/sec_api.py` if proceeding
  > **Comments:**

- [ ] Create `src/tools/sec_filings.py` with `@function_tool`
  > **Comments:**

- [ ] Test SEC filings tool
  > **Comments:**

---

### Phase 2: Output Models

#### 2.1 Qualitative Models

- [ ] Create `src/agents/__init__.py`
  > **Comments:**

- [ ] Create `src/agents/qualitative/__init__.py`
  > **Comments:**

- [ ] Create `src/agents/qualitative/models.py`
  > **Comments:**

- [ ] Define `Development` model (company developments/news items)
  > **Comments:**

- [ ] Define `ExternalFactor` model (macro, geopolitical, regulatory)
  > **Comments:**

- [ ] Define `RiskFactor` model (identified threats)
  > **Comments:**

- [ ] Define `OpportunityFactor` model (identified tailwinds)
  > **Comments:**

- [ ] Define `SentimentAnalysis` model (social/media mood)
  > **Comments:**

- [ ] Define `CompanySituationSummary` model
  > **Comments:**

- [ ] Define `QualitativeReport` model (top-level output)
  > **Comments:**

#### 2.2 Quantitative Models

- [ ] Create `src/agents/quantitative/__init__.py`
  > **Comments:**

- [ ] Create `src/agents/quantitative/models.py`
  > **Comments:**

- [ ] Define `ValuationAnalysis` model (P/E, P/B, EV/EBITDA, etc.)
  > **Comments:**

- [ ] Define `GrowthAnalysis` model (revenue, earnings trends)
  > **Comments:**

- [ ] Define `ProfitabilityAnalysis` model (margins, ROE, ROIC)
  > **Comments:**

- [ ] Define `BalanceSheetHealth` model (debt, liquidity, solvency)
  > **Comments:**

- [ ] Define `CashFlowAnalysis` model (FCF, capex, dividends)
  > **Comments:**

- [ ] Define `TechnicalAnalysis` model (price action, momentum)
  > **Comments:**

- [ ] Define `PeerComparison` model (relative positioning)
  > **Comments:**

- [ ] Define `HealthRating` enum (STRONG/GOOD/FAIR/WEAK/CRITICAL)
  > **Comments:**

- [ ] Define `QuantitativeReport` model (top-level output)
  > **Comments:**

#### 2.3 Macro Economic Models

- [ ] Create `src/agents/macro/__init__.py`
  > **Comments:**

- [ ] Create `src/agents/macro/models.py`
  > **Comments:**

- [ ] Define `InflationData` model (CPI, PCE with values and trends)
  > **Comments:**

- [ ] Define `EmploymentData` model (payrolls, unemployment rate)
  > **Comments:**

- [ ] Define `InterestRateData` model (Fed funds, 10-yr, 2-yr, yield curve status)
  > **Comments:**

- [ ] Define `GrowthData` model (GDP, quarter-over-quarter)
  > **Comments:**

- [ ] Define `MarketData` model (VIX, S&P 500 trend, sector performance)
  > **Comments:**

- [ ] Define `MacroEnvironment` enum (RISK_ON/RISK_OFF/NEUTRAL/UNCERTAIN)
  > **Comments:**

- [ ] Define `MacroReport` model (top-level output with all indicators)
  > **Comments:**

#### 2.4 Synthesis Models

- [ ] Create `src/agents/synthesis/__init__.py`
  > **Comments:**

- [ ] Create `src/agents/synthesis/models.py`
  > **Comments:**

- [ ] Define `DetailedReport` model
  > **Comments:**

- [ ] Define `SummaryReport` model
  > **Comments:**

- [ ] Define `Recommendation` enum (BUY/SELL/HOLD/AVOID)
  > **Comments:**

- [ ] Define `ConvictionLevel` enum (HIGH/MEDIUM/LOW)
  > **Comments:**

- [ ] Define `TimeHorizon` enum (SHORT/MEDIUM/LONG_TERM)
  > **Comments:**

- [ ] Define `TradeAdvice` model
  > **Comments:**

- [ ] Define `ResearchOutput` model (complete output package)
  > **Comments:**

---

### Phase 3: Agents

#### 3.1 Qualitative Research Agent

- [ ] Create `src/agents/qualitative/prompts.py` with detailed instructions
  > **Comments:**

- [ ] Create `src/agents/qualitative/agent.py`
  > **Comments:**

- [ ] Define agent with tools: web_search, x_search, news_sentiment
  > **Comments:**

- [ ] Configure agent for autonomous tool selection
  > **Comments:**

- [ ] Ensure agent focuses on quarterly context (what happened last quarter, what's expected next quarter)
  > **Comments:**

- [ ] Test qualitative agent with sample ticker
  > **Comments:**

- [ ] Tune prompts based on output quality
  > **Comments:**

#### 3.2 Quantitative Research Agent

- [ ] Create `src/agents/quantitative/prompts.py` with detailed instructions
  > **Comments:**

- [ ] Create `src/agents/quantitative/agent.py`
  > **Comments:**

- [ ] Define agent with tools: all Alpha Vantage tools
  > **Comments:**

- [ ] Configure agent for autonomous tool selection
  > **Comments:**

- [ ] Ensure agent focuses on quarterly earnings (past and next quarter)
  > **Comments:**

- [ ] Test quantitative agent with sample ticker
  > **Comments:**

- [ ] Tune prompts based on output quality
  > **Comments:**

#### 3.3 Macro Economic Report Generator

Note: This is NOT an LLM agent - it's a checklist-driven data fetcher that compiles economic indicators into a structured report.

- [ ] Create `src/agents/macro/macro_report.py`
  > **Comments:**

- [ ] Implement `fetch_inflation_data()` function
  > **Comments:**

- [ ] Implement `fetch_employment_data()` function
  > **Comments:**

- [ ] Implement `fetch_interest_rate_data()` function
  > **Comments:**

- [ ] Implement `fetch_growth_data()` function
  > **Comments:**

- [ ] Implement `fetch_market_data()` function (VIX, indices, sector)
  > **Comments:**

- [ ] Implement `determine_macro_environment()` logic (rule-based classification)
  > **Comments:**

- [ ] Implement main `generate_macro_report()` function that compiles all data
  > **Comments:**

- [ ] Add brief contextual notes for each indicator (e.g., "above/below Fed target")
  > **Comments:**

- [ ] Test macro report generation independently
  > **Comments:**

#### 3.4 Detailed Report Agent

- [ ] Create `src/agents/synthesis/detailed_report_agent.py`
  > **Comments:**

- [ ] Define agent (no tools, synthesis only)
  > **Comments:**

- [ ] Write comprehensive prompt for combining qual + quant + macro
  > **Comments:**

- [ ] Ensure prompt emphasizes quarterly earnings focus (past quarter results, next quarter expectations)
  > **Comments:**

- [ ] Test with sample qualitative, quantitative, and macro reports
  > **Comments:**

- [ ] Tune prompts for narrative quality
  > **Comments:**

#### 3.5 Summary Report Agent

- [ ] Create `src/agents/synthesis/summary_report_agent.py`
  > **Comments:**

- [ ] Define agent (no tools, condensation only)
  > **Comments:**

- [ ] Write prompt for extracting key points
  > **Comments:**

- [ ] Test with sample detailed report
  > **Comments:**

- [ ] Tune for appropriate length (~500 words)
  > **Comments:**

#### 3.6 Trade Advice Agent

- [ ] Create `src/agents/synthesis/trade_advice_agent.py`
  > **Comments:**

- [ ] Define agent (no tools, recommendation only)
  > **Comments:**

- [ ] Write prompt for actionable recommendations
  > **Comments:**

- [ ] Include guidance on conviction levels and position sizing
  > **Comments:**

- [ ] Ensure agent considers macro environment in recommendations
  > **Comments:**

- [ ] Test with sample reports
  > **Comments:**

- [ ] Tune for balanced, non-financial-advice recommendations
  > **Comments:**

---

### Phase 4: Orchestration Flow

#### 4.1 Create Autonomous Research Flow

- [ ] Create `src/flows/autonomous_flow.py`
  > **Comments:**

- [ ] Implement `run_qualitative_agent()` helper
  > **Comments:**

- [ ] Implement `run_quantitative_agent()` helper
  > **Comments:**

- [ ] Implement `generate_macro_report()` helper (calls the checklist fetcher)
  > **Comments:**

- [ ] Implement `run_detailed_report_agent()` helper
  > **Comments:**

- [ ] Implement `run_summary_report_agent()` helper
  > **Comments:**

- [ ] Implement `run_trade_advice_agent()` helper
  > **Comments:**

- [ ] Implement main `autonomous_research()` function
  > **Comments:**

- [ ] Add job status updates at each phase
  > **Comments:**

- [ ] Add error handling and graceful degradation
  > **Comments:**

- [ ] Test full flow end-to-end
  > **Comments:**

#### 4.2 Parallel Execution (Optional Enhancement)

- [ ] Evaluate running qualitative + quantitative + macro in parallel
  > **Comments:**

- [ ] Implement parallel execution if beneficial (all three pillars can run independently)
  > **Comments:**

- [ ] Test parallel vs sequential performance
  > **Comments:**

---

### Phase 5: API & Integration

#### 5.1 New API Endpoint

- [ ] Add `POST /research/autonomous` endpoint in `server/api.py`
  > **Comments:**

- [ ] Define request model (symbol, optional parameters)
  > **Comments:**

- [ ] Define response model (complete ResearchOutput)
  > **Comments:**

- [ ] Implement endpoint handler
  > **Comments:**

- [ ] Add appropriate timeouts for long-running research
  > **Comments:**

- [ ] Test endpoint via curl/Postman
  > **Comments:**

#### 5.2 Job Tracking Updates

- [ ] Update job status schema if needed for new phases
  > **Comments:**

- [ ] Implement status updates: "qualitative_research", "quantitative_research", "macro_report", "synthesizing", etc.
  > **Comments:**

- [ ] Test real-time status updates via Supabase Realtime
  > **Comments:**

#### 5.3 Caching Strategy

- [ ] Determine caching strategy for autonomous flow
  > **Comments:**

- [ ] Implement caching for qualitative report (with appropriate TTL)
  > **Comments:**

- [ ] Implement caching for quantitative report (with appropriate TTL)
  > **Comments:**

- [ ] Implement caching for macro report (shorter TTL - economic data changes frequently)
  > **Comments:**

- [ ] Consider cache invalidation triggers (e.g., new earnings release, Fed announcement)
  > **Comments:**

---

### Phase 6: Testing & Validation

#### 6.1 Unit Tests

- [ ] Write tests for all new Pydantic models
  > **Comments:**

- [ ] Write tests for tool functions
  > **Comments:**

- [ ] Write tests for agent helpers
  > **Comments:**

- [ ] Mock external APIs (web search, X, Alpha Vantage, FRED/macro data)
  > **Comments:**

#### 6.2 Integration Tests

- [ ] Test full autonomous flow with mocked APIs
  > **Comments:**

- [ ] Test with real APIs on sample tickers
  > **Comments:**

- [ ] Validate output quality and completeness
  > **Comments:**

#### 6.3 Quality Validation

- [ ] Test with 5-10 diverse tickers (tech, finance, energy, etc.)
  > **Comments:**

- [ ] Review output quality with human evaluation
  > **Comments:**

- [ ] Tune prompts based on findings
  > **Comments:**

- [ ] Document any edge cases or limitations
  > **Comments:**

---

### Phase 7: Cleanup & Documentation

#### 7.1 Code Cleanup

- [ ] Remove or archive unused legacy code (if appropriate)
  > **Comments:**

- [ ] Ensure consistent code style across new modules
  > **Comments:**

- [ ] Add type hints throughout
  > **Comments:**

#### 7.2 Documentation

- [ ] Update CLAUDE.md with new architecture
  > **Comments:**

- [ ] Document new API endpoints
  > **Comments:**

- [ ] Document environment variables for new services (X API, web search, FRED)
  > **Comments:**

- [ ] Create example usage documentation
  > **Comments:**

---

## What to Keep vs Replace

| Keep | Replace |
|------|---------|
| `src/lib/alpha_vantage_api.py` (raw API calls) | Sequential research flow logic |
| Supabase integration (jobs, cache) | Fixed 12-step pipeline |
| Job status tracking pattern | Hardcoded analysis order |
| FastAPI server structure | Existing agent definitions (eventually) |
| Token logging hooks | Existing Pydantic models (eventually) |
| `litellm` model abstraction | — |

---

## Environment Variables (New)

Add to `.env`:

```bash
# xAI API (Primary)
XAI_API_KEY=your_xai_api_key

# Web Search (choose one)
TAVILY_API_KEY=your_tavily_key  # If using Tavily
SERP_API_KEY=your_serp_key      # If using SerpAPI

# X/Twitter API
X_API_KEY=your_x_api_key
X_API_SECRET=your_x_api_secret
X_BEARER_TOKEN=your_x_bearer_token

# Macro Economic Data (choose based on implementation)
FRED_API_KEY=your_fred_api_key  # Federal Reserve Economic Data
```

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Agent makes poor research decisions | Detailed instructions, few-shot examples in prompts |
| Runaway token usage | Max turns limit, token budgets, early stopping |
| Stale macro economic data | Short cache TTL, include data timestamps in reports |
| Missing critical analysis | Minimum analysis checklist in agent instructions |
| Non-deterministic outputs | Caching, temperature=0, structured Pydantic output |
| Debugging difficulty | Verbose logging of agent decisions and tool calls |
| API rate limits | Implement rate limiting, caching, graceful degradation |
| Web search quality varies | Multiple search queries, cross-reference sources |

---

## Notes & Decisions Log

*Add any major decisions, pivots, or discoveries here as implementation progresses.*

-

---

## Completion Checklist

- [ ] Phase 1: Infrastructure complete
- [ ] Phase 2: Output models complete
- [ ] Phase 3: All agents implemented and tested
- [ ] Phase 4: Orchestration flow working end-to-end
- [ ] Phase 5: API endpoint live and functional
- [ ] Phase 6: Testing complete, quality validated
- [ ] Phase 7: Documentation updated

---

*Last Updated: 2026-01-30*
