from legacy.research.global_quote.global_quote_models import GlobalQuoteData
import logging
import json
import os

logger = logging.getLogger(__name__)

async def global_quote_reporting_task(symbol: str, quote_data: GlobalQuoteData) -> None:
    """
    Task to generate global quote reporting outputs.
    
    Args:
        symbol: Stock symbol being analyzed
        quote_data: GlobalQuoteData to generate reports for
    """
    logger.info(f"Generating global quote reporting for {symbol}")
    
    # Ensure the output directory exists
    output_dir = f"output/{symbol}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write quote data to JSON file
    json_output_path = f"{output_dir}/global_quote_data.json"
    with open(json_output_path, 'w') as f:
        json.dump(quote_data.model_dump(), f, indent=2)
    
    # Write quote data to markdown report
    md_output_path = f"{output_dir}/global_quote_data.md"
    with open(md_output_path, 'w') as f:
        f.write(f"# Global Quote Data: {symbol}\n\n")
        f.write(f"**Current Price:** ${quote_data.price}\n\n")
    
    logger.info(f"Global quote reporting completed for {symbol}")
    logger.info(f"Reports saved to: {json_output_path}, {md_output_path}")