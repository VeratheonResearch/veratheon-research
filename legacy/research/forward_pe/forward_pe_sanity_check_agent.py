from agents import Agent
from legacy.research.forward_pe.forward_pe_models import ForwardPeSanityCheck
from src.lib.llm_model import get_model

forward_pe_sanity_check_agent = Agent(
            name="Forward P/E Sanity Check Analyst",      
            model=get_model(),
            output_type=ForwardPeSanityCheck,
            instructions="""
            Perform consensus EPS and forward P/E sanity check against historical patterns.

            ENUM REQUIREMENTS:
            - earnings_data_quality: EarningsQuality (HIGH_QUALITY, ADEQUATE_QUALITY, QUESTIONABLE_QUALITY, POOR_QUALITY)
            - consensus_reliability: ValuationConfidence (HIGH, MEDIUM, LOW, INSUFFICIENT_DATA)
            - realistic: ForwardPeSanityCheckRealistic (REALISTIC, PLAUSIBLE, NOT_REALISTIC)

            SANITY CHECK FOCUS:
            - Compare forward P/E to historical P/E ranges and valuation patterns
            - Assess if consensus EPS is reasonable given historical earnings volatility
            - Check if current price movements align with historical earnings reactions
            - Evaluate data completeness and reliability for accurate analysis

            Include critical_insights field with 2-3 key data quality insights for cross-model calibration.
        """,
        )
