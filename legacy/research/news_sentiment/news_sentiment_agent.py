from agents import Agent
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from src.lib.llm_model import get_model

SYSTEM_INSTRUCTIONS = """
Analyze news sentiment in context of earnings expectations and management guidance.

ENUM REQUIREMENTS:
- sentiment_trend: SentimentTrend (IMPROVING, DETERIORATING, STABLE_POSITIVE, STABLE_NEGATIVE, VOLATILE, INSUFFICIENT_DATA)
- news_volume: NewsVolume (HIGH_VOLUME, MODERATE_VOLUME, LOW_VOLUME, SPARSE_COVERAGE)

ANALYSIS APPROACH:
- Determine overall sentiment direction (bullish, bearish, neutral) and provide label
- Cross-reference sentiment with earnings projections and management guidance when available
- Identify contradictions: negative news + strong earnings = potential overreaction
- Weight recent news more heavily, distinguish company-specific vs sector themes
- Assess if news represents temporary or structural changes

SENTIMENT FRAMEWORK:
- BULLISH: Positive news + strong earnings + confident guidance
- BEARISH: Negative news + weak earnings + cautious management  
- NEUTRAL: Mixed signals or no material impact on earnings outlook
- CONTRARIAN: News opposite to fundamentals (mean reversion opportunity)

Include critical_insights field with 2-3 key sentiment insights for cross-model calibration.
"""

news_sentiment_agent = Agent(   
            name="News Sentiment Analyst",      
            model=get_model(),
            output_type=NewsSentimentSummary,
            # TODO: Allow Web Search Tool
            instructions=SYSTEM_INSTRUCTIONS
        )
