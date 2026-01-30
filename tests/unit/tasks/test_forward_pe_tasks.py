import pytest
from unittest.mock import patch, AsyncMock
from legacy.tasks.forward_pe.forward_pe_fetch_earnings_task import (
    forward_pe_fetch_earnings_for_symbols_task,
    forward_pe_fetch_single_earnings_task
)
from legacy.tasks.forward_pe.forward_pe_sanity_check_task import forward_pe_sanity_check_task
from legacy.tasks.forward_pe.forward_pe_peer_group_task import forward_pe_peer_group_task
from legacy.tasks.forward_pe.forward_pe_analysis_task import forward_pe_analysis_task
from legacy.research.forward_pe.forward_pe_models import (
    ForwardPEEarningsSummary,
    ForwardPeSanityCheck,
    ForwardPeValuation
)
from legacy.research.common.models.peer_group import PeerGroup
from agents import RunResult


class TestForwardPEFetchEarningsTask:
    
    @patch('src.tasks.forward_pe.forward_pe_fetch_earnings_task.get_quarterly_eps_data_for_symbols')
    @pytest.mark.anyio
    async def test_forward_pe_fetch_earnings_for_symbols_task_success(self, mock_get_data):
        """Test successful earnings data fetch for symbol and peer group."""
        # Mock the utility function response
        mock_earnings_list = [
            ForwardPEEarningsSummary(
                symbol="AAPL",
                overview={"MarketCapitalization": "3000000000000"},
                current_price="150.00",
                quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
                consensus_eps_next_quarter="2.65"
            ),
            ForwardPEEarningsSummary(
                symbol="MSFT",
                overview={"MarketCapitalization": "2500000000000"},
                current_price="300.00",
                quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "3.00"}],
                consensus_eps_next_quarter="3.10"
            )
        ]
        mock_get_data.return_value = mock_earnings_list
        
        result = await forward_pe_fetch_earnings_for_symbols_task("AAPL", ["MSFT", "GOOGL"])
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].symbol == "AAPL"
        assert result[1].symbol == "MSFT"
        mock_get_data.assert_called_once_with(["AAPL", "MSFT", "GOOGL"])

    @patch('src.tasks.forward_pe.forward_pe_fetch_earnings_task.get_quarterly_eps_data_for_symbol')
    @pytest.mark.anyio
    async def test_forward_pe_fetch_single_earnings_task_success(self, mock_get_data):
        """Test successful single earnings data fetch."""
        mock_earnings = ForwardPEEarningsSummary(
            symbol="AAPL",
            overview={"MarketCapitalization": "3000000000000"},
            current_price="150.00",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            consensus_eps_next_quarter="2.65"
        )
        mock_get_data.return_value = mock_earnings
        
        result = await forward_pe_fetch_single_earnings_task("AAPL")
        
        assert isinstance(result, ForwardPEEarningsSummary)
        assert result.symbol == "AAPL"
        assert result.current_price == "150.00"
        assert result.consensus_eps_next_quarter == "2.65"
        mock_get_data.assert_called_once_with("AAPL")


class TestForwardPESanityCheckTask:
    
    @patch('src.tasks.forward_pe.forward_pe_sanity_check_task.Runner.run')
    @pytest.mark.anyio
    async def test_forward_pe_sanity_check_task_success(self, mock_runner):
        """Test successful forward PE sanity check."""
        # Mock earnings summary
        earnings_summary = ForwardPEEarningsSummary(
            symbol="AAPL",
            overview={"MarketCapitalization": "3000000000000"},
            current_price="150.00",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            consensus_eps_next_quarter="2.65"
        )
        
        # Mock the agent response
        mock_sanity_check = ForwardPeSanityCheck(
            symbol="AAPL",
            earnings_data_quality="HIGH_QUALITY",
            consensus_reliability="HIGH",
            long_form_analysis="Data appears reliable for analysis with consistent earnings",
            is_realistic="REALISTIC",
            critical_insights="Earnings data quality supports reliable analysis"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_sanity_check})()
        mock_runner.return_value = mock_result
        
        result = await forward_pe_sanity_check_task(earnings_summary)
        
        assert isinstance(result, ForwardPeSanityCheck)
        assert result.is_realistic == "REALISTIC"
        assert "consistent earnings" in result.long_form_analysis
        mock_runner.assert_called_once()


class TestForwardPEPeerGroupTask:
    
    @patch('src.tasks.forward_pe.forward_pe_peer_group_task.peer_group_chatcompletion')
    @pytest.mark.anyio
    async def test_forward_pe_peer_group_task_success(self, mock_peer_group):
        """Test successful peer group identification."""
        mock_peers = PeerGroup(
            original_symbol="AAPL",
            peer_group=["MSFT", "GOOGL", "AMZN"]
        )
        mock_peer_group.return_value = mock_peers
        
        result = await forward_pe_peer_group_task("AAPL")
        
        assert isinstance(result, PeerGroup)
        assert result.original_symbol == "AAPL"
        assert len(result.peer_group) == 3
        assert "MSFT" in result.peer_group
        mock_peer_group.assert_called_once_with("AAPL")


class TestForwardPEAnalysisTask:
    
    @patch('src.tasks.forward_pe.forward_pe_analysis_task.Runner.run')
    @pytest.mark.anyio
    async def test_forward_pe_analysis_task_success(self, mock_runner):
        """Test successful forward PE analysis."""
        # Mock earnings summary
        earnings_summary = ForwardPEEarningsSummary(
            symbol="AAPL",
            overview={"MarketCapitalization": "3000000000000"},
            current_price="150.00",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            consensus_eps_next_quarter="2.65"
        )
        
        # Mock the agent response
        mock_valuation = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=25.0,
            sector_average_pe=27.5,
            historical_pe_range="20-30",
            valuation_attractiveness="UNDERVALUED",
            earnings_quality="HIGH_QUALITY",
            confidence="HIGH",
            long_form_analysis="Trading below peer average with strong fundamentals. Forward PE of 25.0 vs peer average of 27.5 suggests undervaluation.",
            critical_insights="Strong fundamentals support undervaluation thesis"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_valuation})()
        mock_runner.return_value = mock_result
        
        result = await forward_pe_analysis_task(
            "AAPL", 
            earnings_summary,
            earnings_projections_analysis={"projected_eps": 2.65},
            management_guidance_analysis={"guidance_tone": "POSITIVE"}
        )
        
        assert isinstance(result, ForwardPeValuation)
        assert result.confidence == "HIGH"
        assert "undervaluation" in result.long_form_analysis
        mock_runner.assert_called_once()

    @patch('src.tasks.forward_pe.forward_pe_analysis_task.Runner.run')
    @pytest.mark.anyio
    async def test_forward_pe_analysis_task_minimal_context(self, mock_runner):
        """Test forward PE analysis with minimal context."""
        earnings_summary = ForwardPEEarningsSummary(
            symbol="AAPL",
            overview={"MarketCapitalization": "3000000000000"},
            current_price="150.00",
            quarterly_earnings=[{"fiscalDateEnding": "2023-12-31", "reportedEPS": "2.50"}],
            consensus_eps_next_quarter="2.65"
        )
        
        mock_valuation = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=27.0,
            sector_average_pe=27.5,
            historical_pe_range="20-30",
            valuation_attractiveness="FAIRLY_VALUED",
            earnings_quality="ADEQUATE_QUALITY",
            confidence="MEDIUM",
            long_form_analysis="Limited context analysis shows fair valuation with some upside potential.",
            critical_insights="Limited context provides moderate confidence in valuation"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_valuation})()
        mock_runner.return_value = mock_result
        
        result = await forward_pe_analysis_task("AAPL", earnings_summary)
        
        assert isinstance(result, ForwardPeValuation)
        assert result.confidence == "MEDIUM"
        assert "Limited context" in result.long_form_analysis
        mock_runner.assert_called_once()