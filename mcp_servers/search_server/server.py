"""
MCP Server for Google Custom Search
Provides web search capabilities via Model Context Protocol
"""

import os
import json
import asyncio
from typing import Any, Sequence
import requests

# Load environment variables at the very beginning
from dotenv import load_dotenv
load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Debug logging to file (since stdio is used for MCP communication)
import sys
DEBUG_LOG = open('/tmp/mcp_search_debug.log', 'w')
def debug_log(msg):
    DEBUG_LOG.write(f"{msg}\n")
    DEBUG_LOG.flush()


class SearchMCPServer:
    """MCP Server implementing Google Custom Search functionality"""

    def __init__(self):
        debug_log("=== SearchMCPServer initialization started ===")
        self.server = Server("search-server")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")

        debug_log(f"GOOGLE_API_KEY present: {bool(self.google_api_key)}")
        debug_log(f"GOOGLE_CSE_ID present: {bool(self.google_cse_id)}")

        if not self.google_api_key or not self.google_cse_id:
            debug_log("ERROR: Missing API credentials!")
            raise ValueError(
                "GOOGLE_API_KEY and GOOGLE_CSE_ID must be set in environment"
            )

        # Register handlers
        self.server.list_tools()(self.list_tools)
        self.server.call_tool()(self.call_tool)
        debug_log("=== SearchMCPServer initialization complete ===")

    async def list_tools(self) -> list[Tool]:
        """List available tools - in this case, just web_search"""
        return [
            Tool(
                name="web_search",
                description=(
                    "Search the web using Google Custom Search. "
                    "Returns a list of search results with titles, URLs, and snippets. "
                    "Best used for finding research papers, documentation, and technical resources "
                    "about mechanistic interpretability, machine learning, and AI."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query string"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return (1-10, default: 5)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10
                        }
                    },
                    "required": ["query"]
                }
            )
        ]

    async def call_tool(self, name: str, arguments: dict) -> Sequence[TextContent]:
        """Handle tool calls"""
        debug_log(f"call_tool invoked: name={name}, arguments={arguments}")

        if name != "web_search":
            raise ValueError(f"Unknown tool: {name}")

        query = arguments.get("query")
        num_results = arguments.get("num_results", 5)

        debug_log(f"Extracted query='{query}', num_results={num_results}")

        if not query:
            raise ValueError("query parameter is required")

        debug_log("About to call _search_google...")
        # Perform the search
        results = await self._search_google(query, num_results)

        debug_log(f"Results from _search_google: {results}")
        debug_log(f"Results type: {type(results)}")
        debug_log(f"Results length: {len(results) if results else 'None'}")

        # Format results as text
        formatted = self._format_results(results)

        debug_log(f"Formatted output (first 200 chars): {formatted[:200]}")
        debug_log(f"Formatted output length: {len(formatted)}")

        return [TextContent(type="text", text=formatted)]

    async def _search_google(self, query: str, num_results: int) -> list[dict]:
        """
        Perform Google Custom Search API call

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            List of search result dictionaries
        """
        debug_log(f"_search_google called with query='{query}', num_results={num_results}")

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "q": query,
            "num": min(num_results, 10)
        }

        debug_log(f"API URL: {url}")
        debug_log(f"API params (key hidden): cx={self.google_cse_id}, q={query}, num={min(num_results, 10)}")

        try:
            # Run requests in thread pool to avoid blocking
            debug_log("About to make HTTP request to Google API...")
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )
            debug_log(f"HTTP response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            debug_log(f"JSON response keys: {data.keys()}")
            debug_log(f"Number of items in response: {len(data.get('items', []))}")

            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })

            debug_log(f"Parsed {len(results)} search results")
            if results:
                debug_log(f"First result title: {results[0].get('title', 'N/A')}")

            return results

        except Exception as e:
            debug_log(f"EXCEPTION in _search_google: {type(e).__name__}: {e}")
            import traceback
            debug_log(f"Traceback: {traceback.format_exc()}")
            raise RuntimeError(f"Search API error: {e}")

    def _format_results(self, results: list[dict]) -> str:
        """Format search results for consumption by LLM"""
        debug_log(f"_format_results called with {len(results) if results else 0} results")

        if not results:
            debug_log("No results to format, returning 'No search results found.'")
            return "No search results found."

        formatted = f"Found {len(results)} search results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"[{i}] {result['title']}\n"
            formatted += f"    URL: {result['url']}\n"
            formatted += f"    {result['snippet']}\n\n"

        debug_log(f"Formatted {len(results)} results into text")
        return formatted

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point for the MCP server"""
    server = SearchMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
