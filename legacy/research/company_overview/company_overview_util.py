import logging
from typing import Dict, Any
from src.lib.alpha_vantage_api import call_alpha_vantage_overview
from legacy.research.company_overview.company_overview_models import CompanyOverviewData

log = logging.getLogger(__name__)


def get_company_overview_data_for_symbol(symbol: str) -> CompanyOverviewData:
    """
    Calls Alpha Vantage API to fetch comprehensive company overview data.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        CompanyOverviewData containing all company overview information from Alpha Vantage
    """
    try:
        # Get company overview data from Alpha Vantage
        overview_data = call_alpha_vantage_overview(symbol)
        
        # Create CompanyOverviewData object with safe field mapping
        company_overview = CompanyOverviewData(
            symbol=overview_data.get('Symbol', symbol),
            asset_type=overview_data.get('AssetType'),
            name=overview_data.get('Name'),
            description=overview_data.get('Description'),
            cik=overview_data.get('CIK'),
            exchange=overview_data.get('Exchange'),
            currency=overview_data.get('Currency'),
            country=overview_data.get('Country'),
            sector=overview_data.get('Sector'),
            industry=overview_data.get('Industry'),
            address=overview_data.get('Address'),
            fiscal_year_end=overview_data.get('FiscalYearEnd'),
            latest_quarter=overview_data.get('LatestQuarter'),
            market_capitalization=overview_data.get('MarketCapitalization'),
            ebitda=overview_data.get('EBITDA'),
            pe_ratio=overview_data.get('PERatio'),
            peg_ratio=overview_data.get('PEGRatio'),
            book_value=overview_data.get('BookValue'),
            dividend_per_share=overview_data.get('DividendPerShare'),
            dividend_yield=overview_data.get('DividendYield'),
            eps=overview_data.get('EPS'),
            revenue_per_share_ttm=overview_data.get('RevenuePerShareTTM'),
            profit_margin=overview_data.get('ProfitMargin'),
            operating_margin_ttm=overview_data.get('OperatingMarginTTM'),
            return_on_assets_ttm=overview_data.get('ReturnOnAssetsTTM'),
            return_on_equity_ttm=overview_data.get('ReturnOnEquityTTM'),
            revenue_ttm=overview_data.get('RevenueTTM'),
            gross_profit_ttm=overview_data.get('GrossProfitTTM'),
            diluted_eps_ttm=overview_data.get('DilutedEPSTTM'),
            quarterly_earnings_growth_yoy=overview_data.get('QuarterlyEarningsGrowthYOY'),
            quarterly_revenue_growth_yoy=overview_data.get('QuarterlyRevenueGrowthYOY'),
            analyst_target_price=overview_data.get('AnalystTargetPrice'),
            trailing_pe=overview_data.get('TrailingPE'),
            forward_pe=overview_data.get('ForwardPE'),
            price_to_sales_ratio_ttm=overview_data.get('PriceToSalesRatioTTM'),
            price_to_book_ratio=overview_data.get('PriceToBookRatio'),
            ev_to_revenue=overview_data.get('EVToRevenue'),
            ev_to_ebitda=overview_data.get('EVToEBITDA'),
            beta=overview_data.get('Beta'),
            week_52_high=overview_data.get('52WeekHigh'),
            week_52_low=overview_data.get('52WeekLow'),
            day_50_moving_average=overview_data.get('50DayMovingAverage'),
            day_200_moving_average=overview_data.get('200DayMovingAverage'),
            shares_outstanding=overview_data.get('SharesOutstanding'),
            dividend_date=overview_data.get('DividendDate'),
            ex_dividend_date=overview_data.get('ExDividendDate')
        )
        
        log.info(f"Successfully retrieved company overview data for {symbol}")
        return company_overview
        
    except Exception as e:
        log.error(f"Failed to get company overview data for symbol: {symbol}. Error: {e}")
        # Return minimal data structure to allow graceful handling
        return CompanyOverviewData(
            symbol=symbol
        )