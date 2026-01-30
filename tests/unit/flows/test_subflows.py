import pytest
from unittest.mock import patch, AsyncMock
from legacy.flows.subflows.historical_earnings_flow import historical_earnings_flow
from legacy.flows.subflows.earnings_projections_flow import earnings_projections_flow
from legacy.flows.subflows.financial_statements_flow import financial_statements_flow
from legacy.flows.subflows.management_guidance_flow import management_guidance_flow
from legacy.research.historical_earnings.historical_earnings_models import (
    HistoricalEarningsData,
    HistoricalEarningsAnalysis
)
from legacy.research.earnings_projections.earnings_projections_models import (
    EarningsProjectionData,
    EarningsProjectionAnalysis,
    NextQuarterProjection
)
from legacy.research.financial_statements.financial_statements_models import (
    FinancialStatementsData,
    FinancialStatementsAnalysis
)
from legacy.research.management_guidance.management_guidance_models import (
    ManagementGuidanceData,
    ManagementGuidanceAnalysis
)


class TestHistoricalEarningsFlow:
    
    @patch('src.flows.subflows.historical_earnings_flow.historical_earnings_reporting_task')
    @patch('src.flows.subflows.historical_earnings_flow.historical_earnings_analysis_task')
    @patch('src.flows.subflows.historical_earnings_flow.historical_earnings_fetch_task')
    @patch('src.flows.subflows.historical_earnings_flow.historical_earnings_cache_retrieval_task')
    @pytest.mark.anyio
    async def test_historical_earnings_flow_success(
        self, 
        mock_cache_task,
        mock_fetch_task,
        mock_analysis_task,
        mock_reporting_task
    ):
        """Test successful historical earnings flow execution."""
        
        # Mock cache task to return None (no cached data)
        mock_cache_task.return_value = None
        
        # Mock fetch task result
        mock_data = HistoricalEarningsData(
            symbol="AAPL",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            annual_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "10.00"}],
            income_statement=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000"}]
        )
        mock_fetch_task.return_value = mock_data
        
        # Mock analysis task result
        mock_analysis = HistoricalEarningsAnalysis(
            symbol="AAPL",
            earnings_pattern="CONSISTENT_BEATS",
            earnings_pattern_details="Company consistently beats estimates by 5-10%",
            revenue_growth_trend="STABLE",
            revenue_growth_details="Revenue growth averaging 8-12% annually",
            margin_trend="IMPROVING",
            margin_trend_details="Operating margins expanding from 25% to 30%",
            key_insights=["Strong pricing power", "Operational efficiency gains"],
            analysis_confidence_score=85,
            predictability_score=90,
            long_form_analysis="Strong historical performance with consistent beats",
            critical_insights="Company shows strong fundamental strength"
        )
        mock_analysis_task.return_value = mock_analysis
        
        # Mock reporting task
        mock_reporting_task.return_value = None
        
        # Execute the flow
        result = await historical_earnings_flow("AAPL")
        
        # Verify the result
        assert isinstance(result, HistoricalEarningsAnalysis)
        assert result.symbol == "AAPL"
        assert result.earnings_pattern == "CONSISTENT_BEATS"
        
        # Verify tasks were called correctly
        mock_fetch_task.assert_called_once_with("AAPL")
        mock_analysis_task.assert_called_once_with("AAPL", mock_data)
        mock_reporting_task.assert_called_once_with("AAPL", mock_analysis)


class TestEarningsProjectionsFlow:
    
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_reporting_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_analysis_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_fetch_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_cache_retrieval_task')
    @pytest.mark.anyio
    async def test_earnings_projections_flow_success(
        self,
        mock_cache_task,
        mock_fetch_task,
        mock_analysis_task,
        mock_reporting_task
    ):
        """Test successful earnings projections flow execution."""
        
        # Mock cache task to return None (no cached data)
        mock_cache_task.return_value = None
        
        # Mock fetch task result
        mock_data = EarningsProjectionData(
            symbol="AAPL",
            quarterly_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000"}],
            annual_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "400000000"}],
            overview_data={"Symbol": "AAPL", "Name": "Apple Inc."},
            historical_earnings_analysis={"pattern": "CONSISTENT_BEATS"},
            financial_statements_analysis={"trend": "IMPROVING"}
        )
        mock_fetch_task.return_value = mock_data
        
        # Mock analysis task result
        next_quarter = NextQuarterProjection(
            # Revenue Projection
            projected_revenue=56000000.0,
            revenue_projection_method="HISTORICAL_TREND",
            revenue_reasoning="Strong historical growth pattern",
            
            # Cost Projections  
            projected_cogs=30000000.0,
            cogs_projection_method="PERCENTAGE_OF_REVENUE",
            cogs_reasoning="Stable cost structure",
            projected_gross_profit=26000000.0,
            projected_gross_margin=0.464,
            
            # Operating Expense Projections
            projected_sga=15000000.0,
            sga_reasoning="Based on historical trends",
            projected_rd=5000000.0,
            rd_reasoning="Consistent R&D investment",
            projected_total_opex=20000000.0,
            
            # Bottom Line Projections
            projected_operating_income=6000000.0,
            projected_operating_margin=0.107,
            projected_interest_expense=200000.0,
            projected_tax_expense=1400000.0,
            projected_tax_rate=0.25,
            projected_net_income=4400000.0,
            projected_eps=2.65,
            
            # Comparison with Consensus
            consensus_eps_estimate=2.50,
            eps_vs_consensus_diff=0.15,
            eps_vs_consensus_percent=6.0
        )
        mock_analysis = EarningsProjectionAnalysis(
            symbol="AAPL",
            next_quarter_projection=next_quarter,
            projection_methodology="Analysis based on revenue growth trends and historical patterns",
            key_assumptions=["Revenue growth continues at 8-10%", "Margins remain stable", "No major one-time items"],
            upside_risks=["Better than expected product sales", "Cost efficiencies"],
            downside_risks=["Economic slowdown", "Supply chain disruptions"],
            data_quality_score=85,
            consensus_validation_summary="Our projection is 6% above consensus, driven by stronger revenue outlook",
            long_form_analysis="Detailed analysis shows strong fundamentals supporting higher than consensus earnings",
            critical_insights="Strong fundamentals support above-consensus earnings potential"
        )
        mock_analysis_task.return_value = mock_analysis
        
        # Mock reporting task
        mock_reporting_task.return_value = None
        
        # Execute the flow with context
        historical_context = {"pattern": "CONSISTENT_BEATS"}
        financial_context = {"trend": "IMPROVING"}
        result = await earnings_projections_flow("AAPL", historical_context, financial_context)
        
        # Verify the result
        assert isinstance(result, EarningsProjectionAnalysis)
        assert result.symbol == "AAPL"
        assert result.next_quarter_projection.projected_eps == 2.65
        
        # Verify tasks were called correctly
        mock_fetch_task.assert_called_once_with("AAPL", historical_context, financial_context)
        mock_analysis_task.assert_called_once_with("AAPL", mock_data)
        mock_reporting_task.assert_called_once_with("AAPL", mock_analysis)

    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_reporting_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_analysis_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_fetch_task')
    @patch('src.flows.subflows.earnings_projections_flow.earnings_projections_cache_retrieval_task')
    @pytest.mark.anyio
    async def test_earnings_projections_flow_no_context(
        self,
        mock_cache_task,
        mock_fetch_task,
        mock_analysis_task,
        mock_reporting_task
    ):
        """Test earnings projections flow without historical context."""
        
        # Mock cache task to return None (no cached data)
        mock_cache_task.return_value = None
        
        # Mock minimal fetch task result
        mock_data = EarningsProjectionData(
            symbol="AAPL",
            quarterly_income_statements=[],
            annual_income_statements=[],
            overview_data={},
            historical_earnings_analysis=None,
            financial_statements_analysis=None
        )
        mock_fetch_task.return_value = mock_data
        
        # Mock minimal analysis task result
        next_quarter = NextQuarterProjection(
            # Revenue Projection
            projected_revenue=55000000.0,
            revenue_projection_method="HISTORICAL_TREND",
            revenue_reasoning="Limited historical data available",
            
            # Cost Projections  
            projected_cogs=30000000.0,
            cogs_projection_method="PERCENTAGE_OF_REVENUE",
            cogs_reasoning="Basic cost assumptions",
            projected_gross_profit=25000000.0,
            projected_gross_margin=0.45,
            
            # Operating Expense Projections
            projected_sga=15000000.0,
            sga_reasoning="Based on basic assumptions",
            projected_rd=5000000.0,
            rd_reasoning="Basic R&D assumptions",
            projected_total_opex=20000000.0,
            
            # Bottom Line Projections
            projected_operating_income=5000000.0,
            projected_operating_margin=0.091,
            projected_interest_expense=100000.0,
            projected_tax_expense=1200000.0,
            projected_tax_rate=0.25,
            projected_net_income=3700000.0,
            projected_eps=2.50,
            
            # Comparison with Consensus
            consensus_eps_estimate=2.40,
            eps_vs_consensus_diff=0.10,
            eps_vs_consensus_percent=4.2
        )
        mock_analysis = EarningsProjectionAnalysis(
            symbol="AAPL",
            next_quarter_projection=next_quarter,
            projection_methodology="Limited data analysis with basic assumptions",
            key_assumptions=["Basic financial trends", "Simple extrapolation method"],
            upside_risks=["Potential upside surprises"],
            downside_risks=["Limited visibility"],
            data_quality_score=60,
            consensus_validation_summary="Limited consensus comparison available",
            long_form_analysis="Analysis based on limited historical data",
            critical_insights="Limited historical data constrains projection confidence"
        )
        mock_analysis_task.return_value = mock_analysis
        
        # Mock reporting task
        mock_reporting_task.return_value = None
        
        # Execute the flow without context
        result = await earnings_projections_flow("AAPL")
        
        # Verify the result
        assert isinstance(result, EarningsProjectionAnalysis)
        assert result.symbol == "AAPL"
        assert result.data_quality_score == 60
        
        # Verify tasks were called correctly
        mock_fetch_task.assert_called_once_with("AAPL", None, None)
        mock_analysis_task.assert_called_once_with("AAPL", mock_data)
        mock_reporting_task.assert_called_once_with("AAPL", mock_analysis)


class TestFinancialStatementsFlow:
    
    @patch('src.flows.subflows.financial_statements_flow.financial_statements_reporting_task')
    @patch('src.flows.subflows.financial_statements_flow.financial_statements_analysis_task')
    @patch('src.flows.subflows.financial_statements_flow.financial_statements_fetch_task')
    @patch('src.flows.subflows.financial_statements_flow.financial_statements_cache_retrieval_task')
    @pytest.mark.anyio
    async def test_financial_statements_flow_success(
        self,
        mock_cache_task,
        mock_fetch_task,
        mock_analysis_task,
        mock_reporting_task
    ):
        """Test successful financial statements flow execution."""
        
        # Mock cache task to return None (no cached data)
        mock_cache_task.return_value = None
        
        # Mock fetch task result
        mock_data = FinancialStatementsData(
            symbol="AAPL",
            income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000", "netIncome": "20000000"}],
            balance_sheets=[{"fiscalDateEnding": "2023-12-31", "totalAssets": "500000000"}],
            cash_flow_statements=[{"fiscalDateEnding": "2023-12-31", "operatingCashflow": "30000000"}]
        )
        mock_fetch_task.return_value = mock_data
        
        # Mock analysis task result
        mock_analysis = FinancialStatementsAnalysis(
            symbol="AAPL",
            revenue_driver_trend="STRENGTHENING",
            revenue_driver_details="Product demand driving revenue growth",
            cost_structure_trend="IMPROVING_EFFICIENCY", 
            cost_structure_details="Operating leverage improving margins",
            working_capital_trend="IMPROVING_MANAGEMENT",
            working_capital_details="Efficient cash conversion cycle",
            key_financial_changes=["Revenue growth acceleration", "Margin expansion"],
            near_term_projection_risks=["Economic slowdown risk"],
            analysis_confidence_score=85,
            data_quality_score=90,
            long_form_analysis="Strong financial performance with improving trends",
            critical_insights="Financial performance trends support positive outlook"
        )
        mock_analysis_task.return_value = mock_analysis
        
        # Mock reporting task
        mock_reporting_task.return_value = None
        
        # Execute the flow
        result = await financial_statements_flow("AAPL")
        
        # Verify the result
        assert isinstance(result, FinancialStatementsAnalysis)
        assert result.symbol == "AAPL"
        assert result.revenue_driver_trend == "STRENGTHENING"
        
        # Verify tasks were called correctly
        mock_fetch_task.assert_called_once_with("AAPL")
        mock_analysis_task.assert_called_once_with("AAPL", mock_data)
        mock_reporting_task.assert_called_once_with("AAPL", mock_analysis)


class TestManagementGuidanceFlow:
    
    @patch('src.flows.subflows.management_guidance_flow.management_guidance_reporting_task')
    @patch('src.flows.subflows.management_guidance_flow.management_guidance_analysis_task')
    @patch('src.flows.subflows.management_guidance_flow.management_guidance_fetch_task')
    @patch('src.flows.subflows.management_guidance_flow.management_guidance_cache_retrieval_task')
    @pytest.mark.anyio
    async def test_management_guidance_flow_success(
        self,
        mock_cache_task,
        mock_fetch_task,
        mock_analysis_task,
        mock_reporting_task
    ):
        """Test successful management guidance flow execution."""
        
        # Mock cache task to return None (no cached data)
        mock_cache_task.return_value = None
        
        # Mock fetch task result
        mock_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"quarterlyEstimates": [{"fiscalDateEnding": "2024-06-30", "estimatedEPS": "2.50"}]},
            earnings_transcript={"transcript": "Management provided positive guidance for the next quarter with strong revenue outlook and continued margin expansion..."},
            quarter="2024Q1"
        )
        mock_fetch_task.return_value = mock_data
        
        # Mock analysis task result
        mock_analysis = ManagementGuidanceAnalysis(
            symbol="AAPL",
            quarter_analyzed="2024Q1",
            transcript_available=True,
            guidance_indicators=[],
            overall_guidance_tone="OPTIMISTIC",
            risk_factors_mentioned=["Supply chain constraints"],
            opportunities_mentioned=["New product launches", "Market expansion"],
            revenue_guidance_direction="POSITIVE",
            margin_guidance_direction="NEUTRAL",
            eps_guidance_direction="POSITIVE",
            consensus_validation_signal="BULLISH",
            key_guidance_summary="Strong forward guidance provided for next quarter",
            long_form_analysis="Management provided positive outlook with specific growth drivers",
            critical_insights="Management guidance aligns with positive fundamental outlook"
        )
        mock_analysis_task.return_value = mock_analysis
        
        # Mock reporting task
        mock_reporting_task.return_value = None
        
        # Mock context data
        historical_context = HistoricalEarningsAnalysis(
            symbol="AAPL",
            earnings_pattern="CONSISTENT_BEATS",
            earnings_pattern_details="Company consistently beats estimates by 5-10%",
            revenue_growth_trend="STABLE",
            revenue_growth_details="Revenue growth averaging 8-12% annually",
            margin_trend="IMPROVING",
            margin_trend_details="Operating margins expanding from 25% to 30%",
            key_insights=["Strong pricing power", "Operational efficiency gains"],
            analysis_confidence_score=85,
            predictability_score=90,
            long_form_analysis="Strong historical performance with consistent beats",
            critical_insights="Consistent historical performance indicates strong execution"
        )
        financial_context = FinancialStatementsAnalysis(
            symbol="AAPL",
            revenue_driver_trend="STRENGTHENING",
            revenue_driver_details="Strong product sales growth driving revenue",
            cost_structure_trend="STABLE_STRUCTURE",
            cost_structure_details="Consistent cost management and operating leverage",
            working_capital_trend="IMPROVING_MANAGEMENT",
            working_capital_details="Efficient working capital management",
            key_financial_changes=["Revenue acceleration", "Margin stability"],
            near_term_projection_risks=["Market competition risk"],
            analysis_confidence_score=85,
            data_quality_score=90,
            long_form_analysis="Strong financial performance with improving trends",
            critical_insights="Improving financial trends support growth trajectory"
        )
        
        # Execute the flow
        result = await management_guidance_flow(
            "AAPL", 
            historical_context, 
            financial_context
        )
        
        # Verify the result
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.overall_guidance_tone == "OPTIMISTIC"
        
        # Verify tasks were called correctly
        mock_fetch_task.assert_called_once_with("AAPL")
        mock_analysis_task.assert_called_once_with(
            "AAPL", 
            mock_data,
            historical_context,
            financial_context
        )
        mock_reporting_task.assert_called_once_with("AAPL", mock_analysis)
