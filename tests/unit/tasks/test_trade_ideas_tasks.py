import pytest
from unittest.mock import patch
from legacy.tasks.trade_ideas.trade_ideas_task import trade_ideas_task
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from agents import RunResult


class TestTradeIdeasTask:
    
    @patch('src.tasks.trade_ideas.trade_ideas_task.Runner.run')
    @pytest.mark.anyio
    async def test_trade_ideas_task_success(self, mock_runner):
        """Test successful trade ideas generation."""
        # Mock forward PE valuation
        earnings_analysis = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=25.0,
            sector_average_pe=27.5,
            historical_pe_range="18-30",
            valuation_attractiveness="UNDERVALUED",
            earnings_quality="HIGH_QUALITY",
            confidence="HIGH",
            long_form_analysis="Trading below peer average with strong fundamentals. Forward PE of 25.0 vs peer average of 27.5 suggests undervaluation with target range $160-180.",
            critical_insights="Strong fundamentals support undervaluation thesis"
        )
        
        # Mock news sentiment summary
        news_sentiment = NewsSentimentSummary(
            symbol="AAPL",
            sentiment_trend="IMPROVING",
            news_volume="MODERATE_VOLUME",
            sentiment_confidence="HIGH",
            key_themes=["Earnings beat", "Product demand"],
            positive_catalysts=["Strong earnings", "New products"],
            negative_concerns=["Market volatility"],
            news_sentiment_analysis="Strong positive sentiment driven by earnings beat and product demand. Market shows bullish outlook with improving trend.",
            long_form_analysis="Detailed analysis shows strong positive coverage",
            overall_sentiment_label="Bullish",
            critical_insights="Positive sentiment supports bullish outlook"
        )
        
        # Mock the agent response
        mock_trade_idea = TradeIdea(
            symbol="AAPL",
            trade_direction="LONG",
            time_horizon="MEDIUM_TERM",
            risk_level="MEDIUM",
            overall_confidence="HIGH",
            high_level_trade_idea="BUY AAPL - Undervalued tech leader with strong fundamentals",
            reasoning="Trading below peer average with strong fundamentals and positive sentiment. Forward PE suggests undervaluation with bullish news sentiment supporting upside.",
            key_catalysts=["Earnings beat", "Product demand"],
            risk_factors=["Market volatility", "Economic slowdown"],
            simple_equity_trade_specifics="Long AAPL at $150, target $175, stop loss $140, 3-6 month horizon",
            option_play="Buy AAPL Mar calls, strike $155, delta 0.65, for leveraged exposure",
            risk_hedge="Consider position sizing at 3-5% of portfolio to manage single name risk",
            entry_price_target="$150",
            upside_price_target="$175",
            downside_stop_loss="$140",
            critical_insights="Undervaluation with strong fundamentals creates compelling risk/reward"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_trade_idea})()
        mock_runner.return_value = mock_result
        
        result = await trade_ideas_task(
            "AAPL",
            earnings_analysis,
            news_sentiment,
            historical_earnings_analysis={"pattern": "CONSISTENT_BEATS"},
            financial_statements_analysis={"trend": "IMPROVING"},
            earnings_projections_analysis={"projected_eps": 2.65},
            management_guidance_analysis={"guidance_tone": "POSITIVE"}
        )
        
        assert isinstance(result, TradeIdea)
        assert "BUY AAPL" in result.high_level_trade_idea
        assert "$175" in result.simple_equity_trade_specifics
        assert result.overall_confidence == "HIGH"
        mock_runner.assert_called_once()

    @patch('src.tasks.trade_ideas.trade_ideas_task.Runner.run')
    @pytest.mark.anyio
    async def test_trade_ideas_task_minimal_context(self, mock_runner):
        """Test trade ideas generation with minimal context."""
        # Mock basic forward PE valuation
        earnings_analysis = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=30.0,
            sector_average_pe=27.5,
            historical_pe_range="18-32",
            valuation_attractiveness="OVERVALUED",
            earnings_quality="ADEQUATE_QUALITY",
            confidence="MEDIUM",
            long_form_analysis="Trading above peer average with fair valuation but some overvaluation concerns. Forward PE of 30.0 vs peer average of 27.5.",
            critical_insights="Overvaluation concerns warrant cautious approach"
        )
        
        # Mock neutral news sentiment
        news_sentiment = NewsSentimentSummary(
            symbol="AAPL",
            sentiment_trend="STABLE_POSITIVE",
            news_volume="MODERATE_VOLUME",
            sentiment_confidence="MEDIUM",
            key_themes=["General coverage", "Mixed signals"],
            positive_catalysts=["Stable business"],
            negative_concerns=["No strong catalysts"],
            news_sentiment_analysis="Neutral sentiment with general coverage showing no strong directional bias.",
            long_form_analysis="Mixed coverage with no clear directional bias",
            overall_sentiment_label="Neutral",
            critical_insights="Neutral sentiment provides limited trading signals"
        )
        
        # Mock cautious trade idea
        mock_trade_idea = TradeIdea(
            symbol="AAPL",
            trade_direction="NEUTRAL",
            time_horizon="MEDIUM_TERM",
            risk_level="MEDIUM",
            overall_confidence="MEDIUM",
            high_level_trade_idea="HOLD AAPL - Overvalued but quality, wait for better entry",
            reasoning="Trading above peer average with neutral sentiment. Valuation stretched but quality company warrants patience for better entry point.",
            key_catalysts=["Potential price pullback", "Better entry points"],
            risk_factors=["Overvaluation", "Market conditions"],
            simple_equity_trade_specifics="Hold current position, consider adding below $140, target $145",
            option_play="Sell covered calls at $155 strike to generate income while waiting",
            risk_hedge="Maintain small allocation (1-2% of portfolio) given valuation concerns",
            entry_price_target="$140",
            upside_price_target="$145",
            downside_stop_loss="$130",
            critical_insights="Quality company warrants patience for better entry"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_trade_idea})()
        mock_runner.return_value = mock_result
        
        result = await trade_ideas_task("AAPL", earnings_analysis, news_sentiment)
        
        assert isinstance(result, TradeIdea)
        assert "HOLD AAPL" in result.high_level_trade_idea
        assert "better entry" in result.reasoning.lower()
        assert result.overall_confidence == "MEDIUM"
        mock_runner.assert_called_once()

    @patch('src.tasks.trade_ideas.trade_ideas_task.Runner.run')
    @pytest.mark.anyio
    async def test_trade_ideas_task_negative_sentiment(self, mock_runner):
        """Test trade ideas generation with negative sentiment."""
        # Mock negative forward PE valuation
        earnings_analysis = ForwardPeValuation(
            symbol="AAPL",
            current_price=150.0,
            forward_pe_ratio=35.0,
            sector_average_pe=27.5,
            historical_pe_range="18-32",
            valuation_attractiveness="EXTREME_VALUATION",
            earnings_quality="QUESTIONABLE_QUALITY",
            confidence="HIGH",
            long_form_analysis="Significantly overvalued with declining fundamentals. Forward PE of 35.0 vs peer average of 27.5 suggests major overvaluation with target $100-120.",
            critical_insights="Extreme overvaluation with declining fundamentals"
        )
        
        # Mock negative news sentiment
        news_sentiment = NewsSentimentSummary(
            symbol="AAPL",
            sentiment_trend="DETERIORATING",
            news_volume="HIGH_VOLUME",
            sentiment_confidence="HIGH",
            key_themes=["Declining sales", "Competitive pressure", "Market share loss"],
            positive_catalysts=[],
            negative_concerns=["Revenue decline", "Market share loss", "Competition"],
            news_sentiment_analysis="Negative sentiment driven by declining sales and competitive pressure. Market concerns about revenue decline and market share loss.",
            long_form_analysis="Negative coverage dominated by fundamental concerns",
            overall_sentiment_label="Bearish",
            critical_insights="Strong negative sentiment reflects fundamental deterioration"
        )
        
        # Mock sell recommendation
        mock_trade_idea = TradeIdea(
            symbol="AAPL",
            trade_direction="SHORT",
            time_horizon="MEDIUM_TERM",
            risk_level="HIGH",
            overall_confidence="HIGH",
            high_level_trade_idea="SELL AAPL - Overvalued with deteriorating fundamentals",
            reasoning="Significantly overvalued with declining fundamentals and negative sentiment. Multiple headwinds suggest further downside risk.",
            key_catalysts=["Declining sales", "Competitive pressure"],
            risk_factors=["Market reversal", "Unexpected positive news"],
            simple_equity_trade_specifics="Sell AAPL at current levels, target $110, stop loss $160",
            option_play="Buy AAPL puts, strike $140, 3-month expiry for hedging/shorting",
            risk_hedge="Reduce or exit position entirely given deteriorating outlook",
            entry_price_target="$150",
            upside_price_target="$110",
            downside_stop_loss="$160",
            critical_insights="Extreme overvaluation with declining fundamentals warrants exit"
        )
        
        # Mock the runner result
        mock_result = type('MockResult', (), {'final_output': mock_trade_idea})()
        mock_runner.return_value = mock_result
        
        result = await trade_ideas_task("AAPL", earnings_analysis, news_sentiment)
        
        assert isinstance(result, TradeIdea)
        assert "SELL AAPL" in result.high_level_trade_idea
        assert "declining" in result.reasoning.lower()
        assert result.overall_confidence == "HIGH"
        mock_runner.assert_called_once()