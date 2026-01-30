# server/api.py
import sys
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

# Ensure project root is on the Python path (so imports like src.flows... work)
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import after sys.path setup
from legacy.flows.research_flow import main_research_flow  # noqa: E402
from src.lib.supabase_job_tracker import get_job_tracker, JobStatus  # noqa: E402
from src.lib.alpha_vantage_api import call_alpha_vantage_symbol_search  # noqa: E402
from legacy.research.debug.agent_debug import run_agent_debug, AgentDebugRequest, AgentDebugResponse  # noqa: E402

logging.basicConfig(level=logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(title="Veratheon Research API", version="0.1.0")

class ResearchRequest(BaseModel):
    symbol: str
    force_recompute: bool = False
    model: str = "o4_mini"  # Default to o4_mini

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

async def run_research_background(main_job_id: str, symbol: str, force_recompute: bool, model: str):
    """Background task to run research and update job status."""
    job_tracker = get_job_tracker()

    try:
        # Update status to running (using main_job_id)
        job_tracker.update_job_status(main_job_id, JobStatus.RUNNING, step="Starting research flow", use_main_job_id=True)

        # Run the research flow with main_job_id and model
        result = await main_research_flow(symbol=symbol, force_recompute=force_recompute, job_id=main_job_id, model=model)

        # Mark as completed with result (using main_job_id)
        job_tracker.update_job_status(main_job_id, JobStatus.COMPLETED, step="Research completed", result=result, use_main_job_id=True)

        logger.info(f"Research completed for {symbol} (main_job_id {main_job_id})")

    except Exception as e:
        logger.exception(f"Error running research for {symbol} (main_job_id {main_job_id})")
        job_tracker.update_job_status(main_job_id, JobStatus.FAILED, step="Research failed", error=str(e), use_main_job_id=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/research")
async def start_research(req: ResearchRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Start a research job and return main_job_id for tracking."""
    try:
        symbol_upper = req.symbol.upper()
        logger.info(f"Starting market research job for symbol={symbol_upper}")

        job_tracker = get_job_tracker()

        # Create new job (main job)
        job_result = job_tracker.create_job(
            job_type="research",
            symbol=symbol_upper,
            metadata={
                "force_recompute": req.force_recompute,
                "model": req.model,
                "requested_at": datetime.now().isoformat()
            },
            is_sub_job=False,  # This is the main job
            job_name="main_flow"  # Main flow identifier
        )

        main_job_id = job_result["main_job_id"]

        # Start background task with main_job_id and model
        background_tasks.add_task(run_research_background, main_job_id, req.symbol, req.force_recompute, req.model)

        return JobResponse(
            job_id=main_job_id,  # Return main_job_id (UUID) to UI
            status="pending",
            message=f"Research job started for {symbol_upper}"
        )

    except Exception as e:
        logger.exception("Error starting research job")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report-status/{symbol}")
async def check_report_status(symbol: str):
    """Check if a comprehensive report has been run for a stock today."""
    try:
        symbol_upper = symbol.upper()
        job_tracker = get_job_tracker()

        # Get the most recent job for this symbol (returns main_job_id)
        main_job_id = job_tracker.get_job_by_symbol(symbol_upper, return_main_job_id=True)

        if not main_job_id:
            return {"has_report": False, "message": f"No report found for {symbol_upper}"}

        # Get job details by main_job_id
        job_data = job_tracker.get_job_status(main_job_id, use_main_job_id=True)

        if not job_data:
            return {"has_report": False, "message": f"No job data found for {symbol_upper}"}

        # Check if job is completed and has a result with comprehensive_report
        has_report = (
            job_data.get("status") == "completed" and
            job_data.get("result") and
            job_data.get("result", {}).get("comprehensive_report", {}).get("comprehensive_analysis")
        )

        # Check if the report was generated today
        is_today = False
        if has_report and job_data.get("completed_at"):
            from datetime import datetime
            completed_date = datetime.fromisoformat(job_data["completed_at"])
            today = datetime.now()
            is_today = (
                completed_date.year == today.year and
                completed_date.month == today.month and
                completed_date.day == today.day
            )

        return {
            "has_report": has_report and is_today,
            "completed_at": job_data.get("completed_at") if has_report else None,
            "symbol": symbol_upper,
            "job_id": main_job_id if has_report else None  # Return main_job_id
        }

    except Exception as e:
        logger.exception(f"Error checking report status for {symbol}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ticker-search")
async def search_ticker(query: str = Query(..., description="Search query for ticker symbol or company name")):
    """Search for stock symbols based on keywords.

    This endpoint searches for stock symbols and company names that match the provided query.
    It returns a list of matching stocks with relevant information.
    """
    try:
        logger.info(f"Searching for ticker with query: {query}")
        results = call_alpha_vantage_symbol_search(query)

        # Return the best matches directly
        return results

    except Exception as e:
        logger.exception(f"Error searching for ticker with query: {query}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent-debug")
async def agent_debug() -> AgentDebugResponse:
    """Debug endpoint for testing OpenAI Agents SDK with AlphaVantage MCP server.

    This endpoint demonstrates MCP (Model Context Protocol) integration by creating
    an agent that can query AlphaVantage market data using MCP tools.

    Hardcoded to test with AAPL stock quote. Simply visit http://localhost:8085/agent-debug
    """
    try:
        # Hardcoded parameters for easy browser testing
        symbol = "AAPL"

        symbol_upper = symbol.upper()
        logger.info(f"Starting agent debug for symbol={symbol_upper}")

        # Run the debug agent
        result = await run_agent_debug(symbol=symbol_upper)

        logger.info(f"Agent debug completed for {symbol_upper}")
        return result

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.exception(f"Error running agent debug for {symbol}")
        raise HTTPException(status_code=500, detail=str(e))