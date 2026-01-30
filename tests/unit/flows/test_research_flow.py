import pytest
from unittest.mock import patch, AsyncMock, ANY
from legacy.flows.research_flow import main_research_flow
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from legacy.research.earnings_projections.earnings_projections_models import (
    EarningsProjectionAnalysis,
    NextQuarterProjection
)
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation, ForwardPeSanityCheck, ForwardPeSanityCheckRealistic
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from legacy.research.common.models.peer_group import PeerGroup
from legacy.research.cross_reference.cross_reference_models import CrossReferencedAnalysisCompletion, CrossReferencedAnalysis
from legacy.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport, KeyInsights


class TestMainResearchFlow:
    
    @patch('src.flows.research_flow.key_insights_flow')
    @patch('src.flows.research_flow.comprehensive_report_flow')
    @patch('src.flows.research_flow.ensure_reporting_directory_exists')
    @patch('src.flows.research_flow.trade_ideas_flow')
    @patch('src.flows.research_flow.cross_reference_flow')
    @patch('src.flows.research_flow.news_sentiment_flow')
    @patch('src.flows.research_flow.forward_pe_flow')
    @patch('src.flows.research_flow.forward_pe_sanity_check_flow')
    @patch('src.flows.research_flow.peer_group_reporting_task')
    @patch('src.flows.research_flow.peer_group_agent')
    @patch('src.flows.research_flow.management_guidance_flow')
    @patch('src.flows.research_flow.earnings_projections_flow')
    @patch('src.flows.research_flow.financial_statements_flow')
    @patch('src.flows.research_flow.historical_earnings_flow')
    @pytest.mark.anyio
    async def test_main_research_flow_success(
        self,
        mock_historical_earnings_flow,
        mock_financial_statements_flow,
        mock_earnings_projections_flow,
        mock_management_guidance_flow,
        mock_peer_group_agent,
        mock_peer_group_reporting_task,
        mock_forward_pe_sanity_check_flow,
        mock_forward_pe_flow,
        mock_news_sentiment_flow,
        mock_cross_reference_flow,
        mock_trade_ideas_flow,
        mock_ensure_reporting_directory_exists,
        mock_comprehensive_report_flow,
        mock_key_insights_flow
    ):
        """Test successful execution of the complete main research flow."""
        
        # Mock historical earnings analysis
        mock_historical = HistoricalEarningsAnalysis(
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
        mock_historical_earnings_flow.return_value = mock_historical
        
        # Mock financial statements analysis  
        mock_financial = FinancialStatementsAnalysis(
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
            critical_insights="Improving financial metrics support earnings growth trajectory"
        )
        mock_financial_statements_flow.return_value = mock_financial
        
        # Mock earnings projections analysis
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
        mock_projections = EarningsProjectionAnalysis(
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
        mock_earnings_projections_flow.return_value = mock_projections
        
        # Mock management guidance analysis
        mock_guidance = ManagementGuidanceAnalysis(
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
            key_guidance_summary="Management provided bullish guidance for next quarter with strong revenue outlook",
            long_form_analysis="Overall positive tone with specific revenue growth drivers mentioned",
            critical_insights="Management guidance reinforces positive fundamental outlook"
        )
        mock_management_guidance_flow.return_value = mock_guidance
        
        # Mock peer group
        mock_peers = PeerGroup(
            original_symbol="AAPL",
            peer_group=["MSFT", "GOOGL", "AMZN"]
        )
        mock_peer_group_agent.return_value = mock_peers
        
        # Mock forward PE sanity check
        mock_sanity = ForwardPeSanityCheck(
            symbol="AAPL",
            earnings_data_quality="HIGH_QUALITY",
            consensus_reliability="HIGH",
            long_form_analysis="Earnings data appears consistent and reliable for forward PE calculation",
            is_realistic=ForwardPeSanityCheckRealistic.REALISTIC,
            critical_insights="Earnings data quality supports reliable valuation analysis"
        )
        mock_forward_pe_sanity_check_flow.return_value = mock_sanity
        
        # Mock forward PE valuation
        mock_pe_valuation = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=22.5,
            sector_average_pe=25.0,
            historical_pe_range="18-28",
            valuation_attractiveness="UNDERVALUED",
            earnings_quality="HIGH_QUALITY",
            confidence="HIGH",
            long_form_analysis="Trading below peer average with strong fundamentals",
            critical_insights="Undervalued relative to peers with superior fundamentals"
        )
        mock_forward_pe_flow.return_value = mock_pe_valuation
        
        # Mock news sentiment summary
        mock_sentiment = NewsSentimentSummary(
            symbol="AAPL",
            sentiment_trend="IMPROVING",
            news_volume="MODERATE_VOLUME",
            sentiment_confidence="HIGH",
            key_themes=["Strong earnings", "Product demand"],
            positive_catalysts=["Earnings beat", "New product launches"],
            negative_concerns=["Market volatility"],
            news_sentiment_analysis="Recent news shows positive sentiment driven by strong earnings and product demand",
            long_form_analysis="Detailed sentiment analysis shows broad positive coverage",
            overall_sentiment_label="POSITIVE",
            critical_insights="News sentiment supports positive fundamental thesis"
        )
        mock_news_sentiment_flow.return_value = mock_sentiment
        
        # Mock cross-reference analysis
        mock_cross_reference = [CrossReferencedAnalysisCompletion(
            original_analysis_type="historical_earnings",
            cross_referenced_analysis=CrossReferencedAnalysis(
                major_adjustments=None,
                minor_adjustments=None
            )
        )]
        mock_cross_reference_flow.return_value = mock_cross_reference
        
        # Mock trade ideas
        mock_trade_idea = TradeIdea(
            symbol="AAPL",
            trade_direction="LONG",
            time_horizon="MEDIUM_TERM",
            risk_level="MEDIUM",
            overall_confidence="HIGH",
            high_level_trade_idea="BUY AAPL - Undervalued tech leader with strong fundamentals",
            reasoning="Trading below peer average with strong fundamentals and positive sentiment",
            key_catalysts=["Earnings beat", "New product cycle"],
            risk_factors=["Market volatility", "Economic slowdown"],
            simple_equity_trade_specifics="Long AAPL at $150, target $175, stop loss $140, 3-6 month horizon",
            option_play="Buy AAPL Mar calls, strike $155, delta 0.65, for leveraged exposure",
            risk_hedge="Consider position sizing at 3-5% of portfolio to manage single name risk",
            entry_price_target="$150",
            upside_price_target="$175",
            downside_stop_loss="$140",
            critical_insights="Undervaluation with strong fundamentals creates compelling risk/reward"
        )
        mock_trade_ideas_flow.return_value = mock_trade_idea
        
        # Mock comprehensive report and key insights
        mock_comprehensive_report = ComprehensiveReport(
            symbol="AAPL",
            company_name="Apple Inc",
            report_date="2025-09-19",
            comprehensive_analysis="Comprehensive analysis of Apple Inc."
        )
        mock_comprehensive_report_flow.return_value = mock_comprehensive_report
        
        mock_key_insights = KeyInsights(
            symbol="AAPL",
            company_name="Apple Inc",
            report_date="2025-09-19",
            critical_insights="Apple shows strong performance with positive outlook."
        )
        mock_key_insights_flow.return_value = mock_key_insights
        
        # Mock additional tasks
        mock_ensure_reporting_directory_exists.return_value = None
        mock_peer_group_reporting_task.return_value = None
        
        # Execute the main research flow
        result = await main_research_flow("AAPL")
        
        # Verify the result
        assert isinstance(result, dict)
        assert result["symbol"] == "AAPL"
        assert "comprehensive_report" in result
        comprehensive_report = result["comprehensive_report"]
        assert comprehensive_report["symbol"] == "AAPL"
        assert "key_insights" in result
        
        # Verify all flows were called in the correct order
        mock_historical_earnings_flow.assert_called_once_with("AAPL", force_recompute=False)
        mock_financial_statements_flow.assert_called_once_with("AAPL", force_recompute=False)
        mock_earnings_projections_flow.assert_called_once_with(
            "AAPL", 
            mock_historical.model_dump(),
            mock_financial.model_dump(),
            force_recompute=False
        )
        mock_management_guidance_flow.assert_called_once_with(
            "AAPL",
            mock_historical,
            mock_financial,
            force_recompute=False
        )
        mock_peer_group_agent.assert_called_once_with("AAPL", mock_financial)
        mock_forward_pe_sanity_check_flow.assert_called_once_with("AAPL", force_recompute=False)
        mock_forward_pe_flow.assert_called_once_with(
            "AAPL",
            mock_peers,
            mock_projections,
            mock_guidance,
            mock_sanity,
            force_recompute=False
        )
        mock_news_sentiment_flow.assert_called_once_with(
            "AAPL",
            mock_peers,
            mock_projections,
            mock_guidance,
            force_recompute=False
        )
        mock_trade_ideas_flow.assert_called_once_with(
            "AAPL",
            mock_pe_valuation,
            mock_sentiment,
            mock_historical,
            mock_financial,
            mock_projections,
            mock_guidance,
            force_recompute=False
        )
        mock_comprehensive_report_flow.assert_called_once_with(
            "AAPL",
            ANY,
            force_recompute=False
        )
        mock_key_insights_flow.assert_called_once_with(
            "AAPL",
            mock_comprehensive_report,
            force_recompute=False
        )

    @patch('src.flows.research_flow.ensure_reporting_directory_exists')
    @patch('src.flows.research_flow.update_job_status_task')
    @patch('src.flows.research_flow.company_overview_flow')
    @patch('src.flows.research_flow.global_quote_flow')
    @patch('src.flows.research_flow.historical_earnings_flow')
    @pytest.mark.anyio
    async def test_main_research_flow_early_failure(
        self,
        mock_historical_earnings_flow,
        mock_global_quote_flow,
        mock_company_overview_flow,
        mock_update_job_status,
        mock_ensure_reporting_dir
    ):
        """Test main research flow behavior when an early step fails."""

        # Mock successful early steps
        mock_ensure_reporting_dir.return_value = None
        mock_update_job_status.return_value = None
        mock_company_overview_flow.return_value = AsyncMock()
        mock_global_quote_flow.return_value = AsyncMock()

        # Mock historical earnings flow to raise an exception
        mock_historical_earnings_flow.side_effect = Exception("Historical earnings data unavailable")

        # Execute the main research flow and expect it to fail
        with pytest.raises(Exception, match="Historical earnings data unavailable"):
            await main_research_flow("INVALID")

        # Verify historical earnings flow was attempted
        mock_historical_earnings_flow.assert_called_once_with("INVALID", force_recompute=False)
