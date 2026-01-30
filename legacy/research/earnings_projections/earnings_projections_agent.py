from agents import Agent
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from src.lib.llm_model import get_model

earnings_projections_analysis_agent = Agent(
            name="Independent Earnings Projections Analyst",      
            model=get_model(),
            output_type=EarningsProjectionAnalysis,
            instructions="""
            Create independent next-quarter earnings projections to validate consensus estimates.

            ENUM REQUIREMENTS:
            - revenue_projection_method: RevenueProjectionMethod (HISTORICAL_TREND, SEASONAL_ADJUSTMENT, GROWTH_RATE_EXTRAPOLATION, MIXED_METHODOLOGY)
            - cogs_projection_method: CostProjectionMethod (MARGIN_BASED, PERCENTAGE_OF_REVENUE, HISTORICAL_TREND, MIXED_METHODOLOGY)  

            PROJECTION APPROACH:
            - Revenue: Historical trends + seasonal patterns + recent growth trajectory
            - COGS: Margin-based using historical patterns + recent efficiency changes
            - OpEx (SG&A, R&D): % of revenue based on historical ratios + cost management trends
            - Bottom line: Operating income → tax rate → EPS using current share count
            - Compare independent EPS vs consensus to identify validation concerns

            Include critical_insights field with 2-3 key projection insights for cross-model calibration.
        """,
        )