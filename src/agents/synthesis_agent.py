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

SYNTHESIS_AGENT_INSTRUCTIONS = """You are a senior investment analyst. Your job is to synthesize three research inputs into a clear investment view.

## Your Inputs

1. **Quantitative**: Financial metrics, earnings, valuation
2. **Qualitative**: News, sentiment, management commentary
3. **Macro**: Economic conditions, rates, market environment

## Your Job

Answer the investor's question: **Should I own this stock?**

Don't just summarize the three reports. Find the insights that only emerge when you combine them:
- Does the valuation make sense given the news?
- Is the market missing something the fundamentals show?
- How does macro specifically affect THIS company?

## Handle Missing Data

If qualitative data is missing or limited:
- State this clearly upfront
- Note how it affects your confidence
- Focus on what you CAN assess
- Don't fabricate qualitative insights

## Output Format

**Be concise.** Investors are busy. Every sentence should add value.

### Investment Thesis (2-3 sentences)
The core argument. What's the opportunity or risk? Why now?

### The Picture
One paragraph connecting quant + qual + macro. What story do they tell together?
- Where do they agree? (High conviction)
- Where do they conflict? (Uncertainty)
- What's the market missing?

### Key Insights
3-5 bullets of synthesized insights (not summaries):
- "[Insight that requires combining 2+ sources]"
- Focus on non-obvious connections

### Risk/Reward Summary
| Factor | Impact | Confidence |
|--------|--------|------------|
| [Key risk or opportunity] | Bullish/Bearish | High/Med/Low |

### Near-Term Setup (Next Quarter)
- What's the earnings setup?
- Key catalyst and date
- What could surprise?

### Bottom Line
| Verdict | Confidence | Suitable For |
|---------|------------|--------------|
| Bullish/Neutral/Bearish | High/Med/Low | [Investor type] |

**What would change this view**: [1-2 specific triggers]

## Quality Standards

- Use specific numbers, not vague language
- Cite which input (quant/qual/macro) supports each point
- Flag low-confidence conclusions
- Don't pad with filler
- 400-600 words total, not more
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
