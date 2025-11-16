"""AI agent for analyzing management guidance from earnings calls."""

import logging
from typing import Dict, Any, Optional
from agents import Agent, Runner, RunResult
from src.lib.llm_model import get_model
from src.lib.token_logger_hook import TokenLoggerHook
from src.research.management_guidance.management_guidance_models import ManagementGuidanceData, ManagementGuidanceAnalysis, GuidanceTone, GuidanceConfidence, ConsensusValidationSignal

log = logging.getLogger(__name__)

management_guidance_analysis_agent = Agent(
    name="Management Guidance Analyst",
    model=get_model(),
    output_type=ManagementGuidanceAnalysis,
    instructions="""
    Extract and validate management guidance from earnings transcripts against consensus estimates.

    ENUM REQUIREMENTS:
    - overall_guidance_tone: GuidanceTone (OPTIMISTIC, CAUTIOUS, NEUTRAL, PESSIMISTIC, MIXED_SIGNALS)
    - guidance_direction fields: GuidanceDirection (POSITIVE, NEGATIVE, NEUTRAL, UNCLEAR)
    - consensus_validation_signal: ConsensusValidationSignal (BULLISH, BEARISH, NEUTRAL, MIXED)

    ANALYSIS APPROACH:
    - Extract forward-looking statements on revenue, margins, expenses, EPS
    - Flag evasive language: vague terms, buzzwords without metrics, blame deflection
    - Cross-check against historical patterns (conservative vs aggressive guidance history)
    - Validate against recent financial trends from other analyses
    
    CONSENSUS VALIDATION:
    - BULLISH: Guidance suggests upside + context supports
    - BEARISH: Guidance suggests downside + context confirms
    - NEUTRAL: Mixed signals or aligns with consensus
    - MIXED: Conflicting signals needing analysis

    Include critical_insights field with 2-3 key guidance insights for cross-model calibration.
    """
)


async def management_guidance_agent(
    symbol: str,
    guidance_data: ManagementGuidanceData,
    historical_earnings_analysis: Optional[Any] = None,
    financial_statements_analysis: Optional[Any] = None
) -> ManagementGuidanceAnalysis:
    """
    Analyzes management guidance from earnings calls for qualitative risks and opportunities.
    
    This agent extracts key guidance signals from earnings call transcripts to validate
    or challenge consensus earnings estimates, focusing on forward-looking statements
    and management tone that could impact next quarter's performance.
    
    Args:
        symbol: Stock symbol being analyzed
        guidance_data: Management guidance data including transcript and estimates
        historical_earnings_analysis: Optional historical earnings patterns for context
        financial_statements_analysis: Optional recent financial trends for context
        
    Returns:
        ManagementGuidanceAnalysis with extracted guidance indicators and assessment
    """
    log.info(f"Starting management guidance analysis for {symbol}")
    
    # Check if we have transcript data
    if not guidance_data.earnings_transcript:
        log.warning(f"No earnings transcript available for {symbol}")
        return _create_no_transcript_analysis(symbol)
    
    # Extract transcript content
    transcript_content = _extract_transcript_content(guidance_data.earnings_transcript)
    if not transcript_content:
        log.warning(f"Could not extract transcript content for {symbol}")
        return _create_no_transcript_analysis(symbol)
    
    try:
        # Build input with optional context
        input_data = f"symbol: {symbol}, guidance_data: {guidance_data}"
        if historical_earnings_analysis:
            input_data += f", historical_earnings_analysis: {historical_earnings_analysis}"
        if financial_statements_analysis:
            input_data += f", financial_statements_analysis: {financial_statements_analysis}"
        
        # Use the Agent SDK to analyze guidance
        result: RunResult = await Runner.run(
            management_guidance_analysis_agent,
            input=input_data,
            hooks=TokenLoggerHook(symbol=symbol)
        )
        analysis_result: ManagementGuidanceAnalysis = result.final_output
        
        log.info(f"Management guidance analysis completed for {symbol}")
        return analysis_result
        
    except Exception as e:
        log.error(f"Error in management guidance analysis for {symbol}: {e}")
        return _create_error_analysis(symbol, str(e))




def _extract_transcript_content(transcript_data: Dict[str, Any]) -> str:
    """Extracts the actual transcript content from API response."""
    try:
        # Alpha Vantage returns transcript as an array of speaker objects
        if 'transcript' in transcript_data and isinstance(transcript_data['transcript'], list):
            transcript_parts = []
            for speaker_segment in transcript_data['transcript']:
                if isinstance(speaker_segment, dict):
                    speaker = speaker_segment.get('speaker', '')
                    title = speaker_segment.get('title', '')
                    content = speaker_segment.get('content', '')
                    
                    if content:
                        # Format as: Speaker (Title): Content
                        speaker_info = f"{speaker}"
                        if title and title != speaker:
                            speaker_info += f" ({title})"
                        transcript_parts.append(f"{speaker_info}: {content}")
            
            if transcript_parts:
                full_transcript = "\n\n".join(transcript_parts)
                log.info(f"Successfully extracted transcript with {len(transcript_parts)} segments, {len(full_transcript)} characters")
                return full_transcript
        
        # Fallback: Try other possible keys for transcript content
        content_keys = ['transcript', 'content', 'text', 'body']
        
        for key in content_keys:
            if key in transcript_data and transcript_data[key]:
                content = transcript_data[key]
                if isinstance(content, str) and len(content) > 100:
                    return content
        
        # If no direct content, try to extract from nested structures
        if isinstance(transcript_data, dict):
            for value in transcript_data.values():
                if isinstance(value, str) and len(value) > 100:
                    return value
        
        log.warning("Could not find transcript content in response")
        return ""
        
    except Exception as e:
        log.error(f"Error extracting transcript content: {e}")
        return ""


def _create_no_transcript_analysis(symbol: str) -> ManagementGuidanceAnalysis:
    """Creates analysis result when no transcript is available."""
    return ManagementGuidanceAnalysis(
        symbol=symbol,
        quarter_analyzed=None,
        transcript_available=False,
        guidance_indicators=[],
        overall_guidance_tone=GuidanceTone.NEUTRAL,
        risk_factors_mentioned=[],
        opportunities_mentioned=[],
        revenue_guidance_direction=None,
        margin_guidance_direction=None,
        eps_guidance_direction=None,
        guidance_confidence=GuidanceConfidence.LOW,
        consensus_validation_signal=ConsensusValidationSignal.NEUTRAL,
        key_guidance_summary="No earnings call transcript available for analysis",
        long_form_analysis="Management guidance analysis could not be performed due to lack of available earnings call transcript",
        critical_insights="No transcript available - unable to extract guidance signals for model calibration"
    )


def _create_error_analysis(symbol: str, error_msg: str) -> ManagementGuidanceAnalysis:
    """Creates analysis result when an error occurs."""
    return ManagementGuidanceAnalysis(
        symbol=symbol,
        quarter_analyzed=None,
        transcript_available=False,
        guidance_indicators=[],
        overall_guidance_tone=GuidanceTone.NEUTRAL,
        risk_factors_mentioned=[],
        opportunities_mentioned=[],
        revenue_guidance_direction=None,
        margin_guidance_direction=None,
        eps_guidance_direction=None,
        guidance_confidence=GuidanceConfidence.LOW,
        consensus_validation_signal=ConsensusValidationSignal.NEUTRAL,
        key_guidance_summary=f"Analysis failed due to error: {error_msg}",
        long_form_analysis=f"Management guidance analysis encountered an error: {error_msg}",
        critical_insights=f"Analysis failed - unable to extract insights due to error: {error_msg}"
    )


