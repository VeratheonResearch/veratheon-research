import json
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
from src.research.comprehensive_report.comprehensive_report_agent import comprehensive_report_agent
from src.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

async def comprehensive_report_task(
    symbol: str,
    all_analyses: Dict[str, Any]
) -> ComprehensiveReport:
    """
    Task to generate comprehensive investment research report by synthesizing all analyses.

    Args:
        symbol: Stock symbol to research
        all_analyses: Dictionary containing all analysis results from the research pipeline
        
    Returns:
        ComprehensiveReport containing synthesized research findings
    """
    logger.info(f"Generating comprehensive report for {symbol}")

    # Build comprehensive input with all available analyses
    input_data = f"original_symbol: {symbol}"
    
    # Add each analysis to the input data
    for analysis_key, analysis_data in all_analyses.items():
        if analysis_data:
            input_data += f", {analysis_key}: {analysis_data}"

    result: RunResult = await Runner.run(
        comprehensive_report_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    comprehensive_report: ComprehensiveReport = result.final_output

    return comprehensive_report