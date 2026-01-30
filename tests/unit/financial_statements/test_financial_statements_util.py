import pytest
from unittest.mock import patch, MagicMock
from legacy.research.financial_statements.financial_statements_util import (
    calculate_revenue_driver_metrics,
    calculate_cost_structure_metrics,
    calculate_working_capital_metrics,
    get_financial_statements_data_for_symbol
)
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsData


class TestFinancialStatementsUtil:
    
    def test_calculate_revenue_driver_metrics_empty_data(self):
        """Test revenue driver metrics calculation with empty data."""
        result = calculate_revenue_driver_metrics([])
        
        assert result["revenue_growth_rates"] == []
        assert result["revenue_trend"] == "INSUFFICIENT_DATA"
        assert result["avg_growth_rate"] == 0.0
        assert result["revenue_volatility"] == 0.0
        assert result["years_analyzed"] == 0
    
    def test_calculate_revenue_driver_metrics_strengthening(self):
        """Test revenue driver metrics with strengthening trend."""
        income_statements = [
            {"totalRevenue": "120000000"},  # Most recent (20% growth)
            {"totalRevenue": "100000000"},  # Previous (11% growth)
            {"totalRevenue": "90000000"},   # Oldest
        ]
        
        result = calculate_revenue_driver_metrics(income_statements)
        
        assert result["years_analyzed"] == 2
        assert len(result["revenue_growth_rates"]) == 2
        # Should show strengthening trend (20% > 11.1% average)
        assert result["revenue_trend"] == "STRENGTHENING"
        assert result["avg_growth_rate"] > 10
    
    def test_calculate_revenue_driver_metrics_volatile(self):
        """Test revenue driver metrics with volatile revenue."""
        income_statements = [
            {"totalRevenue": "150000000"},  # +50% growth
            {"totalRevenue": "100000000"},  # -10% decline
            {"totalRevenue": "110000000"},  # Previous
        ]
        
        result = calculate_revenue_driver_metrics(income_statements)
        
        assert result["years_analyzed"] == 2
        # Should be classified as volatile due to high variance
        assert result["revenue_volatility"] > 15
        assert result["revenue_trend"] == "VOLATILE"
    
    def test_calculate_cost_structure_metrics_empty_data(self):
        """Test cost structure metrics with empty data."""
        result = calculate_cost_structure_metrics([])
        
        assert result["cogs_margins"] == []
        assert result["sga_ratios"] == []
        assert result["rd_ratios"] == []
        assert result["cost_trend"] == "INSUFFICIENT_DATA"
        assert result["efficiency_score"] == 0.0
        assert result["years_analyzed"] == 0
    
    def test_calculate_cost_structure_metrics_improving(self):
        """Test cost structure metrics with improving efficiency."""
        income_statements = [
            {  # Most recent year - better efficiency
                "totalRevenue": "100000000",
                "costOfRevenue": "60000000",  # 60% COGS margin
                "sellingGeneralAndAdministrative": "15000000",  # 15% SG&A
                "researchAndDevelopment": "5000000"  # 5% R&D
            },
            {  # Previous year - worse efficiency
                "totalRevenue": "90000000",
                "costOfRevenue": "58500000",  # 65% COGS margin
                "sellingGeneralAndAdministrative": "14400000",  # 16% SG&A
                "researchAndDevelopment": "4500000"  # 5% R&D
            }
        ]
        
        result = calculate_cost_structure_metrics(income_statements)
        
        assert result["years_analyzed"] == 2
        assert len(result["cogs_margins"]) == 2
        assert len(result["sga_ratios"]) == 2
        # COGS margin should be improving (60% < 65%)
        assert result["cogs_trend"] == "IMPROVING_EFFICIENCY"
        # Overall trend should be improving
        assert result["cost_trend"] == "IMPROVING_EFFICIENCY"
    
    def test_calculate_working_capital_metrics_empty_data(self):
        """Test working capital metrics with empty data."""
        result = calculate_working_capital_metrics([], [])
        
        assert result["working_capital_ratios"] == []
        assert result["working_capital_trend"] == "INSUFFICIENT_DATA"
        assert result["years_analyzed"] == 0
    
    def test_calculate_working_capital_metrics_improving(self):
        """Test working capital metrics with improving management."""
        balance_sheets = [
            {  # Most recent year
                "totalAssets": "1000000000",
                "totalCurrentAssets": "400000000",
                "totalCurrentLiabilities": "200000000",  # WC = 200M (20% of assets)
                "currentAccountsReceivable": "100000000",
                "inventory": "150000000",
                "currentAccountsPayable": "80000000"
            },
            {  # Previous year
                "totalAssets": "900000000",
                "totalCurrentAssets": "300000000",
                "totalCurrentLiabilities": "200000000",  # WC = 100M (11% of assets)
                "currentAccountsReceivable": "90000000",
                "inventory": "120000000",
                "currentAccountsPayable": "70000000"
            },
            {  # Two years ago
                "totalAssets": "800000000",
                "totalCurrentAssets": "280000000",
                "totalCurrentLiabilities": "180000000",  # WC = 100M (12.5% of assets)
                "currentAccountsReceivable": "80000000",
                "inventory": "110000000",
                "currentAccountsPayable": "60000000"
            }
        ]
        
        result = calculate_working_capital_metrics(balance_sheets, [])
        
        assert result["years_analyzed"] == 3
        assert len(result["working_capital_ratios"]) == 3
        # Working capital should be improving (20% > avg of 11% and 12.5%)
        assert result["working_capital_trend"] == "IMPROVING_MANAGEMENT"
    
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_income_statement')
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_balance_sheet')
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_cash_flow')
    def test_get_financial_statements_data_for_symbol_success(self, mock_cash_flow, mock_balance, mock_income):
        """Test successful data retrieval for a symbol."""
        # Mock the API responses
        mock_income.return_value = {
            'annualReports': [
                {"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000"},
                {"fiscalDateEnding": "2022-12-31", "totalRevenue": "90000000"}
            ]
        }
        
        mock_balance.return_value = {
            'annualReports': [
                {"fiscalDateEnding": "2023-12-31", "totalAssets": "500000000"}
            ]
        }
        
        mock_cash_flow.return_value = {
            'annualReports': [
                {"fiscalDateEnding": "2023-12-31", "operatingCashflow": "50000000"}
            ]
        }
        
        result = get_financial_statements_data_for_symbol("AAPL")
        
        assert isinstance(result, FinancialStatementsData)
        assert result.symbol == "AAPL"
        assert len(result.income_statements) == 2
        assert len(result.balance_sheets) == 1
        assert len(result.cash_flow_statements) == 1
        
        # Verify the API calls were made
        mock_income.assert_called_once_with("AAPL")
        mock_balance.assert_called_once_with("AAPL")
        mock_cash_flow.assert_called_once_with("AAPL")
    
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_income_statement')
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_balance_sheet')
    @patch('src.research.financial_statements.financial_statements_util.call_alpha_vantage_cash_flow')
    def test_get_financial_statements_data_for_symbol_api_error(self, mock_cash_flow, mock_balance, mock_income):
        """Test graceful handling of API errors."""
        # Mock APIs to raise exceptions
        mock_income.side_effect = Exception("API Error")
        mock_balance.side_effect = Exception("API Error")
        mock_cash_flow.side_effect = Exception("API Error")
        
        result = get_financial_statements_data_for_symbol("INVALID")
        
        # Should return empty data structure instead of failing
        assert isinstance(result, FinancialStatementsData)
        assert result.symbol == "INVALID"
        assert result.income_statements == []
        assert result.balance_sheets == []
        assert result.cash_flow_statements == []
    
    def test_calculate_cost_structure_metrics_invalid_data(self):
        """Test cost structure metrics with invalid revenue data."""
        income_statements = [
            {
                "totalRevenue": "0",  # Zero revenue should be skipped
                "costOfRevenue": "1000000",
                "sellingGeneralAndAdministrative": "500000"
            },
            {
                "totalRevenue": "invalid",  # Invalid data should be skipped
                "costOfRevenue": "1000000"
            },
            {
                "totalRevenue": "100000000",  # Valid data
                "costOfRevenue": "60000000",
                "sellingGeneralAndAdministrative": "15000000"
            }
        ]
        
        result = calculate_cost_structure_metrics(income_statements)
        
        # Should only count the one valid statement
        assert result["years_analyzed"] == 1
        assert len(result["cogs_margins"]) == 1
        assert result["cogs_margins"][0] == 60.0  # 60% COGS margin