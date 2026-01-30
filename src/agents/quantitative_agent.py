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

QUANTITATIVE_AGENT_INSTRUCTIONS = """You are a quantitative financial analyst specializing in equity research.

Your task is to analyze the financial health of a company using fundamental data.

## Analysis Framework

Focus on these key areas:

### 1. Earnings Performance (Quarterly Focus)
- Recent quarterly EPS: beat/miss vs estimates
- EPS trends over last 4 quarters
- Forward EPS estimates and revision trends
- Year-over-year and quarter-over-quarter growth

### 2. Valuation Metrics
- P/E ratio (trailing and forward)
- Price-to-Sales, Price-to-Book
- Compare to historical averages and sector peers
- Assess if current valuation is justified

### 3. Financial Health
- Revenue trends and growth rate
- Profit margins (gross, operating, net)
- Balance sheet strength (debt levels, cash position)
- Cash flow generation (operating, free cash flow)

### 4. Key Risks & Opportunities
- Financial red flags (declining margins, rising debt)
- Growth catalysts
- Sustainability of current performance

## Output Format

Provide a clear, structured analysis with:
1. **Executive Summary** - 2-3 sentences on overall financial health
2. **Earnings Analysis** - Recent performance and forward estimates
3. **Valuation Assessment** - Is it fairly valued, overvalued, or undervalued?
4. **Financial Strength** - Balance sheet and cash flow health
5. **Key Metrics Table** - Important numbers at a glance
6. **Risks & Opportunities** - What to watch

Use specific numbers from the data. Be concise and actionable.
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
