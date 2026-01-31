"""
Quantitative Research Agent

Analyzes the financial health of a company using Alpha Vantage data.
Focuses on quarterly earnings, financial statements, and key metrics.
"""

from typing import Dict, Any
from agents import Agent, function_tool, Runner
from src.lib.llm_model import get_model
from src.lib.clients.alpha_vantage_client import AlphaVantageClient

# Initialize Alpha Vantage client
_av_client = AlphaVantageClient()


# =============================================================================
# Alpha Vantage Tools for Quantitative Analysis
# =============================================================================

@function_tool
def get_company_overview(symbol: str) -> Dict[str, Any]:
    """Get company overview and key financial metrics.

    Returns company description, sector, industry, market cap, P/E ratio,
    EPS, dividend yield, 52-week range, and other fundamental metrics.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Company overview data including valuation ratios and key metrics
    """
    return _av_client.run_query(f"OVERVIEW&symbol={symbol}")


@function_tool
def get_income_statement(symbol: str) -> Dict[str, Any]:
    """Get annual and quarterly income statements.

    Returns revenue, cost of revenue, gross profit, operating income,
    net income, and other income statement line items.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Annual and quarterly income statements (typically 5 years/quarters)
    """
    return _av_client.run_query(f"INCOME_STATEMENT&symbol={symbol}")


@function_tool
def get_balance_sheet(symbol: str) -> Dict[str, Any]:
    """Get annual and quarterly balance sheets.

    Returns total assets, liabilities, shareholders equity, cash,
    debt, and other balance sheet items.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Annual and quarterly balance sheets (typically 5 years/quarters)
    """
    return _av_client.run_query(f"BALANCE_SHEET&symbol={symbol}")


@function_tool
def get_cash_flow(symbol: str) -> Dict[str, Any]:
    """Get annual and quarterly cash flow statements.

    Returns operating cash flow, investing cash flow, financing cash flow,
    capital expenditures, and free cash flow.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Annual and quarterly cash flow statements (typically 5 years/quarters)
    """
    return _av_client.run_query(f"CASH_FLOW&symbol={symbol}")


@function_tool
def get_earnings(symbol: str) -> Dict[str, Any]:
    """Get historical earnings per share (EPS) data.

    Returns reported EPS, estimated EPS, surprise, and surprise percentage
    for historical earnings periods.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Annual and quarterly EPS data with beat/miss information
    """
    return _av_client.run_query(f"EARNINGS&symbol={symbol}")


@function_tool
def get_earnings_estimates(symbol: str) -> Dict[str, Any]:
    """Get analyst earnings estimates for upcoming quarters.

    Returns consensus EPS estimates, number of analysts, and revision trends
    for future reporting periods.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Forward-looking earnings estimates from analysts
    """
    return _av_client.run_query(f"EARNINGS_ESTIMATES&symbol={symbol}")


@function_tool
def get_global_quote(symbol: str) -> Dict[str, Any]:
    """Get the latest price and trading information.

    Returns current price, open, high, low, volume, previous close,
    and daily change information.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Real-time (delayed) quote data for the latest trading day
    """
    return _av_client.run_query(f"GLOBAL_QUOTE&symbol={symbol}")


# =============================================================================
# Quantitative Agent Definition
# =============================================================================

QUANTITATIVE_AGENT_INSTRUCTIONS = """You are a quantitative financial analyst. Your job is to assess the financial health of a company with a **quarterly earnings lens**.

## Core Questions to Answer

1. **Last Quarter**: Did they beat or miss? By how much? What drove the result?
2. **Next Quarter**: What are analysts expecting? Are estimates rising or falling?
3. **Valuation**: Is the current price justified given earnings trajectory?
4. **Financial Strength**: Can the company sustain/grow earnings?

## Analysis Approach

### 1. Quarterly Earnings (PRIMARY FOCUS)
- **Last 4 quarters**: EPS actual vs estimate, surprise %, beat/miss streak
- **Next quarter estimate**: Consensus EPS, # of analysts, recent revisions (up/down)
- **Trend**: Is earnings power improving, stable, or deteriorating?

### 2. Valuation Context
- Trailing P/E, Forward P/E, PEG ratio (if available)
- Compare to sector average (tech ~25-30x, industrials ~15-20x, utilities ~15x)
- Is premium/discount justified by growth rate?
- Analyst price targets vs current price

### 3. Financial Fundamentals
- Revenue growth (YoY and QoQ)
- Margin trends (gross, operating) - improving or compressing?
- Balance sheet: Net cash or net debt? Debt/Equity ratio?
- Free cash flow yield

### 4. Key Risks
- Margin compression signals
- Estimate revisions trending down
- High debt with rising rates
- Revenue concentration

## Output Format

Be concise. Investors want signal, not noise.

### One-Line Thesis
Single sentence: What's the financial story?

### Quarterly Scorecard
| Metric | Last Q | vs Est | Trend |
|--------|--------|--------|-------|
| EPS | $X.XX | +X% beat | ↑/↓/→ |
| Revenue | $XB | +X% beat | ↑/↓/→ |

### Next Quarter Setup
- Consensus EPS: $X.XX
- Estimates trending: Up/Down/Flat (X revisions last 30 days)
- Key driver to watch: [specific item]

### Valuation Verdict
- Current: X.Xx P/E (vs sector Xx P/E)
- Forward: X.Xx P/E on FY estimates
- Assessment: [Cheap/Fair/Rich] given [growth rate/quality]

### Financial Health Check
- Margins: [Expanding/Stable/Compressing]
- Balance Sheet: [Net cash $XB / Net debt $XB, X.Xx leverage]
- FCF Yield: X.X%

### Key Numbers
| Metric | Value | Context |
|--------|-------|---------|
| Market Cap | $XB | |
| Revenue TTM | $XB | +X% YoY |
| Net Margin | X% | vs X% prior year |
| ROE | X% | |
| Analyst Target | $XXX | +X% upside |

### Watch List
Bullet points of specific risks or catalysts from the numbers.

Use actual data. Flag if key data is unavailable. Skip sections with no relevant data.
"""

# Create the quantitative agent with tools
quantitative_agent = Agent(
    name="Quantitative Analyst",
    model=get_model(),
    instructions=QUANTITATIVE_AGENT_INSTRUCTIONS,
    tools=[
        get_company_overview,
        get_income_statement,
        get_balance_sheet,
        get_cash_flow,
        get_earnings,
        get_earnings_estimates,
        get_global_quote,
    ],
)


async def run_quantitative_analysis(symbol: str) -> str:
    """
    Run the quantitative analysis agent for a given stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Markdown-formatted quantitative analysis report
    """
    result = await Runner.run(
        quantitative_agent,
        input=f"Analyze the financial health of {symbol}. Use the available tools to gather data, then provide a comprehensive quantitative analysis.",
    )
    return result.final_output
