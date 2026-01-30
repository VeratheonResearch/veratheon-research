import pytest
from unittest.mock import patch
from legacy.tasks.earnings_projections.earnings_projections_fetch_task import earnings_projections_fetch_task
from legacy.tasks.earnings_projections.earnings_projections_analysis_task import earnings_projections_analysis_task
from legacy.research.earnings_projections.earnings_projections_models import (
    EarningsProjectionData, 
    EarningsProjectionAnalysis,
    NextQuarterProjection
)
from agents import RunResult


class TestEarningsProjectionsFetchTask:
    
    @patch('src.tasks.earnings_projections.earnings_projections_fetch_task.get_earnings_projection_data_for_symbol')
    @pytest.mark.anyio
    async def test_earnings_projections_fetch_task_success(self, mock_get_data):
        """Test successful earnings projections data fetch."""
        # Mock the utility function response
        mock_data = EarningsProjectionData(
            symbol="AAPL",
            quarterly_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "50000000"}],
            annual_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "200000000"}],
            overview_data={"MarketCapitalization": "3000000000000", "PERatio": "25.0"},
            historical_earnings_analysis=None,
            financial_statements_analysis=None
        )
        mock_get_data.return_value = mock_data
        
        result = await earnings_projections_fetch_task(
            "AAPL", 
            historical_earnings_analysis={"pattern": "CONSISTENT_BEATS"}, 
            financial_statements_analysis={"trend": "IMPROVING"}
        )
        
        assert isinstance(result, EarningsProjectionData)
        assert result.symbol == "AAPL"
        assert len(result.quarterly_income_statements) == 1
        assert len(result.annual_income_statements) == 1
        mock_get_data.assert_called_once_with("AAPL", {"pattern": "CONSISTENT_BEATS"}, {"trend": "IMPROVING"})

    @patch('src.tasks.earnings_projections.earnings_projections_fetch_task.get_earnings_projection_data_for_symbol')
    @pytest.mark.anyio
    async def test_earnings_projections_fetch_task_no_context(self, mock_get_data):
        """Test earnings projections fetch without historical context."""
        mock_data = EarningsProjectionData(
            symbol="AAPL",
            quarterly_income_statements=[],
            annual_income_statements=[],
            overview_data={},
            historical_earnings_analysis=None,
            financial_statements_analysis=None
        )
        mock_get_data.return_value = mock_data
        
        result = await earnings_projections_fetch_task("AAPL")
        
        assert isinstance(result, EarningsProjectionData)
        assert result.symbol == "AAPL"
        mock_get_data.assert_called_once_with("AAPL", None, None)


class TestEarningsProjectionsAnalysisTask:
    
    @patch('src.tasks.earnings_projections.earnings_projections_analysis_task.Runner.run')
    @pytest.mark.anyio
    async def test_earnings_projections_analysis_task_success(self, mock_runner):
        """Test successful earnings projections analysis."""
        # Mock projection data
        projection_data = EarningsProjectionData(
            symbol="AAPL",
            quarterly_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "50000000"}],
            annual_income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "200000000"}],
            overview_data={"MarketCapitalization": "3000000000000", "PERatio": "25.0"},
            historical_earnings_analysis=None,
            financial_statements_analysis=None
        )
        
        # Mock the agent response
        next_quarter = NextQuarterProjection(
            # Revenue Projection
            projected_revenue=56000000.0,
            revenue_projection_method="HISTORICAL_TREND",
            revenue_confidence="HIGH",
            revenue_reasoning="Strong historical growth pattern",
            
            # Cost Projections  
            projected_cogs=30000000.0,
            cogs_projection_method="PERCENTAGE_OF_REVENUE",
            cogs_confidence="HIGH", 
            cogs_reasoning="Stable cost structure",
            projected_gross_profit=26000000.0,
            projected_gross_margin=0.464,
            
            # Operating Expense Projections
            projected_sga=15000000.0,
            sga_confidence="MEDIUM",
            sga_reasoning="Based on historical trends",
            projected_rd=5000000.0,
            rd_confidence="HIGH",
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
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_analysis})()
        mock_runner.return_value = mock_result
        
        result = await earnings_projections_analysis_task("AAPL", projection_data)
        
        assert isinstance(result, EarningsProjectionAnalysis)
        assert result.symbol == "AAPL"
        assert result.next_quarter_projection.projected_eps == 2.65
        assert result.next_quarter_projection.projected_revenue == 56000000.0
        assert result.data_quality_score == 85
        mock_runner.assert_called_once()