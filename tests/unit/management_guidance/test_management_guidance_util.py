"""Tests for management guidance utility functions."""

import pytest
from unittest.mock import patch, MagicMock
from legacy.research.management_guidance.management_guidance_util import (
    get_management_guidance_data_for_symbol,
    extract_latest_earnings_estimate,
    _determine_latest_transcript_quarter,
    _get_previous_quarter
)
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceData


class TestManagementGuidanceUtil:
    
    def test_get_previous_quarter(self):
        """Test quarter navigation logic."""
        assert _get_previous_quarter("2024Q1") == "2023Q4"
        assert _get_previous_quarter("2024Q2") == "2024Q1"
        assert _get_previous_quarter("2024Q3") == "2024Q2"
        assert _get_previous_quarter("2024Q4") == "2024Q3"
    
    @patch('src.research.management_guidance.management_guidance_util.datetime')
    def test_determine_latest_transcript_quarter_q1(self, mock_datetime):
        """Test quarter determination for Q1 (Jan-Mar)."""
        mock_datetime.now.return_value = MagicMock(month=2, year=2024)
        result = _determine_latest_transcript_quarter()
        assert result == "2023Q4"
    
    @patch('src.research.management_guidance.management_guidance_util.datetime')
    def test_determine_latest_transcript_quarter_q2(self, mock_datetime):
        """Test quarter determination for Q2 (Apr-Jun)."""
        mock_datetime.now.return_value = MagicMock(month=5, year=2024)
        result = _determine_latest_transcript_quarter()
        assert result == "2024Q1"
    
    @patch('src.research.management_guidance.management_guidance_util.datetime')
    def test_determine_latest_transcript_quarter_q3(self, mock_datetime):
        """Test quarter determination for Q3 (Jul-Sep)."""
        mock_datetime.now.return_value = MagicMock(month=8, year=2024)
        result = _determine_latest_transcript_quarter()
        assert result == "2024Q2"
    
    @patch('src.research.management_guidance.management_guidance_util.datetime')
    def test_determine_latest_transcript_quarter_q4(self, mock_datetime):
        """Test quarter determination for Q4 (Oct-Dec)."""
        mock_datetime.now.return_value = MagicMock(month=11, year=2024)
        result = _determine_latest_transcript_quarter()
        assert result == "2024Q3"
    
    def test_extract_latest_earnings_estimate_valid_data(self):
        """Test earnings estimate extraction with valid data."""
        earnings_estimates = {
            "quarterlyEstimates": [
                {
                    "fiscalDateEnding": "2024-06-30",
                    "estimatedEPS": 2.50
                },
                {
                    "fiscalDateEnding": "2024-03-31", 
                    "estimatedEPS": 2.30
                }
            ]
        }
        
        result = extract_latest_earnings_estimate(earnings_estimates)
        assert result is not None
        assert result[0] == "2024-06-30"
        assert result[1] == 2.50
    
    def test_extract_latest_earnings_estimate_empty_data(self):
        """Test earnings estimate extraction with empty data."""
        earnings_estimates = {"quarterlyEstimates": []}
        result = extract_latest_earnings_estimate(earnings_estimates)
        assert result is None
    
    def test_extract_latest_earnings_estimate_no_estimates(self):
        """Test earnings estimate extraction with no estimates key."""
        earnings_estimates = {}
        result = extract_latest_earnings_estimate(earnings_estimates)
        assert result is None
    
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_estimates')
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_call_transcripts')
    @patch('src.research.management_guidance.management_guidance_util._determine_latest_transcript_quarter')
    def test_get_management_guidance_data_success(self, mock_quarter, mock_transcripts, mock_estimates):
        """Test successful data retrieval."""
        mock_quarter.return_value = "2024Q1"
        mock_estimates.return_value = {"quarterlyEstimates": []}
        mock_transcripts.return_value = {"transcript": "Earnings call content..."}
        
        result = get_management_guidance_data_for_symbol("AAPL")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "AAPL"
        assert result.quarter == "2024Q1"
        assert result.earnings_transcript is not None
        assert result.earnings_estimates == {"quarterlyEstimates": []}
    
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_estimates')
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_call_transcripts')
    @patch('src.research.management_guidance.management_guidance_util._determine_latest_transcript_quarter')
    def test_get_management_guidance_data_no_transcript(self, mock_quarter, mock_transcripts, mock_estimates):
        """Test data retrieval when no transcript is available."""
        mock_quarter.return_value = "2024Q1"
        mock_estimates.return_value = {"quarterlyEstimates": []}
        mock_transcripts.side_effect = Exception("Transcript not available")
        
        result = get_management_guidance_data_for_symbol("AAPL")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "AAPL"
        assert result.quarter is None
        assert result.earnings_transcript is None
        assert result.earnings_estimates == {"quarterlyEstimates": []}
    
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_estimates')
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_call_transcripts')
    @patch('src.research.management_guidance.management_guidance_util._determine_latest_transcript_quarter')
    def test_get_management_guidance_data_fallback_quarter(self, mock_quarter, mock_transcripts, mock_estimates):
        """Test fallback to previous quarter when current quarter transcript is unavailable."""
        mock_quarter.return_value = "2024Q2"
        mock_estimates.return_value = {"quarterlyEstimates": []}
        
        # First call fails, second call (previous quarter) succeeds
        mock_transcripts.side_effect = [
            Exception("Current quarter not available"),
            {"transcript": "Previous quarter transcript..."}
        ]
        
        result = get_management_guidance_data_for_symbol("AAPL")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "AAPL"
        assert result.quarter == "2024Q1"  # Should fallback to previous quarter
        assert result.earnings_transcript is not None
    
    @patch('src.research.management_guidance.management_guidance_util.call_alpha_vantage_earnings_estimates')
    def test_get_management_guidance_data_api_error(self, mock_estimates):
        """Test error handling when API calls fail."""
        mock_estimates.side_effect = Exception("API error")
        
        result = get_management_guidance_data_for_symbol("AAPL")
        
        assert isinstance(result, ManagementGuidanceData)
        assert result.symbol == "AAPL"
        assert result.quarter is None
        assert result.earnings_transcript is None
        assert result.earnings_estimates == {}