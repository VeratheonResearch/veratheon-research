"""
Synthesis Agent

Combines quantitative, qualitative, and macro economic reports into a unified
research report with actionable insights.
"""

from typing import Union
from agents import Agent, Runner
from src.lib.llm_model import get_model
from src.agents.macro_report import MacroReport


# =============================================================================
# Synthesis Agent Prompt
# =============================================================================

SYNTHESIS_AGENT_INSTRUCTIONS = """You are a senior investment research analyst synthesizing multiple research inputs into a unified investment report.

You have been provided with three research inputs:
1. **Quantitative Analysis** - Financial metrics, earnings, valuation, and fundamental data
2. **Qualitative Analysis** - News, sentiment, management commentary, and company events
3. **Macro Economic Context** - Economic indicators, interest rates, and market conditions

## Your Task

Synthesize these three perspectives into a cohesive investment narrative that answers:
- What is the complete picture for this investment?
- How do the quantitative, qualitative, and macro factors interact?
- What is the overall risk/reward profile?

## Synthesis Framework

### 1. Cross-Reference Analysis
- Do the fundamentals support the narrative? (e.g., strong earnings but negative sentiment - why?)
- Are there contradictions between data and news? (e.g., stock down but fundamentals strong)
- How does the macro environment affect this specific company?

### 2. Key Questions to Address
- Is the current valuation justified given the qualitative factors?
- How does the macro environment (rates, growth) impact this company's outlook?
- What are the key risks that span multiple categories?
- What catalysts could change the investment thesis?

### 3. Time Horizon Considerations
- Near-term (next quarter): What's the setup for the next earnings?
- Medium-term (6-12 months): How do trends and catalysts play out?

## Output Format

Provide a comprehensive research report with these sections:

### Executive Summary
2-3 sentences capturing the complete investment picture. Include the key insight from synthesizing all three perspectives.

### The Complete Picture
A narrative (3-4 paragraphs) that weaves together:
- The fundamental story (from quantitative)
- What's happening with the company (from qualitative)
- The broader context (from macro)
Explain how these factors interact and reinforce or contradict each other.

### Key Insights
Bullet points of the most important takeaways that only emerge from combining all three analyses:
- Insights that require understanding both fundamentals AND news
- How macro conditions specifically affect this company
- Contradictions or confirmations between data sources

### Risk Assessment
Categorize risks by severity and timeframe:
- **High Priority**: Risks that require immediate attention
- **Monitor**: Risks to watch but not immediate concerns
- **Macro Headwinds/Tailwinds**: How the environment helps or hurts

### Catalysts & Timing
- Upcoming events that could move the stock
- Key dates (earnings, product launches, Fed meetings)
- What to watch for

### Investment Conclusion
A clear, synthesized view:
- Overall assessment (Bullish/Neutral/Bearish)
- Confidence level (High/Medium/Low) based on data quality and alignment
- Key factors that would change this assessment
- What type of investor this is suitable for (growth, value, income, etc.)

## Guidelines

- Be objective - acknowledge both positives and negatives
- Highlight where the three analyses agree (high conviction) vs. conflict (uncertainty)
- Focus on actionable insights, not just summarizing each report
- Use specific data points to support conclusions
- Be direct about unknowns and data limitations
"""


async def run_synthesis_agent(
    symbol: str,
    quantitative_report: str,
    qualitative_report: str,
    macro_report: Union[MacroReport, dict, str],
) -> str:
    """
    Run the synthesis agent to combine all research reports.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        quantitative_report: Output from the quantitative agent
        qualitative_report: Output from the qualitative agent
        macro_report: MacroReport object, dict, or formatted string

    Returns:
        Markdown-formatted synthesis report
    """
    # Format macro report if it's a MacroReport object
    if isinstance(macro_report, MacroReport):
        macro_text = macro_report.format_report()
    elif isinstance(macro_report, dict):
        macro_text = _format_macro_dict(macro_report)
    else:
        macro_text = str(macro_report)

    # Build the synthesis prompt with all three reports
    synthesis_input = f"""Synthesize the following research on {symbol} into a unified investment report.

## QUANTITATIVE ANALYSIS
{quantitative_report}

---

## QUALITATIVE ANALYSIS
{qualitative_report}

---

## MACRO ECONOMIC CONTEXT
{macro_text}

---

Please provide a comprehensive synthesis that combines all three perspectives into actionable investment intelligence for {symbol}."""

    # Create the synthesis agent
    synthesis_agent = Agent(
        name="Synthesis Analyst",
        model=get_model(),
        instructions=SYNTHESIS_AGENT_INSTRUCTIONS,
        tools=[],  # No tools needed - synthesis is pure reasoning
    )

    # Run the agent
    result = await Runner.run(
        synthesis_agent,
        input=synthesis_input,
    )

    return result.final_output


def _format_macro_dict(macro_dict: dict) -> str:
    """Format a macro report dictionary as readable text."""
    lines = ["MACRO ECONOMIC INDICATORS", "=" * 50, ""]

    # Inflation
    if "inflation" in macro_dict:
        lines.append("INFLATION")
        for key, val in macro_dict["inflation"].items():
            if val and val.get("value"):
                lines.append(f"  {val.get('name', key)}: {val['value']}")
        lines.append("")

    # Employment
    if "employment" in macro_dict:
        lines.append("EMPLOYMENT")
        for key, val in macro_dict["employment"].items():
            if val and val.get("value"):
                lines.append(f"  {val.get('name', key)}: {val['value']}")
        lines.append("")

    # Interest Rates
    if "interest_rates" in macro_dict:
        lines.append("INTEREST RATES")
        for key, val in macro_dict["interest_rates"].items():
            if val and val.get("value"):
                lines.append(f"  {val.get('name', key)}: {val['value']}%")
        lines.append("")

    # Growth
    if "growth" in macro_dict:
        lines.append("ECONOMIC GROWTH")
        for key, val in macro_dict["growth"].items():
            if val and val.get("value"):
                lines.append(f"  {val.get('name', key)}: {val['value']}")
        lines.append("")

    # Market
    if "market" in macro_dict:
        lines.append("MARKET INDICATORS")
        for key, val in macro_dict["market"].items():
            if val and val.get("price"):
                change = f" ({val.get('change_percent', '')})" if val.get("change_percent") else ""
                lines.append(f"  {val.get('name', key)}: ${val['price']}{change}")
        lines.append("")

    return "\n".join(lines)
