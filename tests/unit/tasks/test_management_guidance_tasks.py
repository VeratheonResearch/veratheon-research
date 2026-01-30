import pytest
from unittest.mock import patch, AsyncMock
from legacy.tasks.management_guidance.management_guidance_fetch_task import management_guidance_fetch_task
from legacy.tasks.management_guidance.management_guidance_analysis_task import management_guidance_analysis_task
from legacy.research.management_guidance.management_guidance_models import (
    ManagementGuidanceData, 
    ManagementGuidanceAnalysis
)


class TestManagementGuidanceFetchTask:
    
    @patch('src.tasks.management_guidance.management_guidance_fetch_task.get_management_guidance_data_for_symbol')
    @pytest.mark.anyio
    async def test_management_guidance_fetch_task_success(self, mock_get_data):
        """Test successful management guidance data fetch."""
        # Mock the utility function response
        mock_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"next_quarter_eps": "2.50", "next_quarter_revenue": "55000000"},
            earnings_transcript={"transcript": "Management provided positive guidance for next quarter..."},
            quarter="2023Q4"
        )
        mock_get_data.return_value = mock_data
        
        result = await management_guidance_fetch_task("AAPL")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "AAPL"
        assert result.quarter == "2023Q4"
        assert result.earnings_transcript is not None
        mock_get_data.assert_called_once_with("AAPL")

    @patch('src.tasks.management_guidance.management_guidance_fetch_task.get_management_guidance_data_for_symbol')
    @pytest.mark.anyio
    async def test_management_guidance_fetch_task_no_transcript(self, mock_get_data):
        """Test management guidance fetch without transcript."""
        mock_data = ManagementGuidanceData(
            symbol="INVALID",
            earnings_estimates={},
            earnings_transcript=None,
            quarter="2023Q4"
        )
        mock_get_data.return_value = mock_data
        
        result = await management_guidance_fetch_task("INVALID")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "INVALID"
        assert result.earnings_transcript is None
        mock_get_data.assert_called_once_with("INVALID")


class TestManagementGuidanceAnalysisTask:
    
    @patch('src.tasks.management_guidance.management_guidance_analysis_task.management_guidance_agent')
    @pytest.mark.anyio
    async def test_management_guidance_analysis_task_success(self, mock_agent):
        """Test successful management guidance analysis."""
        # Mock guidance data
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"next_quarter_eps": "2.50", "next_quarter_revenue": "55000000"},
            earnings_transcript={"transcript": "Management provided positive guidance for next quarter..."},
            quarter="2023Q4"
        )
        
        # Mock the agent response
        mock_analysis = ManagementGuidanceAnalysis(
            symbol="AAPL",
            quarter_analyzed="2023Q4",
            transcript_available=True,
            guidance_indicators=[],
            overall_guidance_tone="OPTIMISTIC",
            risk_factors_mentioned=["Economic uncertainty"],
            opportunities_mentioned=["New product launches", "Market expansion"],
            revenue_guidance_direction="POSITIVE",
            margin_guidance_direction="NEUTRAL",
            eps_guidance_direction="POSITIVE",
            guidance_confidence="HIGH",
            consensus_validation_signal="BULLISH",
            key_guidance_summary="Strong forward guidance with positive outlook",
            long_form_analysis="Management expressed high confidence in upcoming quarters",
            critical_insights="Management guidance signals strong confidence in execution"
        )
        
        mock_agent.return_value = mock_analysis
        
        result = await management_guidance_analysis_task(
            "AAPL", 
            guidance_data,
            historical_earnings_analysis={"pattern": "CONSISTENT_BEATS"},
            financial_statements_analysis={"trend": "IMPROVING"}
        )
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available is True
        assert result.overall_guidance_tone == "OPTIMISTIC"
        assert len(result.opportunities_mentioned) == 2
        assert len(result.risk_factors_mentioned) == 1
        mock_agent.assert_called_once()

    @patch('src.tasks.management_guidance.management_guidance_analysis_task.management_guidance_agent')
    @pytest.mark.anyio
    async def test_management_guidance_analysis_task_no_context(self, mock_agent):
        """Test management guidance analysis without historical context."""
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={},
            earnings_transcript={"transcript": "Basic guidance provided..."},
            quarter="2023Q4"
        )
        
        mock_analysis = ManagementGuidanceAnalysis(
            symbol="AAPL",
            quarter_analyzed="2023Q4",
            transcript_available=True,
            guidance_indicators=[],
            overall_guidance_tone="NEUTRAL",
            risk_factors_mentioned=[],
            opportunities_mentioned=[],
            guidance_confidence="MEDIUM",
            consensus_validation_signal="NEUTRAL",
            key_guidance_summary="Standard guidance provided without specific details",
            long_form_analysis="Limited forward-looking statements in transcript",
            critical_insights="Limited guidance reduces forward visibility and confidence"
        )
        
        mock_agent.return_value = mock_analysis
        
        result = await management_guidance_analysis_task("AAPL", guidance_data)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.overall_guidance_tone == "NEUTRAL"
        mock_agent.assert_called_once_with("AAPL", guidance_data, None, None)