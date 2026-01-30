from legacy.research.cross_reference.cross_reference_models import (
    CrossReferencedAnalysisCompletion,
)
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.historical_earnings.historical_earnings_models import (
    HistoricalEarningsAnalysis,
)
from legacy.research.financial_statements.financial_statements_models import (
    FinancialStatementsAnalysis,
)
from legacy.research.earnings_projections.earnings_projections_models import (
    EarningsProjectionAnalysis,
)
from legacy.research.management_guidance.management_guidance_models import (
    ManagementGuidanceAnalysis,
)
import logging
import time
from typing import List
from legacy.tasks.cache_retrieval.cross_reference_cache_retrieval_task import cross_reference_cache_retrieval_task
from legacy.tasks.cross_reference.cross_reference_task import cross_reference_task
from legacy.tasks.cross_reference.cross_reference_reporting_task import (
    cross_reference_reporting_task,
)
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CrossReferenceContext:
    symbol: str
    forward_pe_flow_result: ForwardPeValuation
    news_sentiment_flow_result: NewsSentimentSummary
    historical_earnings_analysis: HistoricalEarningsAnalysis
    financial_statements_analysis: FinancialStatementsAnalysis
    earnings_projections_analysis: EarningsProjectionAnalysis
    management_guidance_analysis: ManagementGuidanceAnalysis


async def cross_reference_flow(
    symbol: str,
    forward_pe_flow_result: ForwardPeValuation,
    news_sentiment_flow_result: NewsSentimentSummary,
    historical_earnings_analysis: HistoricalEarningsAnalysis,
    financial_statements_analysis: FinancialStatementsAnalysis,
    earnings_projections_analysis: EarningsProjectionAnalysis,
    management_guidance_analysis: ManagementGuidanceAnalysis,
    force_recompute: bool = False,
) -> List[CrossReferencedAnalysisCompletion]:

    context = CrossReferenceContext(
        symbol=symbol,
        forward_pe_flow_result=forward_pe_flow_result,
        news_sentiment_flow_result=news_sentiment_flow_result,
        historical_earnings_analysis=historical_earnings_analysis,
        financial_statements_analysis=financial_statements_analysis,
        earnings_projections_analysis=earnings_projections_analysis,
        management_guidance_analysis=management_guidance_analysis,
    )

    start_time = time.time()
    logger.info(f"Cross Reference flow started for {context.symbol}")

    # Try to get cached report first
    cached_result = await cross_reference_cache_retrieval_task(context.symbol, forward_pe_flow_result, news_sentiment_flow_result, historical_earnings_analysis, financial_statements_analysis, earnings_projections_analysis, management_guidance_analysis, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached cross reference analysis for {context.symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh cross reference analysis for {context.symbol}")

    cross_reference_forward_pe_completion = await forward_pe_cross_reference(context)

    cross_reference_news_sentiment_completion = await news_sentiment_cross_reference(
        context
    )

    cross_reference_historical_earnings_completion = (
        await historical_earnings_cross_reference(context)
    )

    cross_reference_financial_statements_completion = (
        await financial_statements_cross_reference(context)
    )

    cross_reference_earnings_projections_completion = (
        await earnings_projections_cross_reference(context)
    )

    cross_reference_management_guidance_completion = (
        await management_guidance_cross_reference(context)
    )

    cross_referenced_analysis = [
        cross_reference_forward_pe_completion,
        cross_reference_news_sentiment_completion,
        cross_reference_historical_earnings_completion,
        cross_reference_financial_statements_completion,
        cross_reference_earnings_projections_completion,
        cross_reference_management_guidance_completion,
    ]

    # Generate reporting output
    await cross_reference_reporting_task(symbol, cross_referenced_analysis)

    logger.info(
        f"Cross Reference flow completed for {context.symbol} in {int(time.time() - start_time)} seconds"
    )

    return cross_referenced_analysis


async def forward_pe_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.news_sentiment_flow_result,
        context.historical_earnings_analysis,
        context.financial_statements_analysis,
        context.earnings_projections_analysis,
        context.management_guidance_analysis,
    ]


    cross_reference_forward_pe_completion: CrossReferencedAnalysisCompletion = (
        await cross_reference_task(
            symbol=context.symbol,
            original_analysis_type="forward_pe",
            original_analysis=context.forward_pe_flow_result,
            data_points=data_points,
        )
    )
    return cross_reference_forward_pe_completion


async def news_sentiment_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.forward_pe_flow_result,
        context.historical_earnings_analysis,
        context.financial_statements_analysis,
        context.earnings_projections_analysis,
        context.management_guidance_analysis,
    ]


    cross_reference_news_sentiment_completion: CrossReferencedAnalysisCompletion = (
        await cross_reference_task(
            symbol=context.symbol,
            original_analysis_type="news_sentiment",
            original_analysis=context.news_sentiment_flow_result,
            data_points=data_points,
        )
    )
    return cross_reference_news_sentiment_completion


async def historical_earnings_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.forward_pe_flow_result,
        context.news_sentiment_flow_result,
        context.financial_statements_analysis,
        context.earnings_projections_analysis,
        context.management_guidance_analysis,
    ]


    cross_reference_historical_earnings_completion: (
        CrossReferencedAnalysisCompletion
    ) = await cross_reference_task(
        symbol=context.symbol,
        original_analysis_type="historical_earnings",
        original_analysis=context.historical_earnings_analysis,
        data_points=data_points,
    )
    return cross_reference_historical_earnings_completion


async def financial_statements_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.forward_pe_flow_result,
        context.historical_earnings_analysis,
        context.news_sentiment_flow_result,
        context.earnings_projections_analysis,
        context.management_guidance_analysis,
    ]


    cross_reference_financial_statements_completion: (
        CrossReferencedAnalysisCompletion
    ) = await cross_reference_task(
        symbol=context.symbol,
        original_analysis_type="financial_statements",
        original_analysis=context.financial_statements_analysis,
        data_points=data_points,
    )
    return cross_reference_financial_statements_completion


async def earnings_projections_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.forward_pe_flow_result,
        context.historical_earnings_analysis,
        context.news_sentiment_flow_result,
        context.financial_statements_analysis,
        context.management_guidance_analysis,
    ]


    cross_reference_earnings_projections_completion: (
        CrossReferencedAnalysisCompletion
    ) = await cross_reference_task(
        symbol=context.symbol,
        original_analysis_type="earnings_projections",
        original_analysis=context.earnings_projections_analysis,
        data_points=data_points,
    )
    return cross_reference_earnings_projections_completion


async def management_guidance_cross_reference(context: CrossReferenceContext):
    data_points = [
        context.forward_pe_flow_result,
        context.historical_earnings_analysis,
        context.news_sentiment_flow_result,
        context.financial_statements_analysis,
        context.earnings_projections_analysis,
    ]


    cross_reference_management_guidance_completion: (
        CrossReferencedAnalysisCompletion
    ) = await cross_reference_task(
        symbol=context.symbol,
        original_analysis_type="management_guidance",
        original_analysis=context.management_guidance_analysis,
        data_points=data_points,
    )
    return cross_reference_management_guidance_completion


