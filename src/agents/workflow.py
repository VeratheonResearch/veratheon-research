"""
Veratheon Research Autonomous Workflow

Main entry point for the three-pillar research workflow:
- Quantitative Agent: Financial health analysis
- Qualitative Agent: News and sentiment analysis
- Macro Report: Economic indicators (no LLM)
- Synthesis Agent: Combines all into unified report
- Trade Advice Agent: Generates actionable trade ideas (advisory only)
"""

import asyncio
from dataclasses import dataclass
from typing import Optional, Union

from src.agents.quantitative_agent import run_quantitative_analysis
from src.agents.qualitative_agent import run_qualitative_analysis
from src.agents.macro_report import fetch_macro_report as fetch_macro_data, MacroReport
from src.agents.synthesis_agent import run_synthesis_agent as run_synthesis
from src.agents.trade_advice_agent import run_trade_advice_agent as run_trade_advice
from src.lib.clients.alpha_vantage_client import AlphaVantageClient


@dataclass
class WorkflowResult:
    """Result from the autonomous research workflow."""
    symbol: str
    quantitative_report: Optional[str] = None
    qualitative_report: Optional[str] = None
    macro_report: Optional[Union[MacroReport, dict]] = None
    synthesis_report: Optional[str] = None
    trade_advice: Optional[str] = None
    error: Optional[str] = None


async def run_quantitative_agent(symbol: str) -> str:
    """
    Run the quantitative research agent.
    Analyzes financial health using Alpha Vantage data.
    """
    return await run_quantitative_analysis(symbol)


async def run_qualitative_agent(symbol: str) -> str:
    """
    Run the qualitative research agent.
    Researches news and sentiment via xAI web search and X search.
    """
    return await run_qualitative_analysis(symbol)


async def get_company_sector(symbol: str) -> Optional[str]:
    """
    Fetch the company's sector from Alpha Vantage overview.
    Used to get sector-specific ETF performance in macro report.
    """
    try:
        client = AlphaVantageClient()
        data = await asyncio.to_thread(
            client.run_query,
            f"OVERVIEW&symbol={symbol}"
        )
        return data.get("Sector")
    except Exception:
        return None


async def fetch_macro_report(sector: Optional[str] = None) -> MacroReport:
    """
    Fetch macro economic indicators.
    This is a data lookup, not an LLM call.

    Args:
        sector: Optional company sector for sector-specific ETF data

    Returns:
        MacroReport with all economic indicators
    """
    return await fetch_macro_data(sector=sector)


async def run_synthesis_agent(
    symbol: str,
    quantitative: str,
    qualitative: str,
    macro: Union[MacroReport, dict]
) -> str:
    """
    Run the synthesis agent to combine all reports.

    Args:
        symbol: Stock ticker symbol
        quantitative: Quantitative analysis report
        qualitative: Qualitative analysis report
        macro: Macro economic report (MacroReport or dict)

    Returns:
        Synthesized research report
    """
    return await run_synthesis(
        symbol=symbol,
        quantitative_report=quantitative,
        qualitative_report=qualitative,
        macro_report=macro,
    )


async def run_autonomous_workflow(symbol: str) -> WorkflowResult:
    """
    Execute the full autonomous research workflow for a stock symbol.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        WorkflowResult containing all reports and analysis
    """
    symbol = symbol.upper().strip()
    result = WorkflowResult(symbol=symbol)

    try:
        # First, get the company's sector for macro report (quick API call)
        sector = await get_company_sector(symbol)

        # Phase 1: Run quantitative and qualitative agents in parallel
        # (Macro can also run in parallel since it's just data fetching)
        quant_task = asyncio.create_task(run_quantitative_agent(symbol))
        qual_task = asyncio.create_task(run_qualitative_agent(symbol))
        macro_task = asyncio.create_task(fetch_macro_report(sector=sector))

        # Wait for all to complete
        result.quantitative_report = await quant_task
        result.qualitative_report = await qual_task
        result.macro_report = await macro_task

        # Phase 2: Synthesize all reports
        result.synthesis_report = await run_synthesis_agent(
            symbol=symbol,
            quantitative=result.quantitative_report,
            qualitative=result.qualitative_report,
            macro=result.macro_report
        )

        # Phase 3: Generate trade advice based on synthesis
        result.trade_advice = await run_trade_advice(
            symbol=symbol,
            synthesis_report=result.synthesis_report
        )

    except Exception as e:
        result.error = str(e)

    return result


def format_workflow_result(result: WorkflowResult) -> str:
    """Format the workflow result for display."""
    lines = [
        f"{'='*60}",
        f"VERATHEON RESEARCH REPORT: {result.symbol}",
        f"{'='*60}",
        "",
    ]

    if result.error:
        lines.append(f"ERROR: {result.error}")
        return "\n".join(lines)

    # Format macro report
    macro_str = "Not available"
    if result.macro_report:
        if isinstance(result.macro_report, MacroReport):
            macro_str = result.macro_report.format_report()
        else:
            macro_str = str(result.macro_report)

    lines.extend([
        "QUANTITATIVE ANALYSIS",
        "-" * 40,
        result.quantitative_report or "Not available",
        "",
        "QUALITATIVE ANALYSIS",
        "-" * 40,
        result.qualitative_report or "Not available",
        "",
        "MACRO ECONOMIC CONTEXT",
        "-" * 40,
        macro_str,
        "",
        "SYNTHESIS",
        "-" * 40,
        result.synthesis_report or "Not available",
        "",
        "TRADE IDEAS (ADVISORY ONLY)",
        "-" * 40,
        result.trade_advice or "Not available",
        "",
        "=" * 60,
    ])

    return "\n".join(lines)
