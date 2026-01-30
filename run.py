#!/usr/bin/env python3
"""
Direct runner for the market research flow.
This script directly imports and runs the market research flow for better debugging.
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('LiteLLM').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import the flow after setting up the path
from legacy.flows.research_flow import main_research_flow

async def main():
    """Run the market research flow with example parameters."""
    try:
        # Example parameters - you can modify these or make them command-line arguments
        symbol = "PG"  # Example stock symbol
        
        logger.info(f"Starting market research for {symbol}")
        
        # Run the flow directly
        await main_research_flow(symbol=symbol)
        
        logger.info("Market research completed successfully!")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error running market research: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
