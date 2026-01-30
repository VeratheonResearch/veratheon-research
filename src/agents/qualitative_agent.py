"""
Qualitative Research Agent

Researches what's happening with a company using xAI's web search and X search tools.
Focuses on news, sentiment, management commentary, and company-specific events.
"""

import os
from typing import Optional
from openai import OpenAI

# Environment toggle for web search (expensive operation)
# Set ENABLE_WEB_SEARCH=True in .env to enable (accepts: True, true, 1)
# Default: True (enabled)
_web_search_env = os.getenv("ENABLE_WEB_SEARCH", "True")
ENABLE_WEB_SEARCH = _web_search_env in ("True", "true", "1")

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

QUALITATIVE_AGENT_INSTRUCTIONS = """You are a qualitative research analyst specializing in company research.

Your task is to research what's happening with a company - the actual business events, news, and developments that affect the investment thesis.

## Research Framework

Focus on these key areas:

### 1. Recent News & Developments
- Major news stories in the past 30 days
- Product launches, acquisitions, partnerships
- Regulatory actions or legal issues
- Management changes or executive commentary

### 2. Market Sentiment
- How is the market reacting to recent news?
- What are analysts saying?
- Social media sentiment and buzz

### 3. Upcoming Catalysts
- Earnings date and expectations
- Product announcements or events
- Regulatory decisions pending
- Conference appearances or investor days

### 4. Risks & Concerns
- Negative news or concerns being discussed
- Competitive threats
- Regulatory or geopolitical risks
- Supply chain or operational issues

### 5. Company Narrative
- What story is the company telling?
- Management guidance and tone
- Strategic direction and priorities

## Output Format

Provide a clear, structured analysis with:
1. **Executive Summary** - 2-3 sentences on the current situation
2. **Recent Developments** - Key news and events (with dates where available)
3. **Market Sentiment** - How the market views the company right now
4. **Upcoming Catalysts** - What to watch for
5. **Key Risks** - Material concerns to be aware of
6. **Notable Social/X Posts** - Relevant insights from X (if found)

Be specific and cite sources where possible. Focus on recent, material information.
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
    # Check if web search is disabled
    if not ENABLE_WEB_SEARCH:
        return _get_disabled_message(symbol)

    if not XAI_API_KEY:
        return f"[Qualitative analysis for {symbol} unavailable - XAI_API_KEY not configured]"

    client = get_xai_client()

    # Build the research query
    user_query = f"""Research what's happening with {symbol} (the company, not just the stock).

Focus on:
1. Recent news and developments (last 30 days)
2. What people are saying on X/Twitter about the company
3. Upcoming earnings or events
4. Any concerns or risks being discussed
5. Management commentary or guidance

Provide a comprehensive qualitative analysis."""

    # Configure xAI server-side tools
    tools = [
        {"type": "web_search"},
        {"type": "x_search"},
    ]

    try:
        # Call xAI responses API with search tools
        response = client.responses.create(
            model="grok-4-1-fast",
            instructions=QUALITATIVE_AGENT_INSTRUCTIONS,
            input=[{"role": "user", "content": user_query}],
            tools=tools,
        )

        # Extract the output text from the response
        output_text = _extract_response_text(response)

        if not output_text:
            return f"[Qualitative analysis for {symbol} - no results returned]"

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
    """Return a message when web search is disabled."""
    return f"""## Qualitative Analysis for {symbol}

**Web search is currently disabled.**

To enable web search, set in your `.env` file:
```
ENABLE_WEB_SEARCH=True
```

Note: Web search uses xAI's server-side tools which incur additional API costs.
"""
