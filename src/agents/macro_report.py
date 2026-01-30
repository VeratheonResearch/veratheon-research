"""
Macro Economic Report - Data Fetcher (No LLM)

This module fetches economic indicators from Alpha Vantage to provide
macro context for investment decisions. It is a checklist-driven data
lookup, not an LLM analysis.

Indicators fetched:
- Inflation: CPI, Inflation rate
- Employment: Non-Farm Payrolls, Unemployment Rate
- Interest Rates: Fed Funds Rate, 10-Year Treasury, 2-Year Treasury
- Growth: Real GDP
- Volatility: VIX
- Market: S&P 500 (via SPY)
- Sector: Sector ETF performance (based on company sector)
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.lib.clients.alpha_vantage_client import AlphaVantageClient


@dataclass
class EconomicIndicator:
    """Single economic indicator with value and context."""
    name: str
    value: Optional[str] = None
    previous_value: Optional[str] = None
    date: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    context: Optional[str] = None
    error: Optional[str] = None


@dataclass
class MarketIndicator:
    """Market/volatility indicator."""
    name: str
    symbol: str
    price: Optional[str] = None
    change: Optional[str] = None
    change_percent: Optional[str] = None
    date: Optional[str] = None
    error: Optional[str] = None


@dataclass
class MacroReport:
    """Complete macro economic report."""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Inflation
    cpi: Optional[EconomicIndicator] = None
    inflation: Optional[EconomicIndicator] = None

    # Employment
    unemployment: Optional[EconomicIndicator] = None
    nonfarm_payroll: Optional[EconomicIndicator] = None

    # Interest Rates
    fed_funds_rate: Optional[EconomicIndicator] = None
    treasury_10y: Optional[EconomicIndicator] = None
    treasury_2y: Optional[EconomicIndicator] = None

    # Growth
    real_gdp: Optional[EconomicIndicator] = None

    # Volatility & Market
    vix: Optional[MarketIndicator] = None
    sp500: Optional[MarketIndicator] = None

    # Sector (optional, based on company)
    sector_etf: Optional[MarketIndicator] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "generated_at": self.generated_at,
            "inflation": {},
            "employment": {},
            "interest_rates": {},
            "growth": {},
            "market": {},
        }

        # Inflation
        if self.cpi:
            result["inflation"]["cpi"] = self._indicator_to_dict(self.cpi)
        if self.inflation:
            result["inflation"]["inflation_rate"] = self._indicator_to_dict(self.inflation)

        # Employment
        if self.unemployment:
            result["employment"]["unemployment_rate"] = self._indicator_to_dict(self.unemployment)
        if self.nonfarm_payroll:
            result["employment"]["nonfarm_payroll"] = self._indicator_to_dict(self.nonfarm_payroll)

        # Interest Rates
        if self.fed_funds_rate:
            result["interest_rates"]["fed_funds_rate"] = self._indicator_to_dict(self.fed_funds_rate)
        if self.treasury_10y:
            result["interest_rates"]["treasury_10y"] = self._indicator_to_dict(self.treasury_10y)
        if self.treasury_2y:
            result["interest_rates"]["treasury_2y"] = self._indicator_to_dict(self.treasury_2y)

        # Growth
        if self.real_gdp:
            result["growth"]["real_gdp"] = self._indicator_to_dict(self.real_gdp)

        # Market
        if self.vix:
            result["market"]["vix"] = self._market_to_dict(self.vix)
        if self.sp500:
            result["market"]["sp500"] = self._market_to_dict(self.sp500)
        if self.sector_etf:
            result["market"]["sector_etf"] = self._market_to_dict(self.sector_etf)

        return result

    def _indicator_to_dict(self, indicator: EconomicIndicator) -> dict:
        return {
            "name": indicator.name,
            "value": indicator.value,
            "previous_value": indicator.previous_value,
            "date": indicator.date,
            "trend": indicator.trend,
            "context": indicator.context,
            "error": indicator.error,
        }

    def _market_to_dict(self, indicator: MarketIndicator) -> dict:
        return {
            "name": indicator.name,
            "symbol": indicator.symbol,
            "price": indicator.price,
            "change": indicator.change,
            "change_percent": indicator.change_percent,
            "date": indicator.date,
            "error": indicator.error,
        }

    def format_report(self) -> str:
        """Format the macro report as a readable string."""
        lines = [
            "MACRO ECONOMIC INDICATORS",
            "=" * 50,
            "",
        ]

        # Inflation Section
        lines.append("📈 INFLATION")
        lines.append("-" * 30)
        if self.cpi and self.cpi.value:
            trend_arrow = self._get_trend_arrow(self.cpi.trend)
            # CPI is an index, not a percentage
            lines.append(f"  CPI Index: {self.cpi.value} {trend_arrow}")
            if self.cpi.date:
                lines.append(f"       (as of {self.cpi.date})")
        if self.inflation and self.inflation.value:
            trend_arrow = self._get_trend_arrow(self.inflation.trend)
            try:
                inflation_val = float(self.inflation.value)
                lines.append(f"  Inflation Rate: {inflation_val:.1f}% {trend_arrow}")
            except (ValueError, TypeError):
                lines.append(f"  Inflation Rate: {self.inflation.value}% {trend_arrow}")
            if self.inflation.context:
                lines.append(f"       {self.inflation.context}")
        lines.append("")

        # Employment Section
        lines.append("👥 EMPLOYMENT")
        lines.append("-" * 30)
        if self.unemployment and self.unemployment.value:
            trend_arrow = self._get_trend_arrow(self.unemployment.trend, invert=True)
            lines.append(f"  Unemployment: {self.unemployment.value}% {trend_arrow}")
        if self.nonfarm_payroll and self.nonfarm_payroll.value:
            trend_arrow = self._get_trend_arrow(self.nonfarm_payroll.trend)
            # Non-farm payrolls are in thousands, format as millions
            try:
                payroll_k = float(self.nonfarm_payroll.value)
                payroll_m = payroll_k / 1000
                lines.append(f"  Non-Farm Payrolls: {payroll_m:.1f}M {trend_arrow}")
            except (ValueError, TypeError):
                lines.append(f"  Non-Farm Payrolls: {self.nonfarm_payroll.value} {trend_arrow}")
        lines.append("")

        # Interest Rates Section
        lines.append("💰 INTEREST RATES")
        lines.append("-" * 30)
        if self.fed_funds_rate and self.fed_funds_rate.value:
            lines.append(f"  Fed Funds Rate: {self.fed_funds_rate.value}%")
        if self.treasury_10y and self.treasury_10y.value:
            trend_arrow = self._get_trend_arrow(self.treasury_10y.trend)
            lines.append(f"  10-Year Treasury: {self.treasury_10y.value}% {trend_arrow}")
        if self.treasury_2y and self.treasury_2y.value:
            trend_arrow = self._get_trend_arrow(self.treasury_2y.trend)
            lines.append(f"  2-Year Treasury: {self.treasury_2y.value}% {trend_arrow}")

        # Yield curve context
        if self.treasury_10y and self.treasury_2y:
            try:
                spread = float(self.treasury_10y.value) - float(self.treasury_2y.value)
                curve_status = "inverted (recessionary signal)" if spread < 0 else "normal"
                lines.append(f"  Yield Curve: {spread:.2f}% spread ({curve_status})")
            except (ValueError, TypeError):
                pass
        lines.append("")

        # Growth Section
        lines.append("📊 ECONOMIC GROWTH")
        lines.append("-" * 30)
        if self.real_gdp and self.real_gdp.value:
            trend_arrow = self._get_trend_arrow(self.real_gdp.trend)
            # GDP value is in billions, calculate QoQ growth rate if we have previous
            try:
                current_gdp = float(self.real_gdp.value)
                if self.real_gdp.previous_value:
                    prev_gdp = float(self.real_gdp.previous_value)
                    growth_rate = ((current_gdp - prev_gdp) / prev_gdp) * 100
                    # Annualize quarterly growth (multiply by 4)
                    annualized_growth = growth_rate * 4
                    lines.append(f"  Real GDP: ${current_gdp:.0f}B ({annualized_growth:+.1f}% annualized) {trend_arrow}")
                    if annualized_growth < 0:
                        lines.append("       Economic contraction")
                    elif annualized_growth < 1:
                        lines.append("       Slow growth")
                    elif annualized_growth < 2.5:
                        lines.append("       Moderate growth")
                    else:
                        lines.append("       Strong growth")
                else:
                    lines.append(f"  Real GDP: ${current_gdp:.0f}B")
            except (ValueError, TypeError):
                lines.append(f"  Real GDP: {self.real_gdp.value}")
        lines.append("")

        # Market Section
        lines.append("📉 MARKET INDICATORS")
        lines.append("-" * 30)
        if self.vix and self.vix.price:
            vix_level = self._get_vix_level(self.vix.price)
            change_str = f" ({self.vix.change_percent})" if self.vix.change_percent else ""
            lines.append(f"  VIX: {self.vix.price}{change_str} - {vix_level}")
        if self.sp500 and self.sp500.price:
            change_str = f" ({self.sp500.change_percent})" if self.sp500.change_percent else ""
            lines.append(f"  S&P 500 (SPY): ${self.sp500.price}{change_str}")
        if self.sector_etf and self.sector_etf.price:
            change_str = f" ({self.sector_etf.change_percent})" if self.sector_etf.change_percent else ""
            lines.append(f"  Sector ({self.sector_etf.symbol}): ${self.sector_etf.price}{change_str}")
        lines.append("")

        lines.append("=" * 50)
        lines.append(f"Generated: {self.generated_at}")

        return "\n".join(lines)

    def _get_trend_arrow(self, trend: Optional[str], invert: bool = False) -> str:
        """Get trend arrow (invert for metrics where down is good)."""
        if not trend:
            return ""
        if invert:
            arrows = {"up": "↑ (worse)", "down": "↓ (better)", "stable": "→"}
        else:
            arrows = {"up": "↑", "down": "↓", "stable": "→"}
        return arrows.get(trend, "")

    def _get_vix_level(self, vix_value: str) -> str:
        """Interpret VIX level."""
        try:
            vix = float(vix_value)
            if vix < 15:
                return "Low volatility (complacent)"
            elif vix < 20:
                return "Normal volatility"
            elif vix < 25:
                return "Elevated volatility"
            elif vix < 30:
                return "High volatility (fear)"
            else:
                return "Extreme volatility (panic)"
        except (ValueError, TypeError):
            return "Unknown"


# Sector to ETF mapping
SECTOR_ETF_MAP = {
    "Technology": "XLK",
    "Information Technology": "XLK",
    "Healthcare": "XLV",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Financial Services": "XLF",
    "Consumer Discretionary": "XLY",
    "Consumer Cyclical": "XLY",
    "Consumer Staples": "XLP",
    "Consumer Defensive": "XLP",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
    "Basic Materials": "XLB",
    "Communication Services": "XLC",
    "Communication": "XLC",
}


class MacroReportFetcher:
    """Fetches macro economic data from Alpha Vantage."""

    def __init__(self):
        self.client = AlphaVantageClient()

    async def fetch_economic_indicator(
        self,
        function: str,
        name: str,
        interval: str = "monthly",
        maturity: Optional[str] = None
    ) -> EconomicIndicator:
        """
        Fetch an economic indicator from Alpha Vantage.

        Args:
            function: Alpha Vantage function name (e.g., "CPI", "UNEMPLOYMENT")
            name: Human-readable name
            interval: Data interval ("monthly", "quarterly", "annual")
            maturity: For treasury yields (e.g., "10year", "2year")
        """
        indicator = EconomicIndicator(name=name)

        try:
            query = f"{function}&interval={interval}"
            if maturity:
                query = f"{function}&interval={interval}&maturity={maturity}"

            data = await asyncio.to_thread(self.client.run_query, query)

            if "Error Message" in data or "Information" in data:
                indicator.error = data.get("Error Message") or data.get("Information")
                return indicator

            # Parse the data - Alpha Vantage returns "data" array
            data_points = data.get("data", [])
            if not data_points:
                indicator.error = "No data available"
                return indicator

            # Get latest and previous values
            latest = data_points[0] if len(data_points) > 0 else None
            previous = data_points[1] if len(data_points) > 1 else None

            if latest:
                indicator.value = latest.get("value")
                indicator.date = latest.get("date")

            if previous:
                indicator.previous_value = previous.get("value")

            # Calculate trend
            if indicator.value and indicator.previous_value:
                try:
                    curr = float(indicator.value)
                    prev = float(indicator.previous_value)
                    if curr > prev:
                        indicator.trend = "up"
                    elif curr < prev:
                        indicator.trend = "down"
                    else:
                        indicator.trend = "stable"
                except (ValueError, TypeError):
                    pass

            # Add context based on indicator type
            indicator.context = self._get_indicator_context(function, indicator.value)

        except Exception as e:
            indicator.error = str(e)

        return indicator

    async def fetch_market_quote(
        self,
        symbol: str,
        name: str
    ) -> MarketIndicator:
        """Fetch market quote for a symbol (VIX, SPY, sector ETF)."""
        indicator = MarketIndicator(name=name, symbol=symbol)

        try:
            data = await asyncio.to_thread(
                self.client.run_query,
                f"GLOBAL_QUOTE&symbol={symbol}"
            )

            if "Error Message" in data or "Information" in data:
                indicator.error = data.get("Error Message") or data.get("Information")
                return indicator

            quote = data.get("Global Quote", {})
            if not quote:
                indicator.error = "No quote data available"
                return indicator

            indicator.price = quote.get("05. price")
            indicator.change = quote.get("09. change")
            indicator.change_percent = quote.get("10. change percent")
            indicator.date = quote.get("07. latest trading day")

        except Exception as e:
            indicator.error = str(e)

        return indicator

    def _get_indicator_context(self, function: str, value: Optional[str]) -> Optional[str]:
        """Provide context for indicator values."""
        if not value:
            return None

        try:
            val = float(value)

            if function == "CPI":
                # CPI is an index, not a rate
                return None

            if function == "INFLATION":
                if val < 2:
                    return "Below Fed's 2% target"
                elif val <= 2.5:
                    return "Near Fed's 2% target"
                elif val <= 4:
                    return "Above target, moderately elevated"
                else:
                    return "Significantly elevated"

            if function == "UNEMPLOYMENT":
                if val < 4:
                    return "Very tight labor market"
                elif val < 5:
                    return "Healthy employment"
                elif val < 6:
                    return "Moderately weak"
                else:
                    return "Elevated unemployment"

            if function == "REAL_GDP":
                if val < 0:
                    return "Economic contraction"
                elif val < 1:
                    return "Slow growth"
                elif val < 2.5:
                    return "Moderate growth"
                else:
                    return "Strong growth"

            if function == "FEDERAL_FUNDS_RATE":
                if val < 1:
                    return "Very accommodative policy"
                elif val < 3:
                    return "Moderately accommodative"
                elif val < 5:
                    return "Neutral to restrictive"
                else:
                    return "Restrictive policy"

        except (ValueError, TypeError):
            pass

        return None

    async def fetch_full_report(self, sector: Optional[str] = None) -> MacroReport:
        """
        Fetch the complete macro economic report.

        Args:
            sector: Optional company sector to fetch sector ETF performance

        Returns:
            MacroReport with all indicators populated

        Note:
            Uses batched requests with delays to avoid Alpha Vantage rate limits
            (5 requests per minute for free tier).
        """
        report = MacroReport()
        result_map = {}

        # Batch 1: Inflation and Employment (4 requests)
        batch1 = {
            "cpi": self.fetch_economic_indicator("CPI", "Consumer Price Index", "monthly"),
            "inflation": self.fetch_economic_indicator("INFLATION", "Inflation Rate", "annual"),
            "unemployment": self.fetch_economic_indicator("UNEMPLOYMENT", "Unemployment Rate", "monthly"),
            "nonfarm": self.fetch_economic_indicator("NONFARM_PAYROLL", "Non-Farm Payrolls", "monthly"),
        }
        results1 = await asyncio.gather(*batch1.values(), return_exceptions=True)
        result_map.update(dict(zip(batch1.keys(), results1)))

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

        # Batch 2: Interest Rates (3 requests)
        batch2 = {
            "fed_funds": self.fetch_economic_indicator("FEDERAL_FUNDS_RATE", "Federal Funds Rate", "monthly"),
            "treasury_10y": self.fetch_economic_indicator("TREASURY_YIELD", "10-Year Treasury", "monthly", "10year"),
            "treasury_2y": self.fetch_economic_indicator("TREASURY_YIELD", "2-Year Treasury", "monthly", "2year"),
        }
        results2 = await asyncio.gather(*batch2.values(), return_exceptions=True)
        result_map.update(dict(zip(batch2.keys(), results2)))

        # Small delay to avoid rate limiting
        await asyncio.sleep(0.5)

        # Batch 3: Growth and Market (3-4 requests)
        batch3 = {
            "gdp": self.fetch_economic_indicator("REAL_GDP", "Real GDP Growth", "quarterly"),
            "vix": self.fetch_market_quote("VIXY", "CBOE Volatility Index"),  # VIXY is the VIX ETF
            "sp500": self.fetch_market_quote("SPY", "S&P 500 ETF"),
        }

        # Add sector ETF if sector provided
        if sector:
            etf_symbol = SECTOR_ETF_MAP.get(sector)
            if etf_symbol:
                batch3["sector"] = self.fetch_market_quote(etf_symbol, f"{sector} Sector ETF")

        results3 = await asyncio.gather(*batch3.values(), return_exceptions=True)
        result_map.update(dict(zip(batch3.keys(), results3)))

        # Populate report
        report.cpi = result_map.get("cpi") if not isinstance(result_map.get("cpi"), Exception) else None
        report.inflation = result_map.get("inflation") if not isinstance(result_map.get("inflation"), Exception) else None
        report.unemployment = result_map.get("unemployment") if not isinstance(result_map.get("unemployment"), Exception) else None
        report.nonfarm_payroll = result_map.get("nonfarm") if not isinstance(result_map.get("nonfarm"), Exception) else None
        report.fed_funds_rate = result_map.get("fed_funds") if not isinstance(result_map.get("fed_funds"), Exception) else None
        report.treasury_10y = result_map.get("treasury_10y") if not isinstance(result_map.get("treasury_10y"), Exception) else None
        report.treasury_2y = result_map.get("treasury_2y") if not isinstance(result_map.get("treasury_2y"), Exception) else None
        report.real_gdp = result_map.get("gdp") if not isinstance(result_map.get("gdp"), Exception) else None
        report.vix = result_map.get("vix") if not isinstance(result_map.get("vix"), Exception) else None
        report.sp500 = result_map.get("sp500") if not isinstance(result_map.get("sp500"), Exception) else None

        if "sector" in result_map and not isinstance(result_map.get("sector"), Exception):
            report.sector_etf = result_map["sector"]

        return report


async def fetch_macro_report(sector: Optional[str] = None) -> MacroReport:
    """
    Main entry point for fetching the macro economic report.

    Args:
        sector: Optional company sector for sector-specific ETF data

    Returns:
        MacroReport with all economic indicators
    """
    fetcher = MacroReportFetcher()
    return await fetcher.fetch_full_report(sector=sector)
