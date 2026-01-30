from agents import Agent
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from src.lib.llm_model import get_model

forward_pe_analysis_agent = Agent(
            name="Forward P/E Analyst",      
            model=get_model(),
            output_type=ForwardPeValuation,
            instructions="""
            Analyze forward P/E valuation for original symbol using peer group context.

            ANALYSIS FOCUS:
            - Calculate forward P/E ratio using current price and consensus EPS
            - Compare to peer group forward P/E ratios for relative valuation
            - Assess earnings quality and sustainability for valuation reliability
            - Determine if valuation is attractive relative to fundamentals and peers
            - Provide confidence score (0-10) based on data quality and analysis reliability
        """,
        )
