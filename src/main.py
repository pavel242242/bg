"""
Apify actor with HTTP server for Claude + Keboola chat interface.
"""
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Optional

from apify import Actor
from apify.http import HttpServer

from agent import AgentOrchestrator
from keboola_helper import KeboolaHelper


class ChatHandler:
    """HTTP request handler for chat interface."""

    def __init__(self, agent: AgentOrchestrator, keboola: Optional[KeboolaHelper] = None):
        """
        Initialize chat handler.

        Args:
            agent: Claude agent orchestrator
            keboola: Optional Keboola helper (if credentials available)
        """
        self.agent = agent
        self.keboola = keboola

    def parse_table_command(self, message: str) -> tuple[Optional[str], Optional[int], str]:
        """
        Parse !table command from user message.

        Format: !table <table_id> <limit> [question...]

        Args:
            message: User message

        Returns:
            Tuple of (table_id, limit, user_question)
        """
        if not message.strip().startswith("!table"):
            return None, None, message

        # Parse: !table table_id limit rest...
        pattern = r"^!table\s+(\S+)(?:\s+(\d+))?\s*(.*)?$"
        match = re.match(pattern, message.strip())

        if not match:
            return None, None, message

        table_id = match.group(1)
        limit_str = match.group(2)
        question = match.group(3) or f"Describe this table: {table_id}"

        limit = int(limit_str) if limit_str else 5

        return table_id, limit, question

    async def handle_chat(self, request_data: dict) -> dict:
        """
        Handle chat POST request.

        Args:
            request_data: JSON request body with 'message' field

        Returns:
            JSON response with 'reply' field
        """
        try:
            message = request_data.get("message", "").strip()

            if not message:
                return {"error": "Message cannot be empty"}

            # Parse potential !table command
            table_id, limit, user_question = self.parse_table_command(message)

            # Fetch Keboola context if requested
            keboola_context = None
            if table_id and self.keboola:
                try:
                    keboola_context = self.keboola.get_table_sample_csv(table_id, limit)
                except Exception as e:
                    return {"error": f"Failed to fetch table sample: {str(e)}"}

            # Run agent
            try:
                reply = self.agent.run_agent(user_question, keboola_context)
                return {"reply": reply}
            except Exception as e:
                return {"error": f"Agent error: {str(e)}"}

        except Exception as e:
            return {"error": f"Request error: {str(e)}"}


async def main():
    """Main actor entry point."""
    async with Actor:
        Actor.log.info("Actor started")

        # Initialize agent
        try:
            agent = AgentOrchestrator()
            Actor.log.info("Claude agent initialized")
        except Exception as e:
            Actor.log.error(f"Failed to initialize Claude agent: {e}")
            raise

        # Initialize Keboola (optional)
        keboola = None
        if os.getenv("KBC_URL") and os.getenv("KBC_TOKEN"):
            try:
                keboola = KeboolaHelper()
                Actor.log.info("Keboola helper initialized")
            except Exception as e:
                Actor.log.warning(f"Keboola not available: {e}")

        # Create chat handler
        chat_handler = ChatHandler(agent, keboola)

        # Set up HTTP server
        server = HttpServer()

        @server.get("/")
        async def serve_index(request):
            """Serve chat interface."""
            template_path = Path(__file__).parent / "templates" / "chat.html"

            if not template_path.exists():
                return server.create_response(
                    "<h1>Error</h1><p>Chat template not found</p>",
                    content_type="text/html",
                    status=500
                )

            with open(template_path, 'r', encoding='utf-8') as f:
                html = f.read()

            return server.create_response(html, content_type="text/html")

        @server.post("/chat")
        async def handle_chat_post(request):
            """Handle chat message."""
            try:
                # Parse JSON body
                body = await request.json()

                # Process chat
                response_data = await chat_handler.handle_chat(body)

                # Return JSON response
                return server.create_json_response(response_data)

            except json.JSONDecodeError:
                return server.create_json_response(
                    {"error": "Invalid JSON"},
                    status=400
                )
            except Exception as e:
                Actor.log.error(f"Chat handler error: {e}")
                return server.create_json_response(
                    {"error": str(e)},
                    status=500
                )

        # Get server port
        port = int(os.getenv("APIFY_ACTOR_WEB_SERVER_PORT", "8080"))

        Actor.log.info(f"Starting HTTP server on port {port}")

        # Start server (blocks until actor is stopped)
        await server.start(port=port)

        Actor.log.info("Actor finished")


if __name__ == "__main__":
    asyncio.run(main())
