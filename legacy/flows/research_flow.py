from dotenv import load_dotenv
from src.lib.llm_model import set_model_context
from src.lib.supabase_logger import log_info
from src.lib.token_logger_hook import TokenLoggerHook
from legacy.flows.subflows.forward_pe_flow import forward_pe_flow, forward_pe_sanity_check_flow
from legacy.flows.subflows.trade_ideas_flow import trade_ideas_flow
from legacy.flows.subflows.news_sentiment_flow import news_sentiment_flow
from legacy.flows.subflows.historical_earnings_flow import historical_earnings_flow
from legacy.flows.subflows.financial_statements_flow import financial_statements_flow
from legacy.flows.subflows.earnings_projections_flow import earnings_projections_flow
from legacy.flows.subflows.management_guidance_flow import management_guidance_flow
from legacy.flows.subflows.cross_reference_flow import cross_reference_flow
from legacy.flows.subflows.comprehensive_report_flow import comprehensive_report_flow
from legacy.flows.subflows.key_insights_flow import key_insights_flow
from legacy.flows.subflows.company_overview_flow import company_overview_flow
from legacy.flows.subflows.global_quote_flow import global_quote_flow
from legacy.tasks.common.job_status_task import update_job_status_task
from src.lib.supabase_job_tracker import JobStatus
from legacy.tasks.common.peer_group_reporting_task import peer_group_reporting_task
from legacy.tasks.common.reporting_directory_setup_task import ensure_reporting_directory_exists
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation, ForwardPeSanityCheck
from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
from legacy.research.common.peer_group_agent import peer_group_agent
from legacy.research.common.models.peer_group import PeerGroup
from legacy.research.cross_reference.cross_reference_models import CrossReferencedAnalysisCompletion
from legacy.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport, KeyInsights
from legacy.research.company_overview.company_overview_models import CompanyOverviewAnalysis
from legacy.research.global_quote.global_quote_models import GlobalQuoteData

import logging
import time
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

load_dotenv()

def get_current_date() -> str:
    """
    Get today's current date in YYYY-MM-DD format.
    
    Returns:
        str: Current date in ISO format (YYYY-MM-DD)
    """
    return datetime.now().strftime("%Y-%m-%d")

async def main_research_flow(
    symbol: str,
    force_recompute: bool = False,
    job_id: str = None,
    model: str = "o4_mini",
) -> dict:

    start_time = time.time()
    logger.info(f"Main research flow started for {symbol} using model {model}")

    # Reset token tracking for this workflow
    TokenLoggerHook.reset()

    # Set the model context for all downstream agents in this async context
    set_model_context(model)

    # Log model selection to system logs
    log_info(
        component="main_research_flow",
        message=f"Research flow initialized with model: {model}",
        job_id=job_id,
        symbol=symbol,
        metadata={"model": model, "force_recompute": force_recompute}
    )

    await ensure_reporting_directory_exists()

    await update_job_status_task(job_id, JobStatus.RUNNING, "Starting main research flow", "main_research_flow", symbol)

    # Company overview provides foundational business context
    await update_job_status_task(job_id, JobStatus.RUNNING, "Analyzing company overview", "company_overview_flow", symbol)
    company_overview_analysis: CompanyOverviewAnalysis = await company_overview_flow(symbol, force_recompute=force_recompute)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Company overview complete", "company_overview_flow", symbol)

    # Global quote provides current price data
    await update_job_status_task(job_id, JobStatus.RUNNING, "Fetching current market data", "global_quote_flow", symbol)
    global_quote_data: GlobalQuoteData = await global_quote_flow(symbol, force_recompute=force_recompute)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Current market data fetched", "global_quote_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Analyzing historical earnings", "historical_earnings_flow", symbol)
    historical_earnings_analysis: HistoricalEarningsAnalysis = await historical_earnings_flow(symbol, force_recompute=force_recompute)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Historical earnings analysis complete", "historical_earnings_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Analyzing financial statements", "financial_statements_flow", symbol)
    financial_statements_analysis: FinancialStatementsAnalysis = await financial_statements_flow(symbol, force_recompute=force_recompute)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Financial statements analysis complete", "financial_statements_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Generating earnings projections", "earnings_projections_flow", symbol)
    earnings_projections_analysis: EarningsProjectionAnalysis = await earnings_projections_flow(
        symbol,
        historical_earnings_analysis.model_dump(),
        financial_statements_analysis.model_dump(),
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Earnings projections complete", "earnings_projections_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Analyzing management guidance", "management_guidance_flow", symbol)
    management_guidance_analysis: ManagementGuidanceAnalysis = await management_guidance_flow(
        symbol,
        historical_earnings_analysis,
        financial_statements_analysis,
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Management guidance analysis complete", "management_guidance_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Identifying peer group", "peer_group_analysis", symbol)
    peer_group: PeerGroup = await peer_group_agent(symbol, financial_statements_analysis)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Peer group identification complete", "peer_group_analysis", symbol)

    await peer_group_reporting_task(symbol, peer_group)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Performing forward PE sanity check", "forward_pe_sanity_check_flow", symbol)
    forward_pe_sanity_check: ForwardPeSanityCheck = await forward_pe_sanity_check_flow(symbol, force_recompute=force_recompute)
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Forward PE sanity check complete", "forward_pe_sanity_check_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Calculating forward PE analysis", "forward_pe_flow", symbol)
    forward_pe_flow_result: ForwardPeValuation = await forward_pe_flow(
        symbol,
        peer_group,
        earnings_projections_analysis,
        management_guidance_analysis,
        forward_pe_sanity_check,
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Forward PE analysis complete", "forward_pe_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Analyzing news sentiment", "news_sentiment_flow", symbol)
    news_sentiment_flow_result: NewsSentimentSummary = await news_sentiment_flow(
        symbol,
        peer_group,
        earnings_projections_analysis,
        management_guidance_analysis,
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "News sentiment analysis complete", "news_sentiment_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Cross-referencing analysis", "cross_reference_flow", symbol)
    cross_reference_flow_result: List[CrossReferencedAnalysisCompletion] = await cross_reference_flow(
        symbol,
        forward_pe_flow_result,
        news_sentiment_flow_result,
        historical_earnings_analysis,
        financial_statements_analysis,
        earnings_projections_analysis,
        management_guidance_analysis,
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Cross-reference analysis complete", "cross_reference_flow", symbol)

    await update_job_status_task(job_id, JobStatus.RUNNING, "Generating trade ideas", "trade_ideas_flow", symbol)
    trade_ideas_flow_result: TradeIdea = await trade_ideas_flow(
        symbol,
        forward_pe_flow_result,
        news_sentiment_flow_result,
        historical_earnings_analysis,
        financial_statements_analysis,
        earnings_projections_analysis,
        management_guidance_analysis,
        force_recompute=force_recompute
    )
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Trade ideas generation complete", "trade_ideas_flow", symbol)

    # Collect all analyses for comprehensive report
    all_analyses = {
        "symbol": symbol,
        "analysis_date": get_current_date(),
        "company_overview_analysis": company_overview_analysis.model_dump(),
        "global_quote_data": global_quote_data.model_dump(),
        "historical_earnings_analysis": historical_earnings_analysis.model_dump(),
        "financial_statements_analysis": financial_statements_analysis.model_dump(),
        "earnings_projections_analysis": earnings_projections_analysis.model_dump(),
        "management_guidance_analysis": management_guidance_analysis.model_dump(),
        "peer_group": peer_group.model_dump(),
        "forward_pe_sanity_check": forward_pe_sanity_check.model_dump(),
        "forward_pe_valuation": forward_pe_flow_result.model_dump(),
        "news_sentiment_summary": news_sentiment_flow_result.model_dump(),
        "cross_reference": [item.model_dump() for item in cross_reference_flow_result],
        "trade_idea": trade_ideas_flow_result.model_dump()
    }

    # Generate comprehensive report
    await update_job_status_task(job_id, JobStatus.RUNNING, "Generating comprehensive report", "comprehensive_report_flow", symbol)
    comprehensive_report: ComprehensiveReport = await comprehensive_report_flow(
        symbol,
        all_analyses,
        force_recompute=force_recompute
    )
    logger.info(f"Comprehensive report generated for {symbol}")
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Comprehensive report generation complete", "comprehensive_report_flow", symbol)

    # Generate key insights from comprehensive report
    await update_job_status_task(job_id, JobStatus.RUNNING, "Extracting key insights", "key_insights_flow", symbol)
    key_insights: KeyInsights = await key_insights_flow(
        symbol,
        comprehensive_report,
        force_recompute=force_recompute
    )
    logger.info(f"Key insights generated for {symbol}")
    await update_job_status_task(job_id, JobStatus.COMPLETED, "Key insights extraction complete", "key_insights_flow", symbol)

    duration_seconds = int(time.time() - start_time)
    logger.info(f"Main research for {symbol} completed successfully! in {duration_seconds} seconds")

    # Print token usage summary
    TokenLoggerHook.print_summary()

    # Log token summary to Supabase
    token_totals = TokenLoggerHook.get_totals()
    log_info(
        component="main_research_flow",
        message=f"Research flow completed for {symbol}",
        job_id=job_id,
        symbol=symbol,
        metadata={
            "duration_seconds": duration_seconds,
            "token_usage": TokenLoggerHook.get_summary_dict(),
            "total_tokens": token_totals["total_tokens"],
            "total_input_tokens": token_totals["total_input_tokens"],
            "total_output_tokens": token_totals["total_output_tokens"],
            "total_requests": token_totals["total_requests"],
            "agent_count": token_totals["agent_count"]
        }
    )

    return {
        "symbol": symbol,
        "comprehensive_report": comprehensive_report.model_dump(),
        "key_insights": key_insights.model_dump(),
        "token_usage": TokenLoggerHook.get_summary_dict()
    }
