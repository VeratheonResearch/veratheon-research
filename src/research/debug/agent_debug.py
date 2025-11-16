"""
Agent Debug Module for testing OpenAI Agents SDK with AlphaVantage MCP server.

This module provides a standalone agent that connects to the AlphaVantage MCP server
to demonstrate MCP tool integration with the OpenAI Agents SDK.
"""

import os
import logging
import time
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from agents import Agent, Runner, RunResult
from agents.mcp import MCPServerStreamableHttp
from src.lib.llm_model import get_model
from src.lib.token_logger_hook import TokenLoggerHook

logger = logging.getLogger(__name__)


# Pydantic Models
class AgentDebugRequest(BaseModel):
    """Request model for agent debug endpoint."""
    symbol: str
    message: Optional[str] = "Get the global quote for this stock"


class ToolCall(BaseModel):
    """Represents a tool call made by the agent."""
    tool_name: str
    arguments: Dict[str, Any]


class AgentDebugResponse(BaseModel):
    """Response model for agent debug endpoint."""
    symbol: str
    agent_response: str
    tool_calls: List[ToolCall]
    execution_time_seconds: float
    model_used: str
    mcp_server: str


async def run_agent_debug(symbol: str, message: Optional[str] = None) -> AgentDebugResponse:
    """
    Run the debug agent with AlphaVantage MCP server integration.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL")
        message: Optional custom message/instruction for the agent

    Returns:
        AgentDebugResponse with agent output and execution details

    Raises:
        ValueError: If ALPHA_VANTAGE_API_KEY is not set
        Exception: If agent execution fails
    """
    start_time = time.time()

    # Get API key from environment
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is required")

    # Default message if not provided
    user_message = message or f"{symbol}"

    logger.info(f"Starting agent debug for symbol={symbol}, message='{user_message}'")

    # Construct MCP server URL with API key
    mcp_url = f"https://mcp.alphavantage.co/mcp?apikey={api_key}"

    try:
        # Connect to AlphaVantage MCP server via HTTP
        async with MCPServerStreamableHttp(
            name="AlphaVantage MCP Server",
            params={
                "url": mcp_url,
                "timeout": 30,
            },
            cache_tools_list=True,
            max_retry_attempts=3,
        ) as server:

            logger.info(f"Connected to MCP server: {mcp_url}")

            # Create agent with MCP server tools
            agent = Agent(
                name="Debug Agent",
                model=get_model("xai_grok_4_fast_reasoning"),
                mcp_servers=[server],
                instructions=f"""You are a financial data assistant with access to AlphaVantage market data tools.

                Your task is to help users retrieve stock market data using the available MCP tools.

                Gather a high level summary of the balance sheet, income statement, and the global quote.

                Return a json object with the following keys:
                - balance_sheet_summary
                - income_statement_summary
                - global_quote_summary

                Stock symbol: {symbol}
                """,
            )

            # Run the agent
            logger.info(f"Running agent with message: {user_message}")
            result: RunResult = await Runner.run(
                agent,
                input=user_message,
                hooks=TokenLoggerHook(symbol=symbol)
            )

            # Extract tool calls from result
            tool_calls = []
            if hasattr(result, 'steps'):
                for step in result.steps:
                    if hasattr(step, 'tool_calls') and step.tool_calls:
                        for tool_call in step.tool_calls:
                            tool_calls.append(ToolCall(
                                tool_name=tool_call.function.name if hasattr(tool_call, 'function') else str(tool_call),
                                arguments=tool_call.function.arguments if hasattr(tool_call, 'function') else {}
                            ))

            # Calculate execution time
            execution_time = time.time() - start_time

            # Get model name
            model_name = str(get_model("xai_grok_4_fast_reasoning"))

            logger.info(f"Agent debug completed in {execution_time:.2f}s, tools used: {len(tool_calls)}")

            # Return structured response
            return AgentDebugResponse(
                symbol=symbol.upper(),
                agent_response=str(result.final_output) if result.final_output else "No response from agent",
                tool_calls=tool_calls,
                execution_time_seconds=round(execution_time, 2),
                model_used=model_name,
                mcp_server=mcp_url.replace(api_key, "***")  # Mask API key in response
            )

    except Exception as e:
        logger.exception(f"Error running agent debug for {symbol}")
        raise Exception(f"Agent debug failed: {str(e)}")
