"""Supabase-based job tracking system."""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from src.lib.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def get_user_friendly_status_message(status: JobStatus) -> str:
    """
    Get user-friendly status message for job statuses.

    Args:
        status: JobStatus enum value

    Returns:
        User-friendly message string, or the status value if no mapping exists
    """
    return str(status)

class JobTracker:
    """Supabase-based job tracking system."""

    def __init__(self):
        """Initialize job tracker with Supabase client."""
        self._client = None

    @property
    def client(self):
        """Get Supabase client connection."""
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    def close(self):
        """Close connection (no-op for Supabase compatibility with Redis interface)."""
        self._client = None

    def create_job(self, job_type: str, symbol: str, metadata: Optional[Dict[str, Any]] = None,
                   main_job_id: Optional[str] = None, is_sub_job: bool = False,
                   job_name: Optional[str] = None) -> Dict[str, str]:
        """
        Create a new job and return its main_job_id and sub_job_id.

        Args:
            job_type: Type of job (e.g., 'research')
            symbol: Stock symbol being analyzed
            metadata: Optional additional metadata
            main_job_id: Optional main_job_id for sub-jobs (if None, generates new UUID)
            is_sub_job: Whether this is a sub-job (defaults to False)
            job_name: Optional job name (e.g., 'main_flow', 'historical_earnings_flow', etc.)

        Returns:
            Dict with 'main_job_id', 'sub_job_id', and 'id' (row ID)
        """
        try:
            # Prepare metadata with job_type and other info
            job_metadata = metadata or {}
            job_metadata["job_type"] = job_type
            job_metadata["steps"] = []
            job_metadata["result"] = None

            # Generate or use existing main_job_id
            if main_job_id is None:
                main_job_id = str(uuid.uuid4())

            # Generate sub_job_id if this is a sub-job
            sub_job_id = str(uuid.uuid4()) if is_sub_job else None

            # Insert job into Supabase
            insert_data = {
                "symbol": symbol.upper(),
                "status": JobStatus.PENDING,
                "metadata": job_metadata,
                "main_job_id": main_job_id
            }

            if sub_job_id:
                insert_data["sub_job_id"] = sub_job_id

            if job_name:
                insert_data["job_name"] = job_name

            print(f"🔵 DEBUG JobTracker.create_job: Inserting job with data: {insert_data}")
            response = self.client.table("research_jobs").insert(insert_data).execute()
            print(f"✅ DEBUG JobTracker.create_job: Insert response: {response.data}")

            if response.data and len(response.data) > 0:
                row_id = str(response.data[0]["id"])
                returned_main_job_id = response.data[0]["main_job_id"]
                returned_sub_job_id = response.data[0].get("sub_job_id")
                returned_job_name = response.data[0].get("job_name")

                logger.info(f"Created job '{returned_job_name}' with main_job_id={returned_main_job_id}, sub_job_id={returned_sub_job_id}, row_id={row_id} for {job_type} of {symbol}")

                return {
                    "main_job_id": returned_main_job_id,
                    "sub_job_id": returned_sub_job_id,
                    "id": row_id,
                    "job_name": returned_job_name
                }
            else:
                raise Exception("Failed to create job - no data returned")

        except Exception as e:
            logger.error(f"Failed to create job: {str(e)}")
            raise

    def update_job_status(self, job_id: str, status: JobStatus, step: Optional[str] = None,
                         result: Optional[Dict[str, Any]] = None, error: Optional[str] = None,
                         use_main_job_id: bool = True, use_sub_job_id: bool = False) -> bool:
        """
        Update job status and add step information.

        Args:
            job_id: Job ID (main_job_id by default, sub_job_id if use_sub_job_id=True, or row id if both False)
            status: New job status
            step: Optional step description
            result: Optional result data (for completed jobs)
            error: Optional error message (for failed jobs)
            use_main_job_id: If True, treat job_id as main_job_id
            use_sub_job_id: If True, treat job_id as sub_job_id (overrides use_main_job_id)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current job data to preserve metadata
            if use_sub_job_id:
                current_job = self.client.table("research_jobs").select("*").eq("sub_job_id", job_id).execute()
            elif use_main_job_id:
                # When using main_job_id, only get the main job row (where job_name='main_flow')
                # This prevents accidentally getting a subjob's data
                current_job = self.client.table("research_jobs").select("*").eq("main_job_id", job_id).eq("job_name", "main_flow").execute()
            else:
                current_job = self.client.table("research_jobs").select("*").eq("id", job_id).execute()

            if not current_job.data or len(current_job.data) == 0:
                logger.error(f"Job {job_id} not found")
                return False

            current_metadata = current_job.data[0].get("metadata", {})

            # Add step if provided
            if step:
                steps = current_metadata.get("steps", [])
                steps.append({
                    "step": step,
                    "timestamp": datetime.now().isoformat(),
                    "status": status
                })
                current_metadata["steps"] = steps

            # Set result for completed jobs
            if result and status == JobStatus.COMPLETED:
                current_metadata["result"] = result

            # Prepare update data
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
                "metadata": current_metadata
            }

            # Set timestamps based on status
            if status == JobStatus.COMPLETED:
                update_data["completed_at"] = datetime.now().isoformat()
            elif status == JobStatus.FAILED:
                update_data["failed_at"] = datetime.now().isoformat()
                update_data["error"] = error

            # Update job in Supabase
            if use_sub_job_id:
                self.client.table("research_jobs").update(update_data).eq("sub_job_id", job_id).execute()
            elif use_main_job_id:
                # When using main_job_id, only update the main job row (where job_name='main_flow')
                # This prevents accidentally updating all subjobs with the same main_job_id
                self.client.table("research_jobs").update(update_data).eq("main_job_id", job_id).eq("job_name", "main_flow").execute()
            else:
                self.client.table("research_jobs").update(update_data).eq("id", job_id).execute()

            logger.info(f"Updated job {job_id} status to {status}" + (f" with step: {step}" if step else ""))
            return True

        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {str(e)}")
            return False

    def get_job_status(self, job_id: str, use_main_job_id: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get job status and information.

        Args:
            job_id: Job ID (main_job_id by default, or row id if use_main_job_id=False)
            use_main_job_id: If True, treat job_id as main_job_id; if False, treat as row id

        Returns:
            Job data dict or None if not found
        """
        try:
            if use_main_job_id:
                # When using main_job_id, only get the main job row (where job_name='main_flow')
                # This prevents accidentally getting a subjob's data
                response = self.client.table("research_jobs").select("*").eq("main_job_id", job_id).eq("job_name", "main_flow").execute()
            else:
                response = self.client.table("research_jobs").select("*").eq("id", job_id).execute()

            if not response.data or len(response.data) == 0:
                return None

            job_data = response.data[0]
            metadata = job_data.get("metadata", {})

            # Format response with both IDs
            return {
                "job_id": str(job_data["id"]),  # Row ID (for backward compatibility)
                "main_job_id": job_data.get("main_job_id"),  # Main job UUID
                "sub_job_id": job_data.get("sub_job_id"),  # Sub job UUID (if exists)
                "job_type": metadata.get("job_type", "research"),
                "symbol": job_data["symbol"],
                "status": job_data["status"],
                "created_at": job_data["created_at"],
                "updated_at": job_data["updated_at"],
                "completed_at": job_data.get("completed_at"),
                "failed_at": job_data.get("failed_at"),
                "metadata": metadata,
                "steps": metadata.get("steps", []),
                "result": metadata.get("result"),
                "error": job_data.get("error")
            }

        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {str(e)}")
            return None

    def get_job_by_symbol(self, symbol: str, return_main_job_id: bool = True) -> Optional[str]:
        """
        Get the most recent job ID for a symbol.

        Args:
            symbol: Stock symbol
            return_main_job_id: If True, return main_job_id; if False, return row id

        Returns:
            Job ID (main_job_id or row id) or None if not found
        """
        try:
            response = self.client.table("research_jobs")\
                .select("id, main_job_id")\
                .eq("symbol", symbol.upper())\
                .order("created_at", desc=True)\
                .limit(1)\
                .execute()

            if response.data and len(response.data) > 0:
                if return_main_job_id:
                    return response.data[0]["main_job_id"]
                else:
                    return str(response.data[0]["id"])
            return None

        except Exception as e:
            logger.error(f"Failed to get job by symbol {symbol}: {str(e)}")
            return None

    def cancel_job(self, job_id: str, use_main_job_id: bool = True) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job ID (main_job_id by default, or row id if use_main_job_id=False)
            use_main_job_id: If True, treat job_id as main_job_id; if False, treat as row id

        Returns:
            True if successful, False otherwise
        """
        return self.update_job_status(job_id, JobStatus.CANCELLED, use_main_job_id=use_main_job_id)

    def create_sub_job(self, main_job_id: str, symbol: str, job_name: str,
                       job_type: str = "autonomous_research",
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Create a sub-job for an existing main job.

        This is a convenience method for creating sub-jobs within a workflow.

        Args:
            main_job_id: The main job ID to associate this sub-job with
            symbol: Stock symbol being analyzed
            job_name: Name of this sub-job (e.g., 'quantitative_agent', 'qualitative_agent')
            job_type: Type of job (defaults to 'autonomous_research')
            metadata: Optional additional metadata

        Returns:
            Dict with 'main_job_id', 'sub_job_id', and 'id' (row ID)
        """
        return self.create_job(
            job_type=job_type,
            symbol=symbol,
            metadata=metadata,
            main_job_id=main_job_id,
            is_sub_job=True,
            job_name=job_name
        )

    def update_sub_job_status(self, sub_job_id: str, status: JobStatus,
                              step: Optional[str] = None,
                              result: Optional[Dict[str, Any]] = None,
                              error: Optional[str] = None) -> bool:
        """
        Update a sub-job's status.

        This is a convenience method that wraps update_job_status with use_sub_job_id=True.

        Args:
            sub_job_id: The sub_job_id to update
            status: New job status
            step: Optional step description
            result: Optional result data (for completed jobs)
            error: Optional error message (for failed jobs)

        Returns:
            True if successful, False otherwise
        """
        return self.update_job_status(
            job_id=sub_job_id,
            status=status,
            step=step,
            result=result,
            error=error,
            use_main_job_id=False,
            use_sub_job_id=True
        )

    def add_user_research_history(self, user_id: str, symbol: str, main_job_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an entry to user_research_history table.

        Args:
            user_id: User identifier
            symbol: Stock symbol
            main_job_id: Main job UUID
            metadata: Optional additional metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.table("user_research_history").insert({
                "user_id": user_id,
                "symbol": symbol.upper(),
                "job_id": main_job_id,  # Store main_job_id
                "metadata": metadata or {}
            }).execute()

            logger.info(f"Added user research history for user {user_id}, symbol {symbol}, main_job_id {main_job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add user research history: {str(e)}")
            return False

    def list_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List recent jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job data dicts
        """
        try:
            response = self.client.table("research_jobs")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()

            jobs = []
            for job_data in response.data:
                metadata = job_data.get("metadata", {})
                jobs.append({
                    "job_id": str(job_data["id"]),  # Row ID (for backward compatibility)
                    "main_job_id": job_data.get("main_job_id"),  # Main job UUID
                    "sub_job_id": job_data.get("sub_job_id"),  # Sub job UUID (if exists)
                    "job_type": metadata.get("job_type", "research"),
                    "symbol": job_data["symbol"],
                    "status": job_data["status"],
                    "created_at": job_data["created_at"],
                    "updated_at": job_data["updated_at"],
                    "completed_at": job_data.get("completed_at"),
                    "failed_at": job_data.get("failed_at"),
                    "metadata": metadata,
                    "steps": metadata.get("steps", []),
                    "result": metadata.get("result"),
                    "error": job_data.get("error")
                })

            return jobs

        except Exception as e:
            logger.error(f"Failed to list jobs: {str(e)}")
            return []

# Global job tracker instance
_job_tracker_instance = None

def get_job_tracker() -> JobTracker:
    """Get or create global job tracker instance."""
    global _job_tracker_instance
    if _job_tracker_instance is None:
        _job_tracker_instance = JobTracker()
    return _job_tracker_instance

def close_job_tracker():
    """Close global job tracker connection."""
    global _job_tracker_instance
    if _job_tracker_instance:
        _job_tracker_instance.close()
        _job_tracker_instance = None
