import logging
from typing import Optional, Dict
from src.lib.supabase_job_tracker import get_job_tracker, JobStatus

logger = logging.getLogger(__name__)

# Track created subjobs to avoid duplicates - keyed by main_job_id
_created_subjobs: Dict[str, Dict[str, str]] = {}

async def update_job_status_task(
    main_job_id: Optional[str],
    status: JobStatus,
    step: str,
    flow: Optional[str] = None,
    symbol: Optional[str] = None
) -> bool:
    """
    Task to update job status in Supabase. Creates a subjob for each flow if it doesn't exist.

    Args:
        main_job_id: Main job UUID (if None, this is a no-op for backward compatibility)
        status: Job status to update to
        step: Description of the current step
        flow: Optional flow name (will be used as job_name for subjobs)
        symbol: Stock symbol (required when creating subjobs)

    Returns:
        bool: True if successful, False otherwise
    """
    # Log every call to this function
    print(f"📞 DEBUG: update_job_status_task called: main_job_id={main_job_id}, flow={flow}, step={step}, symbol={symbol}")
    logger.info(f"📞 update_job_status_task called: main_job_id={main_job_id}, flow={flow}, step={step}, symbol={symbol}")

    if not main_job_id:
        # For backward compatibility when main_job_id is not provided
        logger.debug(f"No main_job_id provided, skipping status update: {step}")
        return True

    try:
        job_tracker = get_job_tracker()

        # Initialize subjobs dict for this main_job_id if needed
        if main_job_id not in _created_subjobs:
            _created_subjobs[main_job_id] = {}

        # Determine which job to update
        logger.debug(f"Processing flow='{flow}' for main_job_id={main_job_id}")

        if flow and flow != "main_research_flow":
            # This is a subflow - create/update subjob
            logger.debug(f"Flow '{flow}' is a subflow, checking if subjob exists...")

            if flow not in _created_subjobs[main_job_id]:
                # Create a new subjob for this flow
                if not symbol:
                    logger.error(f"Symbol required to create subjob for flow {flow}")
                    return False

                print(f"🔵 DEBUG: Creating subjob for flow '{flow}' under main_job_id {main_job_id}, symbol={symbol}")
                logger.info(f"🔵 Creating subjob for flow '{flow}' under main_job_id {main_job_id}, symbol={symbol}")
                subjob_result = job_tracker.create_job(
                    job_type="research_subflow",
                    symbol=symbol,
                    metadata={"parent_flow": "main_research_flow"},
                    main_job_id=main_job_id,
                    is_sub_job=True,
                    job_name=flow
                )
                _created_subjobs[main_job_id][flow] = subjob_result["sub_job_id"]
                print(f"✅ DEBUG: Created subjob '{flow}' with sub_job_id={subjob_result['sub_job_id']}")
                logger.info(f"✅ Created subjob '{flow}' with sub_job_id={subjob_result['sub_job_id']}")
            else:
                logger.debug(f"Subjob for flow '{flow}' already exists, will update it")

            # Update the subjob status by sub_job_id
            sub_job_id = _created_subjobs[main_job_id][flow]
            result = job_tracker.update_job_status(
                sub_job_id,
                status,
                step=step,
                use_main_job_id=False,
                use_sub_job_id=True  # Use sub_job_id for lookup
            )
        else:
            # This is the main flow - update main job
            result = job_tracker.update_job_status(
                main_job_id,
                status,
                step=step,
                use_main_job_id=True
            )

        if result:
            logger.info(f"Updated job {main_job_id} ({flow or 'main_flow'}) status to {status}: {step}")
        else:
            logger.warning(f"Failed to update job {main_job_id} ({flow or 'main_flow'}) status")

        return result

    except Exception as e:
        logger.error(f"Failed to update job status for {main_job_id}: {str(e)}")
        return False