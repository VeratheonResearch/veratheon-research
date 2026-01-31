"""
Trade Advice Agent

Generates actionable trade ideas based on the synthesized research report.
This is ADVISORY ONLY and NOT a financial recommendation.
"""

from agents import Agent, Runner
from src.lib.llm_model import get_model


# =============================================================================
# Trade Advice Agent Prompt
# =============================================================================

TRADE_ADVICE_INSTRUCTIONS = """You are a trade strategist. Convert the synthesis report into actionable trade ideas.

**This is ADVISORY ONLY, not financial advice.**

## Output Format

Keep it tight. Traders want actionable information, not essays.

### Trade Thesis (2 sentences max)
What's the trade? Why now?

### Setup
| Direction | Conviction | Timeframe |
|-----------|------------|-----------|
| Long/Short/Neutral | High/Med/Low | Days/Weeks/Months |

### Entry & Exit
| Level | Price | Rationale |
|-------|-------|-----------|
| Entry | $XXX-XXX | [Brief reason] |
| Stop | $XXX | [Risk boundary] |
| Target 1 | $XXX | [+X% from entry] |
| Target 2 | $XXX | [If thesis fully plays out] |

### Position Sizing
- **Risk per trade**: [1-2% of portfolio max]
- **Sizing logic**: [Conservative/moderate/aggressive given conviction]

### Key Catalyst
The ONE event that matters most and when it happens.

### If Wrong
What would invalidate this trade? When to cut and reassess.

### Alternative Play
One options strategy or variant if applicable (e.g., "Sell cash-secured puts at $XXX for lower-risk entry").

---
*This is educational only. Not a recommendation. All trades involve risk.*
"""


async def run_trade_advice_agent(symbol: str, synthesis_report: str) -> str:
    """
    Generate trade advice based on the synthesis report.

    DISCLAIMER: This is advisory information only, not a financial recommendation.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        synthesis_report: Output from the synthesis agent

    Returns:
        Markdown-formatted trade advice with appropriate disclaimers
    """
    trade_advice_input = f"""Based on the following research synthesis for {symbol}, generate actionable trade ideas.

Remember: Your output is ADVISORY ONLY and NOT a financial recommendation.

## SYNTHESIS REPORT
{synthesis_report}

---

Please provide practical trade considerations for {symbol} based on this research."""

    # Create the trade advice agent
    trade_advice_agent = Agent(
        name="Trade Idea Generator",
        model=get_model(),
        instructions=TRADE_ADVICE_INSTRUCTIONS,
        tools=[],  # No tools needed - pure reasoning from synthesis
    )

    # Run the agent
    result = await Runner.run(
        trade_advice_agent,
        input=trade_advice_input,
    )

    # Prepend disclaimer to output
    disclaimer_header = """---
⚠️ **ADVISORY NOTICE**: The following trade ideas are for **educational and informational purposes only**. This is NOT financial advice or a recommendation to buy, sell, or hold any security. All investments involve risk, including potential loss of principal. Consult with a licensed financial advisor before making investment decisions.

---

"""

    return disclaimer_header + result.final_output
