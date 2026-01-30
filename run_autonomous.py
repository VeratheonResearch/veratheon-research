#!/usr/bin/env python3
"""
CLI runner for the Veratheon autonomous research workflow.

Usage:
    uv run python run_autonomous.py AAPL
    uv run python run_autonomous.py MSFT
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logging.getLogger('LiteLLM').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import the workflow after setting up the path
from src.agents.workflow import run_autonomous_workflow, format_workflow_result


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Veratheon autonomous research workflow for a stock symbol."
    )
    parser.add_argument(
        "symbol",
        type=str,
        help="Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


async def main():
    """Run the autonomous research workflow."""
    args = parse_args()
    symbol = args.symbol.upper().strip()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info(f"Starting autonomous research for {symbol}")

        # Run the workflow
        result = await run_autonomous_workflow(symbol)

        # Display the result
        print(format_workflow_result(result))

        if result.error:
            logger.error(f"Workflow completed with error: {result.error}")
            return 1

        logger.info("Autonomous research completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Error running autonomous research: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
