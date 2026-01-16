"""
MCP Client for connecting to MCP servers
Provides a simple interface for agents to use MCP tools
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Client for interacting with MCP servers"""

    def __init__(self, server_name: str, server_script_path: str, verbose: bool = False):
        """
        Initialize MCP client

        Args:
            server_name: Name of the MCP server
            server_script_path: Path to the server script
            verbose: Enable verbose logging
        """
        self.server_name = server_name
        self.server_script_path = Path(server_script_path)
        self.verbose = verbose
        self.session: Optional[ClientSession] = None
        self.read = None
        self.write = None
        self._exit_stack = None

    async def connect(self):
        """Connect to the MCP server"""
        if self.verbose:
            print(f"[MCP Client] Connecting to {self.server_name}...")

        # Get Python executable path
        python_exe = sys.executable

        # Server parameters
        server_params = StdioServerParameters(
            command=python_exe,
            args=[str(self.server_script_path.absolute())],
            env=os.environ.copy()
        )

        # Connect to server
        self._exit_stack = asyncio.create_task(self._maintain_connection(server_params))

        # Wait for session to be initialized
        max_wait = 5  # seconds
        waited = 0
        while not self.session and waited < max_wait:
            await asyncio.sleep(0.1)
            waited += 0.1

        if not self.session:
            raise RuntimeError(f"Failed to initialize MCP session after {max_wait}s")

        if self.verbose:
            print(f"[MCP Client] Connected to {self.server_name}")

    async def _maintain_connection(self, server_params: StdioServerParameters):
        """Maintain connection to MCP server"""
        async with stdio_client(server_params) as (read, write):
            self.read = read
            self.write = write
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                if self.verbose:
                    print(f"[MCP Client] Session initialized with {self.server_name}")

                # Keep connection alive
                try:
                    while True:
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    if self.verbose:
                        print(f"[MCP Client] Disconnecting from {self.server_name}")

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self._exit_stack:
            self._exit_stack.cancel()
            try:
                await self._exit_stack
            except asyncio.CancelledError:
                pass

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server

        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        response = await self.session.list_tools()
        return [tool.model_dump() for tool in response.tools]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the MCP server

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool response as string
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        if self.verbose:
            print(f"[MCP Client] Calling tool: {tool_name}")
            print(f"  └─ Arguments: {arguments}")

        result = await self.session.call_tool(tool_name, arguments)

        if self.verbose:
            print(f"[MCP Client] Raw result type: {type(result)}")
            print(f"[MCP Client] Has content: {hasattr(result, 'content')}")
            if hasattr(result, 'content'):
                print(f"[MCP Client] Content length: {len(result.content) if result.content else 0}")

        # Extract text content from result
        if result.content:
            text_parts = []
            for i, content in enumerate(result.content):
                if self.verbose:
                    print(f"[MCP Client] Content[{i}] type: {type(content)}")
                    print(f"[MCP Client] Content[{i}] has text: {hasattr(content, 'text')}")
                if hasattr(content, 'text'):
                    text_parts.append(content.text)
                    if self.verbose:
                        print(f"[MCP Client] Content[{i}] text length: {len(content.text)}")

            response_text = '\n'.join(text_parts)

            if self.verbose:
                preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                print(f"  └─ Response: {preview}")

            return response_text

        if self.verbose:
            print("[MCP Client] No content in result, returning empty string")
        return ""


class SearchMCPClient:
    """Specialized MCP client for the Search server"""

    def __init__(self, verbose: bool = False):
        """
        Initialize Search MCP client

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.project_root = Path(__file__).parent.parent.parent
        self.server_path = self.project_root / "mcp_servers" / "search_server" / "server.py"
        self.client = MCPClient("search-server", str(self.server_path), verbose=verbose)
        self._connected = False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Connect to the search MCP server"""
        if not self._connected:
            await self.client.connect()
            self._connected = True

    async def disconnect(self):
        """Disconnect from the search MCP server"""
        if self._connected:
            await self.client.disconnect()
            self._connected = False

    async def search(self, query: str, num_results: int = 5) -> str:
        """
        Search the web using the MCP server

        Args:
            query: Search query string
            num_results: Number of results to return (1-10)

        Returns:
            Formatted search results
        """
        if not self._connected:
            raise RuntimeError("Not connected to search server. Call connect() first.")

        return await self.client.call_tool(
            "web_search",
            {
                "query": query,
                "num_results": num_results
            }
        )


# Synchronous wrapper for easier use in non-async code
class SearchMCPClientSync:
    """Synchronous wrapper for SearchMCPClient"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._async_client = None
        self._loop = None

    def __enter__(self):
        """Context manager entry"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._async_client = SearchMCPClient(verbose=self.verbose)
        self._loop.run_until_complete(self._async_client.connect())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._async_client:
            self._loop.run_until_complete(self._async_client.disconnect())
        if self._loop:
            self._loop.close()

    def search(self, query: str, num_results: int = 5) -> str:
        """
        Search the web (synchronous)

        Args:
            query: Search query string
            num_results: Number of results to return

        Returns:
            Formatted search results
        """
        if not self._async_client:
            raise RuntimeError("Client not initialized. Use with statement.")

        return self._loop.run_until_complete(
            self._async_client.search(query, num_results)
        )
