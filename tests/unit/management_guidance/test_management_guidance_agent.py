"""Tests for management guidance agent."""

import pytest
from unittest.mock import patch, AsyncMock
from legacy.research.management_guidance.management_guidance_agent import (
    management_guidance_agent,
    _extract_transcript_content,
    _create_no_transcript_analysis,
    _create_error_analysis
)
from legacy.research.management_guidance.management_guidance_models import (
    ManagementGuidanceData,
    ManagementGuidanceAnalysis,
    GuidanceIndicator
)


class TestManagementGuidanceAgent:
    
    def test_extract_transcript_content_direct_key(self):
        """Test transcript content extraction with direct key."""
        transcript_data = {
            "transcript": "This is the earnings call transcript content that is long enough to meet the minimum character requirement for the function to process it properly and return the content."
        }
        
        result = _extract_transcript_content(transcript_data)
        assert "This is the earnings call transcript content" in result
    
    def test_extract_transcript_content_alternative_keys(self):
        """Test transcript content extraction with alternative keys."""
        transcript_data = {
            "content": "This is the content that is long enough to meet the minimum character requirement for the function to process it properly and return the content."
        }
        
        result = _extract_transcript_content(transcript_data)
        assert "This is the content" in result
    
    def test_extract_transcript_content_nested_structure(self):
        """Test transcript content extraction with structured format."""
        transcript_data = {
            "transcript": [
                {
                    "speaker": "CEO",
                    "title": "Chief Executive Officer",
                    "content": "Thank you for joining us today. Our Q4 results demonstrate strong operational performance."
                },
                {
                    "speaker": "CFO", 
                    "title": "Chief Financial Officer",
                    "content": "Revenue grew 15% year-over-year, and we maintained strong margins."
                }
            ]
        }
        
        result = _extract_transcript_content(transcript_data)
        assert "CEO (Chief Executive Officer): Thank you for joining us today" in result
        assert "CFO (Chief Financial Officer): Revenue grew 15%" in result
    
    def test_extract_transcript_content_empty(self):
        """Test transcript content extraction with empty data."""
        transcript_data = {}
        result = _extract_transcript_content(transcript_data)
        assert result == ""
    
    def test_create_no_transcript_analysis(self):
        """Test creation of analysis when no transcript is available."""
        result = _create_no_transcript_analysis("AAPL")
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == False
        assert result.quarter_analyzed is None
        assert result.consensus_validation_signal == "NEUTRAL"
        assert "No earnings call transcript available" in result.key_guidance_summary
    
    def test_create_error_analysis(self):
        """Test creation of analysis when an error occurs."""
        error_msg = "API connection failed"
        result = _create_error_analysis("AAPL", error_msg)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == False
        assert result.consensus_validation_signal == "NEUTRAL"
        assert error_msg in result.key_guidance_summary
        assert error_msg in result.long_form_analysis
    
    @pytest.mark.anyio
    async def test_management_guidance_agent_no_transcript(self):
        """Test agent when no transcript is available."""
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"quarterlyEstimates": []},
            earnings_transcript=None,
            quarter=None
        )
        
        result = await management_guidance_agent("AAPL", guidance_data)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == False
        assert result.consensus_validation_signal == "NEUTRAL"
    
    @pytest.mark.anyio
    @patch('src.research.management_guidance.management_guidance_agent.Runner.run')
    async def test_management_guidance_agent_with_transcript(self, mock_runner):
        """Test agent with valid transcript data."""
        # Mock ManagementGuidanceAnalysis response
        mock_analysis = ManagementGuidanceAnalysis(
            symbol="AAPL",
            quarter_analyzed="2024Q1",
            transcript_available=True,
            guidance_indicators=[
                GuidanceIndicator(
                    type="revenue",
                    direction="POSITIVE",
                    context="Management expects strong iPhone sales next quarter",
                    impact_assessment="Positive impact on Q2 revenue growth"
                )
            ],
            overall_guidance_tone="OPTIMISTIC",
            risk_factors_mentioned=["Supply chain constraints"],
            opportunities_mentioned=["New product launches", "Market expansion"],
            revenue_guidance_direction="POSITIVE",
            margin_guidance_direction="NEUTRAL",
            eps_guidance_direction="POSITIVE",
            consensus_validation_signal="BULLISH",
            key_guidance_summary="Management provided bullish guidance for next quarter with strong revenue outlook",
            long_form_analysis="Overall positive tone with specific revenue growth drivers mentioned",
            critical_insights="Management guidance signals strong confidence in near-term performance"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_analysis})()
        mock_runner.return_value = mock_result
        
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={
                "quarterlyEstimates": [
                    {"fiscalDateEnding": "2024-06-30", "estimatedEPS": 2.50}
                ]
            },
            earnings_transcript={"transcript": "This is a sample earnings call transcript with management guidance that is long enough to be processed correctly by the extraction function..."},
            quarter="2024Q1"
        )
        
        result = await management_guidance_agent("AAPL", guidance_data)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == True
        assert result.quarter_analyzed == "2024Q1"
        assert result.overall_guidance_tone == "OPTIMISTIC"
        assert result.consensus_validation_signal == "BULLISH"
        assert len(result.guidance_indicators) == 1
        assert result.guidance_indicators[0].type == "revenue"
        assert result.guidance_indicators[0].direction == "POSITIVE"
        assert "Supply chain constraints" in result.risk_factors_mentioned
        assert "New product launches" in result.opportunities_mentioned
        mock_runner.assert_called_once()
    
    @pytest.mark.anyio
    @patch('src.research.management_guidance.management_guidance_agent.Runner.run')
    async def test_management_guidance_agent_json_parse_error(self, mock_runner):
        """Test agent when Runner.run fails with exception."""
        mock_runner.side_effect = Exception("AI processing error")
        
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"quarterlyEstimates": []},
            earnings_transcript={"transcript": "Sample transcript that is long enough to be processed correctly by the extraction function for testing purposes..."},
            quarter="2024Q1"
        )
        
        result = await management_guidance_agent("AAPL", guidance_data)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == False
        assert "AI processing error" in result.key_guidance_summary
    
    @pytest.mark.anyio
    @patch('src.research.management_guidance.management_guidance_agent.Runner.run')
    async def test_management_guidance_agent_llm_error(self, mock_runner):
        """Test agent when Runner.run fails."""
        mock_runner.side_effect = Exception("LLM API error")
        
        guidance_data = ManagementGuidanceData(
            symbol="AAPL",
            earnings_estimates={"quarterlyEstimates": []},
            earnings_transcript={"transcript": "Sample transcript that is long enough to be processed correctly by the extraction function for testing purposes..."},
            quarter="2024Q1"
        )
        
        result = await management_guidance_agent("AAPL", guidance_data)
        
        assert isinstance(result, ManagementGuidanceAnalysis)
        assert result.symbol == "AAPL"
        assert result.transcript_available == False
        assert "LLM API error" in result.key_guidance_summary