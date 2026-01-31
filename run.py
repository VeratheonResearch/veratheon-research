#!/usr/bin/env python3
"""
Direct runner for the autonomous research workflow.
This script directly imports and runs the autonomous research workflow for better debugging.

Usage:
    uv run python run.py AAPL
    uv run python run.py AAPL -v  # verbose mode
"""
import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import the workflow after setting up the path
from src.agents.workflow import run_autonomous_workflow, format_workflow_result


async def main():
    """Run the autonomous research workflow."""
    parser = argparse.ArgumentParser(description="Run autonomous stock research")
    parser.add_argument("symbol", type=str, help="Stock symbol to research (e.g., AAPL)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Configure logging based on verbosity
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    logging.getLogger('LiteLLM').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    try:
        symbol = args.symbol.upper()
        logger.info(f"Starting autonomous research for {symbol}")

        # Run the autonomous workflow
        result = await run_autonomous_workflow(symbol)

        # Format and print results
        formatted = format_workflow_result(result)
        print(formatted)

        if result.error:
            logger.error(f"Workflow completed with errors: {result.error}")
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
