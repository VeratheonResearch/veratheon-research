from agents import Agent
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from src.lib.llm_model import get_model

financial_statements_analysis_agent = Agent(
            name="Financial Statements Analyst",      
            model=get_model(),
            output_type=FinancialStatementsAnalysis,
            instructions="""
            Analyze recent financial statements for changes affecting near-term projection accuracy.

            ENUM REQUIREMENTS:
            - revenue_driver_trend: RevenueDriverTrend (STRENGTHENING, WEAKENING, STABLE, VOLATILE, INSUFFICIENT_DATA)
            - cost_structure_trend: CostStructureTrend (IMPROVING_EFFICIENCY, DETERIORATING_EFFICIENCY, STABLE_STRUCTURE, VOLATILE_COSTS, INSUFFICIENT_DATA)
            - working_capital_trend: WorkingCapitalTrend (IMPROVING_MANAGEMENT, DETERIORATING_MANAGEMENT, STABLE_MANAGEMENT, CASH_FLOW_CONCERNS, INSUFFICIENT_DATA)

            ANALYSIS FOCUS (last 2-3 periods):
            - Revenue drivers: Growth sources, pricing power, mix changes, new markets
            - Cost structure: COGS, SG&A, R&D as % revenue, efficiency trends, scale benefits
            - Working capital: Receivables, inventory, payables, cash conversion cycle
            - One-time items and seasonal factors affecting projections

            Identify changes that could make consensus estimates too optimistic/pessimistic.
            Include critical_insights field with 2-3 key financial changes for cross-model calibration.
        """,
        )