import pytest
from unittest.mock import patch
from legacy.tasks.financial_statements.financial_statements_fetch_task import financial_statements_fetch_task
from legacy.tasks.financial_statements.financial_statements_analysis_task import financial_statements_analysis_task
from legacy.research.financial_statements.financial_statements_models import (
    FinancialStatementsData, 
    FinancialStatementsAnalysis
)
from agents import RunResult


class TestFinancialStatementsFetchTask:
    
    @patch('src.tasks.financial_statements.financial_statements_fetch_task.get_financial_statements_data_for_symbol')
    @pytest.mark.anyio
    async def test_financial_statements_fetch_task_success(self, mock_get_data):
        """Test successful financial statements data fetch."""
        # Mock the utility function response
        mock_data = FinancialStatementsData(
            symbol="AAPL",
            income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000", "netIncome": "20000000"}],
            balance_sheets=[{"fiscalDateEnding": "2023-12-31", "totalAssets": "500000000", "totalShareholderEquity": "200000000"}],
            cash_flow_statements=[{"fiscalDateEnding": "2023-12-31", "operatingCashflow": "30000000", "capitalExpenditures": "5000000"}]
        )
        mock_get_data.return_value = mock_data
        
        result = await financial_statements_fetch_task("AAPL")
        
        assert isinstance(result, FinancialStatementsData)
        assert result.symbol == "AAPL"
        assert len(result.income_statements) == 1
        assert len(result.balance_sheets) == 1
        assert len(result.cash_flow_statements) == 1
        mock_get_data.assert_called_once_with("AAPL")

    @patch('src.tasks.financial_statements.financial_statements_fetch_task.get_financial_statements_data_for_symbol')
    @pytest.mark.anyio
    async def test_financial_statements_fetch_task_empty_data(self, mock_get_data):
        """Test financial statements fetch with empty data."""
        mock_data = FinancialStatementsData(
            symbol="INVALID",
            income_statements=[],
            balance_sheets=[],
            cash_flow_statements=[]
        )
        mock_get_data.return_value = mock_data
        
        result = await financial_statements_fetch_task("INVALID")
        
        assert isinstance(result, FinancialStatementsData)
        assert result.symbol == "INVALID"
        assert len(result.income_statements) == 0
        assert len(result.balance_sheets) == 0
        assert len(result.cash_flow_statements) == 0


class TestFinancialStatementsAnalysisTask:
    
    @patch('src.tasks.financial_statements.financial_statements_analysis_task.Runner.run')
    @pytest.mark.anyio
    async def test_financial_statements_analysis_task_success(self, mock_runner):
        """Test successful financial statements analysis."""
        # Mock financial data
        financial_data = FinancialStatementsData(
            symbol="AAPL",
            income_statements=[{"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000000", "netIncome": "20000000"}],
            balance_sheets=[{"fiscalDateEnding": "2023-12-31", "totalAssets": "500000000", "totalShareholderEquity": "200000000"}],
            cash_flow_statements=[{"fiscalDateEnding": "2023-12-31", "operatingCashflow": "30000000", "capitalExpenditures": "5000000"}]
        )
        
        # Mock the agent response
        mock_analysis = FinancialStatementsAnalysis(
            symbol="AAPL",
            revenue_driver_trend="STRENGTHENING",
            revenue_driver_details="Strong product sales growth driving revenue",
            cost_structure_trend="IMPROVING_EFFICIENCY",
            cost_structure_details="Stable operating leverage improving efficiency",
            working_capital_trend="IMPROVING_MANAGEMENT",
            working_capital_details="Efficient working capital management",
            key_financial_changes=["Revenue acceleration", "Margin improvement"],
            near_term_projection_risks=["Market competition risk"],
            analysis_confidence_score=85,
            data_quality_score=90,
            long_form_analysis="Strong financial performance with improving margins and efficiency",
            critical_insights="Improving financial metrics indicate operational efficiency gains"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_analysis})()
        mock_runner.return_value = mock_result
        
        result = await financial_statements_analysis_task("AAPL", financial_data)
        
        assert isinstance(result, FinancialStatementsAnalysis)
        assert result.symbol == "AAPL"
        assert result.revenue_driver_trend == "STRENGTHENING"
        assert result.cost_structure_trend == "IMPROVING_EFFICIENCY"
        assert result.working_capital_trend == "IMPROVING_MANAGEMENT"
        mock_runner.assert_called_once()