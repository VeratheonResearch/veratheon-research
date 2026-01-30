from legacy.research.company_overview.company_overview_models import CompanyOverviewAnalysis
import logging
import json
import os

logger = logging.getLogger(__name__)

async def company_overview_reporting_task(symbol: str, analysis: CompanyOverviewAnalysis) -> None:
    """
    Task to generate company overview analysis reporting outputs.
    
    Args:
        symbol: Stock symbol being analyzed
        analysis: CompanyOverviewAnalysis to generate reports for
    """
    logger.info(f"Generating company overview reporting for {symbol}")
    
    # Ensure the output directory exists
    output_dir = f"output/{symbol}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write analysis to JSON file
    json_output_path = f"{output_dir}/company_overview_analysis.json"
    with open(json_output_path, 'w') as f:
        json.dump(analysis.model_dump(), f, indent=2)
    
    # Write analysis to markdown report
    md_output_path = f"{output_dir}/company_overview_analysis.md"
    with open(md_output_path, 'w') as f:
        f.write(f"# Company Overview Analysis: {analysis.company_name} ({symbol})\n\n")
        f.write(f"**Sector:** {analysis.sector}\n")
        f.write(f"**Industry:** {analysis.industry}\n")
        f.write(f"**Market Cap Category:** {analysis.market_cap_category}\n\n")
        
        f.write("## Business Description\n")
        f.write(f"{analysis.business_description}\n\n")
        
        f.write("## Key Financials\n")
        f.write(f"{analysis.key_financials}\n\n")
        
        f.write("## Valuation Metrics\n")
        f.write(f"{analysis.valuation_metrics}\n\n")
        
        f.write("## Profitability Assessment\n")
        f.write(f"{analysis.profitability_assessment}\n\n")
        
        f.write("## Growth Indicators\n")
        f.write(f"{analysis.growth_indicators}\n\n")
        
        f.write("## Risk Factors\n")
        f.write(f"{analysis.risk_factors}\n\n")
        
        f.write("## Competitive Position\n")
        f.write(f"{analysis.competitive_position}\n\n")
        
        f.write("## Comprehensive Analysis\n")
        f.write(f"{analysis.long_form_analysis}\n\n")
    
    logger.info(f"Company overview reporting completed for {symbol}")
    logger.info(f"Reports saved to: {json_output_path}, {md_output_path}")