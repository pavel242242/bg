"""
Claude Agent SDK integration for Apify actor.
"""
import os
from typing import Optional
from claude_agent_sdk import ClaudeAgent, ClaudeAgentOptions


# System prompt for the data automation agent
SYSTEM_PROMPT = """You are a pragmatic data automation agent running inside an Apify actor.

You can:
- Use the Apify SDK to:
  - Run and orchestrate actors and tasks.
  - Configure and launch new web scrapers and crawlers.
  - Schedule and monitor runs.
  - Read and write actor input/output datasets, key-value stores, and request queues.

- Use the Keboola Storage API to:
  - Read table schemas and samples from any bucket.
  - Clean, filter, join, and reshape data via simple, explicit instructions.
  - Create new tables and write incremental or full loads.
  - Export data from Keboola to external tools or destinations via generated configs or API calls.

Your mission:
- Help the user move data from **any source to any destination** using Apify and Keboola together:
  - Design and describe scrapers and actors that fetch source data.
  - Design and describe Keboola pipelines that clean, normalize, and route that data.
  - Propose concrete steps, configs, and API interactions that can be executed by the underlying code.

Conventions:
- You may receive inline context such as small CSV samples or configuration snippets.
- If you need more detail (URL, table ID, schema, credentials), ask for it explicitly.
- Prefer:
  - Step-by-step plans over vague descriptions.
  - Minimal, copy-pasteable examples (actor input, Storage API calls, table IDs, column mappings).
  - Clear separation of stages: scrape → ingest → clean → export.

Behavior:
- Be concise, technical, and unambiguous.
- Never invent external access you don't have; instead, describe exactly what should be configured or run.
- If something is impossible or underspecified, say so and state what is missing."""


class AgentOrchestrator:
    """Orchestrates Claude agent interactions."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.agent = ClaudeAgent(api_key=self.api_key)

    def run_agent(self, user_message: str, keboola_context: Optional[str] = None) -> str:
        """
        Run Claude agent with user message and optional Keboola context.

        Args:
            user_message: User's question or request
            keboola_context: Optional CSV sample from Keboola table

        Returns:
            Agent's reply as a single string
        """
        # Build the full user message
        full_message = user_message

        if keboola_context:
            full_message = f"{user_message}\n\nKEBOOLA SAMPLE:\n{keboola_context}"

        # Configure agent options
        options = ClaudeAgentOptions(
            max_turns=1,
            system_prompt=SYSTEM_PROMPT,
            model="claude-sonnet-4-5-20250929"
        )

        # Call agent
        response = self.agent.query(full_message, options=options)

        # Concatenate all assistant messages
        reply_parts = []
        for message in response.messages:
            if hasattr(message, 'role') and message.role == 'assistant':
                if hasattr(message, 'content'):
                    if isinstance(message.content, str):
                        reply_parts.append(message.content)
                    elif isinstance(message.content, list):
                        # Handle multiple content blocks
                        for block in message.content:
                            if hasattr(block, 'text'):
                                reply_parts.append(block.text)
                            elif isinstance(block, str):
                                reply_parts.append(block)

        return '\n'.join(reply_parts) if reply_parts else "No response generated."
