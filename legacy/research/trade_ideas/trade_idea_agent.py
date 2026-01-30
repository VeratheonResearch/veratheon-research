from agents import Agent
from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from src.lib.llm_model import get_model

trade_idea_agent = Agent(
            name="Trade Idea Analyst",      
            model=get_model(),
            output_type=TradeIdea,
            instructions="""
            Generate trade ideas based on earnings, valuation, and sentiment analyses.

            ENUM REQUIREMENTS:
            - trade_direction: TradeDirection (LONG, SHORT, NEUTRAL, COMPLEX)
            - time_horizon: TimeHorizon (SHORT_TERM <3mo, MEDIUM_TERM 3-12mo, LONG_TERM >12mo)
            - risk_level: RiskLevel (LOW, MEDIUM, HIGH, VERY_HIGH)

            TRADE DEVELOPMENT:
            - Synthesize earnings projections, forward P/E analysis, and news sentiment
            - Consider long positions, short positions, options, and option spreads
            - Provide confidence score (0-10) - if ≤6, recommend wait-and-see
            - Include entry targets, upside targets, stop-loss levels
            - Suggest risk hedges appropriate for the position
            - Focus only on the given symbol, no other recommendations

            CRITICAL: No position sizing - that happens later in workflow.
            Include critical_insights field with 2-3 key trade insights for cross-model calibration.
        """,
        )
