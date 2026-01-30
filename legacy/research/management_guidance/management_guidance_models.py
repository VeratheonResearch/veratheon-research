"""Pydantic models for management guidance analysis."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import enum


class GuidanceTone(str, enum.Enum):
    OPTIMISTIC = "OPTIMISTIC"
    CAUTIOUS = "CAUTIOUS"
    NEUTRAL = "NEUTRAL"
    PESSIMISTIC = "PESSIMISTIC"
    MIXED_SIGNALS = "MIXED_SIGNALS"


class GuidanceDirection(str, enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    UNCLEAR = "UNCLEAR"


class GuidanceConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ConsensusValidationSignal(str, enum.Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"


class ManagementGuidanceData(BaseModel):
    """Raw data needed for management guidance analysis."""
    
    symbol: str = Field(description="Stock symbol")
    earnings_estimates: Dict[str, Any] = Field(description="Earnings estimates data from Alpha Vantage")
    earnings_transcript: Optional[Dict[str, Any]] = Field(default=None, description="Latest earnings call transcript")
    quarter: Optional[str] = Field(default=None, description="Quarter for the transcript (YYYYQM format)")


class GuidanceIndicator(BaseModel):
    """Individual guidance indicator found in earnings call."""
    
    type: str = Field(description="Type of guidance (revenue, eps, margin, etc.)")
    direction: GuidanceDirection = Field(description="Direction of guidance")
    context: str = Field(description="Context or quote from transcript")
    impact_assessment: str = Field(description="Assessment of potential impact on earnings")


class ManagementGuidanceAnalysis(BaseModel):
    """Results of management guidance analysis."""
    
    symbol: str = Field(description="Stock symbol")
    quarter_analyzed: Optional[str] = Field(description="Quarter of the transcript analyzed")
    transcript_available: bool = Field(description="Whether transcript was available for analysis")
    
    # Core guidance indicators
    guidance_indicators: List[GuidanceIndicator] = Field(default_factory=list, description="Specific guidance indicators found")
    
    # Overall assessment
    overall_guidance_tone: GuidanceTone = Field(description="Overall guidance tone")
    risk_factors_mentioned: List[str] = Field(default_factory=list, description="Key risk factors mentioned by management")
    opportunities_mentioned: List[str] = Field(default_factory=list, description="Key opportunities mentioned by management")
    
    # Forward-looking indicators
    revenue_guidance_direction: Optional[GuidanceDirection] = Field(default=None, description="Revenue guidance direction if mentioned")
    margin_guidance_direction: Optional[GuidanceDirection] = Field(default=None, description="Margin guidance direction if mentioned")
    eps_guidance_direction: Optional[GuidanceDirection] = Field(default=None, description="EPS guidance direction if mentioned")
    
    # Confidence and validation
    consensus_validation_signal: ConsensusValidationSignal = Field(description="Signal for consensus validation")
    key_guidance_summary: str = Field(description="Summary of key guidance points for next quarter")
    
    # Metadata
    long_form_analysis: str = Field(description="Additional analysis notes and context")
    critical_insights: str = Field(description="Critical insights for model calibration across all analyses")