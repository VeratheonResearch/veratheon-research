from agents import Agent, Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
from legacy.research.common.models.peer_group import PeerGroup
import openai
import json
from src.lib.llm_model import get_model
from typing import Optional, Any

SYSTEM_INSTRUCTIONS = """
You are a financial analyst performing a comparable-company ("comps") analysis for forward P/E comparison.
Use financial statements analysis to identify peers with similar business models and financial characteristics.

INSTRUCTIONS:
- Given an original symbol, identify what market segment it belongs to.
- Identify 2 to 4 public companies whose business models, scale and growth profiles most closely resemble it.  
- Focus on similarities in core products/services, market-cap range, revenue/growth trajectory and investor expectations.  
- Exclude companies that, despite superficial overlaps, differ dramatically in size, profitability or market positioning (e.g. Fitbit vs. Apple)

CRITICAL: Use Financial Context When Available:

When financial_statements_analysis is provided:
- Match peers by revenue mix and business model characteristics (e.g. subscription vs. transactional, B2B vs. B2C)
- Consider revenue drivers and growth patterns (organic vs. acquisition-driven growth)
- Match similar cost structures and margin profiles (asset-light vs. capital-intensive)
- Consider business model transitions (e.g. if company is shifting to SaaS, include SaaS peers not legacy peers)
- Factor in working capital patterns and cash conversion cycles
- Consider geographical focus and market exposure

Examples of Financial Context Usage:
- If target shows subscription revenue growth → include subscription-based peers
- If target shows margin expansion → include peers with similar operational leverage
- If target shows working capital improvements → include peers with similar business models
- If target shows international expansion → include peers with global operations

IMPORTANT: 
- Companies must belong to the same market segment, not simply sharing broadly similar business models.
- Only the NYSE and NASDAQ exchanges are supported. For example, SSNFL trades on the OTC market and would not be included in the peer group.
- Only public companies are supported.
- Use financial data to select more relevant peers that reflect the company's current business trajectory

CRITICALLY IMPORTANT:
- EACH COMPANY MUST BE IN THE FORM OF A STOCK SYMBOL.
"""

_peer_group_agent = Agent(
            name="Peer Group Analyst",      
            model=get_model(),
            output_type=PeerGroup,
            # TODO: Allow Web Search Tool
            instructions=SYSTEM_INSTRUCTIONS
        )

async def peer_group_agent(symbol: str, financial_statements_analysis: Optional[Any] = None) -> PeerGroup:
    # Build input with optional financial context
    input_data = f"original_symbol: {symbol}"
    if financial_statements_analysis:
        input_data += f", financial_statements_analysis: {financial_statements_analysis}"

    result: RunResult = await Runner.run(
        _peer_group_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    peer_group: PeerGroup = result.final_output

    return peer_group


async def peer_group_chatcompletion(symbol: str) -> PeerGroup:
    response = openai.chat.completions.create(
        model=get_model(),
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user",   "content": f"original_symbol: {symbol}"}
        ],
        #temperature=0.0,
    )
    content = response.choices[0].message.content
    data = json.loads(content)
    return PeerGroup(**data)

