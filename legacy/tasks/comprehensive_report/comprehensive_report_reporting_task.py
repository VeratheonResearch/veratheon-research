from src.lib.supabase_cache import get_supabase_cache
from src.lib.supabase_rag import get_supabase_rag
from legacy.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def comprehensive_report_reporting_task(symbol: str, comprehensive_report: ComprehensiveReport) -> None:
    """
    Reporting task for comprehensive report analysis.

    Caches the comprehensive report results to Supabase and stores in research_docs for RAG.

    Args:
        symbol: Stock symbol analyzed
        comprehensive_report: ComprehensiveReport model with analysis results
    """
    logger.info(f"Caching comprehensive report results for {symbol}")

    # Cache the report in research_cache table
    cache = get_supabase_cache()
    cache_success = cache.cache_report(
        "comprehensive_report",
        symbol,
        comprehensive_report,
        ttl=24*60*60  # 24 hours
    )

    if cache_success:
        logger.info(f"Successfully cached comprehensive report for {symbol}")
    else:
        logger.warning(f"Failed to cache comprehensive report for {symbol}")

    # Store in research_docs table for RAG functionality
    if comprehensive_report.comprehensive_analysis:
        rag = get_supabase_rag()
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = f"Comprehensive Research Report - {symbol.upper()} - {date_str}"

        # Count approximate tokens (rough estimate: ~4 chars per token)
        token_count = len(comprehensive_report.comprehensive_analysis) // 4

        rag_success = rag.add_document(
            content=comprehensive_report.comprehensive_analysis,
            title=title,
            symbol=symbol,
            report_type="comprehensive_report",
            embedding=None,  # Embedding can be generated later via batch job
            metadata={
                "generated_at": datetime.now().isoformat(),
                "report_date": date_str
            },
            token_count=token_count
        )

        if rag_success:
            logger.info(f"Successfully stored comprehensive report in research_docs for {symbol}")
        else:
            logger.warning(f"Failed to store comprehensive report in research_docs for {symbol}")

    # Note: We don't raise exceptions here because caching/storage failure
    # shouldn't break the analysis flow