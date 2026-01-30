"""Utility functions for management guidance analysis."""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from src.lib.alpha_vantage_api import call_alpha_vantage_earnings_estimates, call_alpha_vantage_earnings_call_transcripts
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceData

log = logging.getLogger(__name__)


def get_management_guidance_data_for_symbol(symbol: str) -> ManagementGuidanceData:
    """
    Fetches management guidance data including earnings estimates and latest transcript.
    
    Args:
        symbol: Stock symbol to research
        
    Returns:
        ManagementGuidanceData containing earnings estimates and transcript (if available)
    """
    try:
        # Get earnings estimates to find the most recent quarter
        earnings_estimates = call_alpha_vantage_earnings_estimates(symbol)
        
        # Determine the most recent completed quarter for transcript lookup
        quarter = _determine_latest_transcript_quarter()
        
        # Try to get the earnings call transcript for the recent quarter
        earnings_transcript = None
        try:
            earnings_transcript = call_alpha_vantage_earnings_call_transcripts(symbol, quarter)
            log.info(f"Retrieved earnings transcript for {symbol} Q{quarter}")
        except Exception as transcript_error:
            log.warning(f"Could not retrieve earnings transcript for {symbol} Q{quarter}: {transcript_error}")
            # Try previous quarter as backup
            try:
                prev_quarter = _get_previous_quarter(quarter)
                earnings_transcript = call_alpha_vantage_earnings_call_transcripts(symbol, prev_quarter)
                quarter = prev_quarter
                log.info(f"Retrieved earnings transcript for {symbol} Q{prev_quarter} (fallback)")
            except Exception as prev_error:
                log.warning(f"Could not retrieve earnings transcript for previous quarter either: {prev_error}")
        
        guidance_data = ManagementGuidanceData(
            symbol=symbol,
            earnings_estimates=earnings_estimates,
            earnings_transcript=earnings_transcript,
            quarter=quarter if earnings_transcript else None
        )
        
        log.info(f"Successfully retrieved management guidance data for {symbol}")
        return guidance_data
        
    except Exception as e:
        log.error(f"Failed to get management guidance data for symbol: {symbol}. Error: {e}")
        return ManagementGuidanceData(
            symbol=symbol,
            earnings_estimates={},
            earnings_transcript=None,
            quarter=None
        )


def _determine_latest_transcript_quarter() -> str:
    """
    Determines the most recent quarter that would have a transcript available.
    Assumes transcripts are available ~1-2 months after quarter end.
    
    Returns:
        Quarter string in YYYYQM format (e.g., "2024Q1")
    """
    now = datetime.now()
    
    # Determine current calendar quarter and year
    current_month = now.month
    current_year = now.year
    
    # Map months to quarters
    if current_month <= 3:
        # Q1: Jan-Mar, likely have Q4 of previous year transcript
        return f"{current_year - 1}Q4"
    elif current_month <= 6:
        # Q2: Apr-Jun, likely have Q1 transcript  
        return f"{current_year}Q1"
    elif current_month <= 9:
        # Q3: Jul-Sep, likely have Q2 transcript
        return f"{current_year}Q2"
    else:
        # Q4: Oct-Dec, likely have Q3 transcript
        return f"{current_year}Q3"


def _get_previous_quarter(quarter: str) -> str:
    """
    Gets the previous quarter from a given quarter string.
    
    Args:
        quarter: Quarter in YYYYQM format
        
    Returns:
        Previous quarter in YYYYQM format
    """
    year = int(quarter[:4])
    q = int(quarter[5:])
    
    if q == 1:
        return f"{year - 1}Q4"
    else:
        return f"{year}Q{q - 1}"


def extract_latest_earnings_estimate(earnings_estimates: Dict[str, Any]) -> Optional[Tuple[str, float]]:
    """
    Extracts the latest quarterly earnings estimate from earnings estimates data.
    
    Args:
        earnings_estimates: Earnings estimates data from Alpha Vantage
        
    Returns:
        Tuple of (fiscal_date_ending, estimated_eps) for the next quarter, or None if not found
    """
    try:
        # Look for the most recent quarterly estimate
        estimates = earnings_estimates.get('quarterlyEstimates', [])
        if not estimates:
            return None
            
        # Sort by fiscal date ending to get the latest
        sorted_estimates = sorted(estimates, key=lambda x: x.get('fiscalDateEnding', ''), reverse=True)
        latest = sorted_estimates[0]
        
        fiscal_date = latest.get('fiscalDateEnding')
        estimated_eps = latest.get('estimatedEPS')
        
        if fiscal_date and estimated_eps is not None:
            return (fiscal_date, float(estimated_eps))
            
    except Exception as e:
        log.warning(f"Error extracting latest earnings estimate: {e}")
    
    return None