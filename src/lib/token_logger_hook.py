"""
Token usage logging hook for OpenAI Agents SDK.

Automatically tracks and logs token usage for all agent executions using
the SDK's built-in RunHooks lifecycle callbacks.
"""

import logging
from typing import Any, Optional, List, Dict
from dataclasses import dataclass, field
from agents.lifecycle import RunHooksBase
from agents.run_context import RunContextWrapper
from agents import Agent

from src.lib.supabase_logger import log_info

logger = logging.getLogger(__name__)


@dataclass
class AgentTokenUsage:
    """Represents token usage for a single agent run."""
    agent_name: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: int


class TokenAggregator:
    """
    Aggregates token usage across multiple agent runs.

    Usage:
        aggregator = TokenAggregator()
        # Pass to hooks during workflow
        hook = TokenLoggerHook(symbol=symbol, aggregator=aggregator)
        # At end of workflow
        aggregator.print_summary()
    """

    def __init__(self):
        """Initialize the token aggregator."""
        self.agent_runs: List[AgentTokenUsage] = []
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_tokens = 0
        self._total_requests = 0

    def add_agent_run(
        self,
        agent_name: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        requests: int
    ) -> None:
        """
        Record token usage for an agent run.

        Args:
            agent_name: Name of the agent
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            total_tokens: Total tokens used
            requests: Number of API requests made
        """
        usage = AgentTokenUsage(
            agent_name=agent_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            requests=requests
        )
        self.agent_runs.append(usage)

        # Update totals
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._total_tokens += total_tokens
        self._total_requests += requests

    def get_totals(self) -> Dict[str, int]:
        """
        Get aggregated totals across all agent runs.

        Returns:
            Dictionary with total_input_tokens, total_output_tokens,
            total_tokens, total_requests, and agent_count
        """
        return {
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_tokens": self._total_tokens,
            "total_requests": self._total_requests,
            "agent_count": len(self.agent_runs)
        }

    def print_summary(self) -> None:
        """Print a formatted summary of all token usage."""
        print("\n" + "="*80)
        print("TOKEN USAGE SUMMARY")
        print("="*80)

        if not self.agent_runs:
            print("No agent runs recorded.")
            return

        # Print per-agent breakdown
        print(f"\n{'Agent Name':<40} {'Input':<12} {'Output':<12} {'Total':<12} {'Requests':<10}")
        print("-"*80)

        for run in self.agent_runs:
            print(
                f"{run.agent_name:<40} "
                f"{run.input_tokens:>10,}  "
                f"{run.output_tokens:>10,}  "
                f"{run.total_tokens:>10,}  "
                f"{run.requests:>8}"
            )

        # Print totals
        print("-"*80)
        print(
            f"{'TOTAL (' + str(len(self.agent_runs)) + ' agents)':<40} "
            f"{self._total_input_tokens:>10,}  "
            f"{self._total_output_tokens:>10,}  "
            f"{self._total_tokens:>10,}  "
            f"{self._total_requests:>8}"
        )
        print("="*80 + "\n")

    def get_summary_dict(self) -> Dict[str, Any]:
        """
        Get summary as a dictionary for logging.

        Returns:
            Dictionary containing per-agent breakdown and totals
        """
        return {
            "agent_runs": [
                {
                    "agent_name": run.agent_name,
                    "input_tokens": run.input_tokens,
                    "output_tokens": run.output_tokens,
                    "total_tokens": run.total_tokens,
                    "requests": run.requests
                }
                for run in self.agent_runs
            ],
            "totals": self.get_totals()
        }


class TokenLoggerHook(RunHooksBase):
    """
    Hook that logs token usage after each agent execution.
    Automatically tracks all token usage in a class-level aggregator.

    Usage:
        # Use hooks normally
        result = await Runner.run(agent, input, hooks=TokenLoggerHook(symbol=symbol))

        # At end of workflow, get summary
        TokenLoggerHook.print_summary()
        # Or reset for new workflow
        TokenLoggerHook.reset()
    """

    # Class-level aggregator shared across all instances
    _aggregator = TokenAggregator()

    def __init__(
        self,
        job_id: Optional[str] = None,
        symbol: Optional[str] = None
    ):
        """
        Initialize the token logger hook.

        Args:
            job_id: Optional job ID for Supabase logging
            symbol: Optional stock symbol for Supabase logging
        """
        super().__init__()
        self.job_id = job_id
        self.symbol = symbol

    @classmethod
    def reset(cls) -> None:
        """Reset the class-level aggregator (useful between workflows)."""
        cls._aggregator = TokenAggregator()

    @classmethod
    def print_summary(cls) -> None:
        """Print the aggregated token usage summary."""
        cls._aggregator.print_summary()

    @classmethod
    def get_summary_dict(cls) -> Dict[str, Any]:
        """Get the aggregated token usage as a dictionary."""
        return cls._aggregator.get_summary_dict()

    @classmethod
    def get_totals(cls) -> Dict[str, int]:
        """Get the aggregated totals."""
        return cls._aggregator.get_totals()

    async def on_agent_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        output: Any
    ) -> None:
        """
        Called when the agent produces a final output.
        Logs token usage to console and Supabase, and adds to class-level aggregator.

        Args:
            context: Run context containing usage information
            agent: The agent that completed execution
            output: The agent's final output
        """
        usage = context.usage

        # Add to class-level aggregator
        self._aggregator.add_agent_run(
            agent_name=agent.name,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            requests=usage.requests
        )

        # Format console output
        console_msg = (
            f"[Agent: {agent.name}] "
            f"Tokens: {usage.input_tokens:,} prompt + {usage.output_tokens:,} completion = "
            f"{usage.total_tokens:,} total ({usage.requests} request(s))"
        )

        logger.info(console_msg)
        print(f"\n✓ {console_msg}")

        # Log to Supabase system_logs table
        try:
            log_info(
                component="token_tracker",
                message=f"Agent execution completed: {agent.name}",
                job_id=self.job_id,
                symbol=self.symbol,
                metadata={
                    "agent_name": agent.name,
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                    "requests": usage.requests,
                    # Include detailed per-request breakdown if available
                    "request_breakdown": [
                        {
                            "input_tokens": req.input_tokens,
                            "output_tokens": req.output_tokens,
                            "total_tokens": req.input_tokens + req.output_tokens
                        }
                        for req in usage.request_usage_entries
                    ] if hasattr(usage, 'request_usage_entries') else []
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log token usage to Supabase: {e}")

    async def on_llm_end(
        self,
        context: RunContextWrapper,
        agent: Agent,
        response: Any
    ) -> None:
        """
        Optional: Called after each individual LLM call.
        Can be used for more granular per-call logging.
        Currently disabled to avoid log spam.
        """
        pass
