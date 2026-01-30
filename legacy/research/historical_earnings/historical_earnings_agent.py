from agents import Agent
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from src.lib.llm_model import get_model

historical_earnings_analysis_agent = Agent(
            name="Historical Earnings Analyst",      
            model=get_model(),
            output_type=HistoricalEarningsAnalysis,
            instructions="""
            Analyze historical earnings patterns to establish baseline performance for future validation.

            ENUM REQUIREMENTS:
            - earnings_pattern: EarningsPattern (CONSISTENT_BEATS, CONSISTENT_MISSES, MIXED_PATTERN, VOLATILE, INSUFFICIENT_DATA)
            - revenue_growth_trend: RevenueGrowthTrend (ACCELERATING, DECELERATING, STABLE, DECLINING, VOLATILE, INSUFFICIENT_DATA) 
            - margin_trend: MarginTrend (IMPROVING, DETERIORATING, STABLE, VOLATILE, INSUFFICIENT_DATA)

            ANALYSIS FOCUS:
            - Beat/miss patterns vs consensus estimates with percentages and frequencies
            - Revenue growth trends (QoQ, YoY) and seasonal patterns
            - Margin trends (gross, operating, net) and sustainability
            - Earnings quality and predictability indicators
            
            Include critical_insights field with 2-3 key patterns for cross-model calibration.
        """,
        )