import pytest
from unittest.mock import patch, AsyncMock
from legacy.tasks.historical_earnings.historical_earnings_fetch_task import historical_earnings_fetch_task
from legacy.tasks.historical_earnings.historical_earnings_analysis_task import historical_earnings_analysis_task
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsData, HistoricalEarningsAnalysis
from agents import RunResult


class TestHistoricalEarningsFetchTask:
    
    @patch('src.tasks.historical_earnings.historical_earnings_fetch_task.get_historical_earnings_data_for_symbol')
    @pytest.mark.anyio
    async def test_historical_earnings_fetch_task_success(self, mock_get_data):
        """Test successful historical earnings data fetch."""
        # Mock the utility function response
        mock_data = HistoricalEarningsData(
            symbol="AAPL",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            annual_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "10.00"}],
            income_statement=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000"}]
        )
        mock_get_data.return_value = mock_data
        
        result = await historical_earnings_fetch_task("AAPL")
        
        assert isinstance(result, HistoricalEarningsData)
        assert result.symbol == "AAPL"
        assert len(result.quarterly_earnings) == 1
        assert len(result.annual_earnings) == 1
        assert len(result.income_statement) == 1
        mock_get_data.assert_called_once_with("AAPL")


class TestHistoricalEarningsAnalysisTask:

    @patch('src.tasks.historical_earnings.historical_earnings_analysis_task.Runner.run')
    @pytest.mark.anyio
    async def test_historical_earnings_analysis_task_success(self, mock_runner):
        """Test successful historical earnings analysis."""
        # Mock historical data
        historical_data = HistoricalEarningsData(
            symbol="AAPL",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            annual_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "10.00"}],
            income_statement=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000"}]
        )
        
        # Mock the agent response
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
            critical_insights="Consistent beat pattern indicates strong management execution"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_analysis})()
        mock_runner.return_value = mock_result
        
        result = await historical_earnings_analysis_task("AAPL", historical_data)
        
        assert isinstance(result, HistoricalEarningsAnalysis)
        assert result.symbol == "AAPL"
        assert result.earnings_pattern == "CONSISTENT_BEATS"
        assert result.revenue_growth_trend == "STABLE"
        assert result.margin_trend == "IMPROVING"
        mock_runner.assert_called_once()