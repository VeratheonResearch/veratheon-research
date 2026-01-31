"""
Qualitative Research Agent

Researches what's happening with a company using xAI's web search and X search tools.
Focuses on news, sentiment, management commentary, and company-specific events.
"""

import os
from typing import Optional
from openai import OpenAI

# Environment toggles for search capabilities
# Both are expensive API operations - control separately if needed
#
# ENABLE_WEB_SEARCH: General web search for news, articles, press releases
# Set ENABLE_WEB_SEARCH=True in .env to enable (accepts: True, true, 1)
# Default: True (enabled)
_web_search_env = os.getenv("ENABLE_WEB_SEARCH", "True")
ENABLE_WEB_SEARCH = _web_search_env in ("True", "true", "1")

# ENABLE_X_SEARCH: X/Twitter search for real-time sentiment, influencer takes, breaking news
# Provides unique value through:
# - Real-time market sentiment and reactions
# - Influencer/analyst commentary with engagement metrics
# - Breaking news often ahead of traditional media
# - Social proof signals (likes, retweets)
# Set ENABLE_X_SEARCH=True in .env to enable (accepts: True, true, 1)
# Default: True (enabled) - follows ENABLE_WEB_SEARCH if not explicitly set
_x_search_env = os.getenv("ENABLE_X_SEARCH")
if _x_search_env is not None:
    ENABLE_X_SEARCH = _x_search_env in ("True", "true", "1")
else:
    # Default: follow web search setting for backwards compatibility
    ENABLE_X_SEARCH = ENABLE_WEB_SEARCH

# xAI API configuration
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_BASE_URL = "https://api.x.ai/v1"

# Initialize xAI client (OpenAI SDK with xAI base URL)
_xai_client: Optional[OpenAI] = None


def get_xai_client() -> OpenAI:
    """Get or create the xAI client."""
    global _xai_client
    if _xai_client is None:
        if not XAI_API_KEY:
            raise ValueError("XAI_API_KEY environment variable is required")
        _xai_client = OpenAI(
            api_key=XAI_API_KEY,
            base_url=XAI_BASE_URL,
        )
    return _xai_client


# =============================================================================
# Qualitative Agent Prompt
# =============================================================================

QUALITATIVE_AGENT_INSTRUCTIONS = """You are a qualitative research analyst. Your job is to answer: **What's actually happening with this company?**

Not stock price movements—the actual business. What would a board member or competitor want to know?

## Core Questions to Answer

1. **Last Quarter**: What happened? Any surprises? How did management explain results?
2. **Right Now**: What's the current narrative? Any breaking news or emerging issues?
3. **Next Quarter**: What catalysts are coming? What could cause a beat or miss?
4. **Risks**: What are the bears saying? What could go wrong?

## Search Strategy

### Priority Searches (do these first)
1. "[Company] earnings" - Get the last earnings story and guidance
2. "[Company] news" - Recent headlines (last 30 days)
3. "[Company] analyst" - Wall Street reactions and rating changes

### Secondary Searches (if time permits)
4. "[Company] CEO/CFO" - Management commentary
5. "[Company] competition" or "[Company] market share" - Competitive dynamics
6. "[Company] risk" or "[Company] concern" - Bear cases
7. "$[TICKER]" on X - Real-time sentiment and breaking news

## Source Credibility

**Trust more**: SEC filings, earnings transcripts, Reuters, Bloomberg, WSJ, FT, company press releases
**Trust less**: Blog posts, promotional content, anonymous sources
**Flag speculation**: Clearly label rumors vs confirmed news

## Output Format

Be concise and actionable. Lead with the most important findings.

### The Story in 30 Seconds
2-3 sentences: What's the narrative right now? What would you tell someone at a dinner party?

### Last Quarter Recap
- **Result**: Beat/miss by X%, revenue $XB
- **Management tone**: Confident/cautious/concerned
- **Key quote**: "[Actual quote from earnings call if available]"
- **Guidance**: Raised/lowered/maintained for next quarter

### What's Happening Now
Bullet points of material news from last 30 days:
- [Date] Event/headline (source)
- Focus on: Product launches, partnerships, executive changes, lawsuits, regulatory news

### Upcoming Catalysts
| Event | Expected Date | Why It Matters |
|-------|---------------|----------------|
| Earnings | ~[Date] | [Key thing to watch] |
| [Product/Event] | [Date] | [Impact] |

### Sentiment Check
- **Analysts**: X Buy / X Hold / X Sell, recent changes
- **Social/X buzz**: [Brief summary of tone - bullish/bearish/mixed]
- **Notable voices**: Any influential commentators weighing in?

### Risk Radar
What bears are focused on:
- [Risk 1]: [Why it matters]
- [Risk 2]: [Why it matters]

### Key Quotes
Include 1-2 verbatim quotes from management, analysts, or notable X posts that capture the current narrative.

Cite sources. Include dates. Flag uncertainty clearly.
"""


async def run_qualitative_analysis(symbol: str) -> str:
    """
    Run the qualitative analysis agent for a given stock symbol.

    Uses xAI's web_search and x_search server-side tools to research
    recent news, sentiment, and company developments.

    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')

    Returns:
        Markdown-formatted qualitative analysis report
    """
    # Check if all search capabilities are disabled
    if not ENABLE_WEB_SEARCH and not ENABLE_X_SEARCH:
        return _get_disabled_message(symbol)

    if not XAI_API_KEY:
        return f"[Qualitative analysis for {symbol} unavailable - XAI_API_KEY not configured]"

    client = get_xai_client()

    # Build the research query based on enabled search types
    focus_items = ["Recent news and developments (last 30 days)"]
    if ENABLE_X_SEARCH:
        focus_items.append("What people are saying on X/Twitter about the company")
    focus_items.extend([
        "Upcoming earnings or events",
        "Any concerns or risks being discussed",
        "Management commentary or guidance",
    ])

    focus_list = "\n".join(f"{i+1}. {item}" for i, item in enumerate(focus_items))

    user_query = f"""Research what's happening with {symbol} (the company, not just the stock).

Focus on:
{focus_list}

Provide a comprehensive qualitative analysis."""

    # Configure xAI server-side tools based on enabled capabilities
    tools = []
    if ENABLE_WEB_SEARCH:
        tools.append({"type": "web_search"})
    if ENABLE_X_SEARCH:
        tools.append({"type": "x_search"})

    # Adjust instructions based on available tools
    instructions = QUALITATIVE_AGENT_INSTRUCTIONS
    if not ENABLE_X_SEARCH:
        # Remove X/Twitter references from output format
        instructions = instructions.replace(
            "6. **Notable Social/X Posts** - Relevant insights from X (if found)",
            "6. **Additional Context** - Any other relevant insights"
        )

    try:
        # Call xAI responses API with search tools
        response = client.responses.create(
            model="grok-4-1-fast",
            instructions=instructions,
            input=[{"role": "user", "content": user_query}],
            tools=tools,
        )

        # Extract the output text from the response
        output_text = _extract_response_text(response)

        if not output_text:
            return f"[Qualitative analysis for {symbol} - no results returned]"

        # Add note about partial search capability if applicable
        if not ENABLE_WEB_SEARCH:
            output_text = f"*Note: Analysis based on social media sources only - traditional news sources temporarily unavailable*\n\n{output_text}"
        elif not ENABLE_X_SEARCH:
            output_text = f"*Note: Analysis based on web sources only - social media sentiment temporarily unavailable*\n\n{output_text}"

        return output_text

    except Exception as e:
        error_msg = str(e)
        # Provide helpful error messages
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return f"[Qualitative analysis for {symbol} failed - Invalid XAI_API_KEY]"
        elif "429" in error_msg or "rate" in error_msg.lower():
            return f"[Qualitative analysis for {symbol} failed - Rate limit exceeded]"
        else:
            return f"[Qualitative analysis for {symbol} failed - {error_msg}]"


def _extract_response_text(response) -> str:
    """
    Extract the text content from an xAI responses API response.

    The response object structure may vary, so we handle multiple formats.
    """
    # Try to get output_text directly (common response format)
    if hasattr(response, 'output_text') and response.output_text:
        return response.output_text

    # Try to get from output array
    if hasattr(response, 'output') and response.output:
        text_parts = []
        for item in response.output:
            if hasattr(item, 'content') and item.content:
                # Handle content array
                if isinstance(item.content, list):
                    for content_item in item.content:
                        if hasattr(content_item, 'text'):
                            text_parts.append(content_item.text)
                elif isinstance(item.content, str):
                    text_parts.append(item.content)
        if text_parts:
            return "\n".join(text_parts)

    # Try choices format (OpenAI-style)
    if hasattr(response, 'choices') and response.choices:
        choice = response.choices[0]
        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
            return choice.message.content

    # Fallback: convert to string
    return str(response)


def _get_disabled_message(symbol: str) -> str:
    """Return a message when all search capabilities are disabled."""
    return f"""## Qualitative Analysis for {symbol}

**Qualitative research is temporarily disabled.**

Live news and sentiment analysis are currently unavailable. Quantitative analysis and macro economic data remain available for your research.
"""
