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
from src.lib.supabase_job_tracker import get_job_tracker, JobStatus  # noqa: E402
from src.lib.alpha_vantage_api import call_alpha_vantage_symbol_search  # noqa: E402
from src.agents.workflow import run_autonomous_workflow, WorkflowResult  # noqa: E402

logging.basicConfig(level=logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

app = FastAPI(title="Veratheon Research API", version="0.1.0")

class ResearchRequest(BaseModel):
    symbol: str


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


async def run_autonomous_research_background(main_job_id: str, symbol: str):
    """Background task to run autonomous research workflow and update job status."""
    job_tracker = get_job_tracker()

    try:
        # Update status to running
        job_tracker.update_job_status(main_job_id, JobStatus.RUNNING, step="Starting autonomous research", use_main_job_id=True)

        # Run the autonomous workflow with job tracking
        workflow_result: WorkflowResult = await run_autonomous_workflow(symbol, main_job_id=main_job_id)

        # Check for errors in the workflow result
        if workflow_result.error:
            job_tracker.update_job_status(
                main_job_id,
                JobStatus.FAILED,
                step="Autonomous research failed",
                error=workflow_result.error,
                use_main_job_id=True
            )
            logger.error(f"Autonomous research failed for {symbol}: {workflow_result.error}")
            return

        # Convert WorkflowResult to dict for storage
        # Handle macro_report which may be a MacroReport dataclass
        macro_data = None
        if workflow_result.macro_report:
            from src.agents.macro_report import MacroReport
            if isinstance(workflow_result.macro_report, MacroReport):
                # Use the to_dict() method which properly serializes all fields
                macro_data = workflow_result.macro_report.to_dict()
            else:
                macro_data = workflow_result.macro_report

        result_dict = {
            "symbol": workflow_result.symbol,
            "quantitative_report": workflow_result.quantitative_report,
            "qualitative_report": workflow_result.qualitative_report,
            "macro_report": macro_data,
            "synthesis_report": workflow_result.synthesis_report,
            "trade_advice": workflow_result.trade_advice
        }

        # Mark as completed with result
        job_tracker.update_job_status(
            main_job_id,
            JobStatus.COMPLETED,
            step="Autonomous research completed",
            result=result_dict,
            use_main_job_id=True
        )

        logger.info(f"Autonomous research completed for {symbol} (main_job_id {main_job_id})")

    except Exception as e:
        logger.exception(f"Error running autonomous research for {symbol} (main_job_id {main_job_id})")
        job_tracker.update_job_status(main_job_id, JobStatus.FAILED, step="Autonomous research failed", error=str(e), use_main_job_id=True)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/research")
async def start_research(req: ResearchRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Start an autonomous research job using the three-pillar workflow.

    This endpoint runs the autonomous research workflow which includes:
    - Quantitative Agent: Financial health analysis using Alpha Vantage data
    - Qualitative Agent: News and sentiment via xAI web/X search
    - Macro Report: Economic indicators (no LLM)
    - Synthesis Agent: Combines all into unified report
    - Trade Advice Agent: Generates actionable trade ideas (advisory only)

    Returns a job_id for tracking progress via Supabase Realtime.
    """
    try:
        symbol_upper = req.symbol.upper()
        logger.info(f"Starting autonomous research job for symbol={symbol_upper}")

        job_tracker = get_job_tracker()

        # Create new job
        job_result = job_tracker.create_job(
            job_type="autonomous_research",
            symbol=symbol_upper,
            metadata={
                "workflow": "autonomous",
                "requested_at": datetime.now().isoformat()
            },
            is_sub_job=False,
            job_name="main_flow"
        )

        main_job_id = job_result["main_job_id"]

        # Start background task
        background_tasks.add_task(run_autonomous_research_background, main_job_id, symbol_upper)

        return JobResponse(
            job_id=main_job_id,
            status="pending",
            message=f"Autonomous research job started for {symbol_upper}"
        )

    except Exception as e:
        logger.exception("Error starting autonomous research job")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/report-status/{symbol}")
async def check_report_status(symbol: str):
    """Check if a research report has been run for a stock today."""
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

        # Check if job is completed and has a result with synthesis_report (new autonomous workflow)
        result = job_data.get("result")
        has_report = (
            job_data.get("status") == "completed" and
            result and
            result.get("synthesis_report")
        )

        # Check if the report was generated today
        is_today = False
        if has_report and job_data.get("completed_at"):
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
            "job_id": main_job_id if has_report else None
        }

    except Exception as e:
        logger.exception(f"Error checking report status for {symbol}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get job status by job_id.

    This endpoint returns the full job status including result if completed.
    Used by frontend for polling fallback when Realtime is unavailable.

    Args:
        job_id: The main_job_id of the research job

    Returns:
        Job data including status, result (if completed), and error (if failed)
    """
    try:
        job_tracker = get_job_tracker()

        # Get job status by main_job_id
        job_data = job_tracker.get_job_status(job_id, use_main_job_id=True)

        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        return {
            "job_id": job_data.get("main_job_id"),
            "symbol": job_data.get("symbol"),
            "status": job_data.get("status"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "completed_at": job_data.get("completed_at"),
            "failed_at": job_data.get("failed_at"),
            "result": job_data.get("result"),
            "error": job_data.get("error"),
            "steps": job_data.get("steps", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting job status for {job_id}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/symbol/{symbol}")
async def get_job_by_symbol(symbol: str):
    """Get the most recent job for a symbol.

    This endpoint allows the frontend to resume tracking a job by symbol
    when the job_id is not available (e.g., page refresh).

    Args:
        symbol: Stock symbol to look up

    Returns:
        Most recent job data for the symbol, or 404 if not found
    """
    try:
        symbol_upper = symbol.upper()
        job_tracker = get_job_tracker()

        # Get the most recent job for this symbol
        main_job_id = job_tracker.get_job_by_symbol(symbol_upper, return_main_job_id=True)

        if not main_job_id:
            raise HTTPException(status_code=404, detail=f"No job found for symbol {symbol_upper}")

        # Get full job details
        job_data = job_tracker.get_job_status(main_job_id, use_main_job_id=True)

        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job data not found for symbol {symbol_upper}")

        return {
            "job_id": job_data.get("main_job_id"),
            "symbol": job_data.get("symbol"),
            "status": job_data.get("status"),
            "created_at": job_data.get("created_at"),
            "updated_at": job_data.get("updated_at"),
            "completed_at": job_data.get("completed_at"),
            "failed_at": job_data.get("failed_at"),
            "result": job_data.get("result"),
            "error": job_data.get("error"),
            "steps": job_data.get("steps", [])
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting job by symbol {symbol}")
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