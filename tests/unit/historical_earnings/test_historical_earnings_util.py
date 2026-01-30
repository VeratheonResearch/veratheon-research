import pytest
from unittest.mock import patch, MagicMock
from legacy.research.historical_earnings.historical_earnings_util import (
    calculate_earnings_beat_miss_pattern,
    calculate_revenue_growth_trend,
    calculate_margin_trend,
    get_historical_earnings_data_for_symbol
)
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsData


class TestHistoricalEarningsUtil:
    
    def test_calculate_earnings_beat_miss_pattern_empty_data(self):
        """Test beat/miss pattern calculation with empty data."""
        result = calculate_earnings_beat_miss_pattern([])
        
        assert result["total_quarters"] == 0
        assert result["beats"] == 0
        assert result["misses"] == 0
        assert result["meets"] == 0
        assert result["beat_percentage"] == 0.0
        assert result["pattern"] == "INSUFFICIENT_DATA"
    
    def test_calculate_earnings_beat_miss_pattern_consistent_beats(self):
        """Test beat/miss pattern calculation with consistent beats."""
        quarterly_data = [
            {"reportedEPS": "2.50", "estimatedEPS": "2.30"},  # Beat
            {"reportedEPS": "2.80", "estimatedEPS": "2.60"},  # Beat
            {"reportedEPS": "3.10", "estimatedEPS": "2.90"},  # Beat
            {"reportedEPS": "3.40", "estimatedEPS": "3.20"},  # Beat
            {"reportedEPS": "3.70", "estimatedEPS": "3.50"},  # Beat
        ]
        
        result = calculate_earnings_beat_miss_pattern(quarterly_data)
        
        assert result["total_quarters"] == 5
        assert result["beats"] == 5
        assert result["misses"] == 0
        assert result["meets"] == 0
        assert result["beat_percentage"] == 100.0
        assert result["pattern"] == "CONSISTENT_BEATS"
    
    def test_calculate_earnings_beat_miss_pattern_mixed(self):
        """Test beat/miss pattern calculation with mixed results."""
        quarterly_data = [
            {"reportedEPS": "2.50", "estimatedEPS": "2.30"},  # Beat
            {"reportedEPS": "2.40", "estimatedEPS": "2.60"},  # Miss
            {"reportedEPS": "3.10", "estimatedEPS": "2.90"},  # Beat
            {"reportedEPS": "3.00", "estimatedEPS": "3.20"},  # Miss
        ]
        
        result = calculate_earnings_beat_miss_pattern(quarterly_data)
        
        assert result["total_quarters"] == 4
        assert result["beats"] == 2
        assert result["misses"] == 2
        assert result["meets"] == 0
        assert result["beat_percentage"] == 50.0
        assert result["pattern"] == "MIXED_PATTERN"
    
    def test_calculate_revenue_growth_trend_empty_data(self):
        """Test revenue growth trend calculation with empty data."""
        result = calculate_revenue_growth_trend([])
        
        assert result["years_analyzed"] == 0
        assert result["growth_rates"] == []
        assert result["avg_growth_rate"] == 0.0
        assert result["trend"] == "INSUFFICIENT_DATA"
    
    def test_calculate_revenue_growth_trend_stable(self):
        """Test revenue growth trend calculation with stable growth."""
        annual_data = [
            {"totalRevenue": "120000000"},  # Most recent
            {"totalRevenue": "110000000"},
            {"totalRevenue": "100000000"},  # Oldest
        ]
        
        result = calculate_revenue_growth_trend(annual_data)
        
        assert result["years_analyzed"] == 2
        assert len(result["growth_rates"]) == 2
        # Growth rates should be approximately 9.09% and 10%
        assert abs(result["growth_rates"][0] - 9.09) < 0.1  # (120-110)/110 * 100
        assert abs(result["growth_rates"][1] - 10.0) < 0.1  # (110-100)/100 * 100
        assert result["trend"] == "STABLE"
    
    def test_calculate_margin_trend_empty_data(self):
        """Test margin trend calculation with empty data."""
        result = calculate_margin_trend([])
        
        assert result["years_analyzed"] == 0
        assert result["gross_margins"] == []
        assert result["operating_margins"] == []
        assert result["net_margins"] == []
        assert result["trend"] == "INSUFFICIENT_DATA"
    
    def test_calculate_margin_trend_improving(self):
        """Test margin trend calculation with improving margins."""
        income_data = [
            {  # Most recent year
                "totalRevenue": "100000000",
                "grossProfit": "40000000",
                "operatingIncome": "20000000",
                "netIncome": "15000000"
            },
            {  # Previous year
                "totalRevenue": "90000000",
                "grossProfit": "32400000",  # 36% gross margin
                "operatingIncome": "16200000",  # 18% operating margin
                "netIncome": "10800000"  # 12% net margin
            }
        ]
        
        result = calculate_margin_trend(income_data)
        
        assert result["years_analyzed"] == 2
        assert len(result["gross_margins"]) == 2
        assert len(result["operating_margins"]) == 2
        assert len(result["net_margins"]) == 2
        # Most recent year should have better margins (40%, 20%, 15%)
        # vs previous year (36%, 18%, 12%)
        assert result["trend"] == "IMPROVING"
    
    @patch('src.research.historical_earnings.historical_earnings_util.call_alpha_vantage_earnings')
    @patch('src.research.historical_earnings.historical_earnings_util.call_alpha_vantage_income_statement')
    def test_get_historical_earnings_data_for_symbol_success(self, mock_income, mock_earnings):
        """Test successful data retrieval for a symbol."""
        # Mock the API responses
        mock_earnings.return_value = {
            'quarterlyEarnings': [
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"},
                {"fiscalDateEnding": "2023-09-30", "reportedEPS": "2.30"}
            ],
            'annualEarnings': [
                {"fiscalDateEnding": "2023-12-31", "reportedEPS": "9.50"}
            ]
        }
        
        mock_income.return_value = {
            'annualReports': [
                {
                    "fiscalDateEnding": "2023-12-31",
                    "totalRevenue": "100000000",
                    "grossProfit": "40000000"
                }
            ]
        }
        
        result = get_historical_earnings_data_for_symbol("AAPL")
        
        assert isinstance(result, HistoricalEarningsData)
        assert result.symbol == "AAPL"
        assert len(result.quarterly_earnings) == 2
        assert len(result.annual_earnings) == 1
        assert len(result.income_statement) == 1
        
        # Verify the API calls were made
        mock_earnings.assert_called_once_with("AAPL")
        mock_income.assert_called_once_with("AAPL")
    
    @patch('src.research.historical_earnings.historical_earnings_util.call_alpha_vantage_earnings')
    @patch('src.research.historical_earnings.historical_earnings_util.call_alpha_vantage_income_statement')
    def test_get_historical_earnings_data_for_symbol_api_error(self, mock_income, mock_earnings):
        """Test graceful handling of API errors."""
        # Mock API to raise an exception
        mock_earnings.side_effect = Exception("API Error")
        mock_income.side_effect = Exception("API Error")
        
        result = get_historical_earnings_data_for_symbol("INVALID")
        
        # Should return empty data structure instead of failing
        assert isinstance(result, HistoricalEarningsData)
        assert result.symbol == "INVALID"
        assert result.quarterly_earnings == []
        assert result.annual_earnings == []
        assert result.income_statement == []
    
    def test_calculate_earnings_beat_miss_pattern_invalid_data(self):
        """Test beat/miss pattern calculation with invalid EPS data."""
        quarterly_data = [
            {"reportedEPS": "invalid", "estimatedEPS": "2.30"},
            {"reportedEPS": "2.80", "estimatedEPS": "invalid"},
            {"reportedEPS": "0", "estimatedEPS": "2.90"},  # Zero values should be skipped
            {"reportedEPS": "3.40", "estimatedEPS": "3.20"},  # Valid data
        ]
        
        result = calculate_earnings_beat_miss_pattern(quarterly_data)
        
        # Should only count the one valid quarter
        assert result["total_quarters"] == 1
        assert result["beats"] == 1
        assert result["misses"] == 0
        assert result["pattern"] == "CONSISTENT_BEATS"