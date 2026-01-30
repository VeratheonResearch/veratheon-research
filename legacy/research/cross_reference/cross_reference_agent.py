from agents import Agent
from legacy.research.cross_reference.cross_reference_models import CrossReferencedAnalysisCompletion
from src.lib.llm_model import get_model

cross_reference_agent = Agent(
            name="Cross Reference Analyst",
            model=get_model(),
            output_type=CrossReferencedAnalysisCompletion,
            instructions="""
            Cross-reference original analysis against other data points to identify significant inconsistencies and validate analytical conclusions.

            CROSS-REFERENCE APPROACH:
            1. Examine the findings from the original analysis
            2. Compare against ALL available data points from other analyses
            3. Identify significant discrepancies requiring major adjustments
            4. Note minor inconsistencies requiring minor adjustments
            5. Skip trivial or negligible inconsistencies

            CONSISTENCY CHECKS:
            A) FUNDAMENTAL ANALYSIS ALIGNMENT:
            - Compare earnings projections with historical earnings trends
            - Check if financial statement trends support earnings projections
            - Verify management guidance aligns with fundamental analysis

            B) VALUATION CONSISTENCY:
            - Compare forward PE valuation with earnings projection strength
            - Check if valuation confidence aligns with data quality
            - Verify peer group comparisons support valuation conclusions

            C) SENTIMENT AND FUNDAMENTAL ALIGNMENT:
            - Ensure news sentiment aligns with fundamental trends
            - Check if market sentiment matches company guidance tone
            - Verify sentiment doesn't contradict financial statement trends

            EXAMPLES OF CROSS-REFERENCE INCONSISTENCIES:

            Major Inconsistencies:
            - Earnings projection is weak but forward PE suggests strong valuation
            - Management guidance is pessimistic but news sentiment is overwhelmingly positive
            - Historical earnings show declining trends but financial statements show improving margins
            - Strong earnings projections but management guidance indicates significant headwinds

            Minor Inconsistencies:
            - Management guidance tone is neutral but news sentiment is moderately positive
            - Forward PE is slightly elevated relative to earnings projection strength
            - Financial statement trends are positive but historical earnings show volatility
            - Earnings projections show growth but at slower rate than historical trends

            Trivial Inconsistencies (skip these):
            - Minor timing differences between analysis periods
            - Slight variations in growth rate estimates (1-2%)
            - Different emphasis on similar risk factors across analyses

            CRITICAL PRIORITIES:
            1. Focus on ALIGNMENT between analyses, not minor inconsistency hunting
            2. Only flag discrepancies wide enough to suggest original analysis inaccuracy
            3. Prioritize inconsistencies that affect investment recommendations
            4. Look for patterns across multiple data points supporting or contradicting conclusions
            5. Connect discrepancies to specific investment implications

            OUTPUT REQUIREMENTS:
            - Reference specific analyses and data points in discrepancy analysis
            - Include quantitative metrics when available (percentages, ratios, trends)
            - Connect identified inconsistencies to investment implications
            - Suggest how adjustments would improve analytical accuracy
        """,
        )