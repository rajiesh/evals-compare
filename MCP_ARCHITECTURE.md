# MCP Architecture Documentation

## Overview

This project uses **Model Context Protocol (MCP)** for tool integration, providing a clean separation between agents and their tools. This document explains the architecture and benefits.

## What is MCP?

Model Context Protocol is a standardized way for AI agents to interact with external tools and data sources. Instead of tightly coupling tools into agent code, MCP:
- Runs tools as **separate server processes**
- Provides a **standardized interface** for communication
- Enables **tool reusability** across different projects and agents

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface (CLI)                   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Agent System (src/main.py)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Agent 1: Feature Extraction Specialist          │   │
│  │  - Uses MCP Client to call tools                 │   │
│  │  - Domain expertise in SAEs, monosemanticity     │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────┘
                      │ MCP Protocol
                      │ (stdio, async)
┌─────────────────────▼───────────────────────────────────┐
│              MCP Client (src/tools/mcp_client.py)        │
│  - SearchMCPClientSync: Synchronous wrapper              │
│  - SearchMCPClient: Async MCP client                     │
│  - MCPClient: Generic MCP client                         │
└─────────────────────┬───────────────────────────────────┘
                      │ stdio communication
                      │ (subprocess)
┌─────────────────────▼───────────────────────────────────┐
│       MCP Server: Search (mcp_servers/search_server/)    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Tool: web_search                                 │   │
│  │  - query: string                                  │   │
│  │  - num_results: int (1-10)                        │   │
│  └──────────────────┬───────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│         Google Custom Search API                         │
└─────────────────────────────────────────────────────────┘
```

## Key Components

### 1. MCP Server (`mcp_servers/search_server/server.py`)

**Responsibilities:**
- Runs as independent process
- Implements `web_search` tool
- Handles Google Custom Search API calls
- Returns formatted results

**Interface:**
```python
Tool: web_search
  Input:
    - query (string): Search query
    - num_results (int): Number of results (1-10)
  Output:
    - Formatted text with search results (titles, URLs, snippets)
```

**Why separate process?**
- **Isolation**: Crashes don't affect agents
- **Reusability**: Any MCP-compatible agent can use it
- **Scaling**: Can run on different machines
- **Testing**: Easy to test independently

### 2. MCP Client (`src/tools/mcp_client.py`)

**Responsibilities:**
- Connect to MCP servers via subprocess
- Manage server lifecycle (start, stop)
- Call tools via MCP protocol
- Handle async/sync conversion

**Classes:**
- `MCPClient`: Generic client for any MCP server
- `SearchMCPClient`: Specialized for search server (async)
- `SearchMCPClientSync`: Synchronous wrapper for easy use

**Usage Example:**
```python
# Synchronous (for use in agents)
with SearchMCPClientSync(verbose=True) as client:
    results = client.search("monosemanticity", num_results=5)
    print(results)

# Async (for advanced use)
async with SearchMCPClient(verbose=True) as client:
    results = await client.search("SAEs", num_results=10)
```

### 3. Agent Integration

Agents use MCP client within their methods:

```python
def answer_question(self, question: str):
    # Generate search queries
    queries = self._generate_search_queries(question)

    # Use MCP client for searching
    with SearchMCPClientSync(verbose=self.verbose) as client:
        all_results = []
        for query in queries:
            results = client.search(query, num_results=5)
            all_results.append(results)

    # Process results with LLM
    answer = self.llm.chat_completion(...)
    return answer
```

## Benefits of MCP Architecture

### 1. Separation of Concerns
- **Agents** focus on reasoning and domain expertise
- **Tools** focus on specific capabilities (search, file I/O, etc.)
- Clear boundaries make code maintainable

### 2. Reusability
- Same search server can be used by:
  - All 3 agents in this project
  - Other projects using MCP
  - Different programming languages (MCP is language-agnostic)

### 3. Easier Testing
```bash
# Test MCP server independently
python mcp_servers/search_server/server.py

# Test agents with mock MCP server
# No need to mock Google API - mock the MCP server instead
```

### 4. Better for Evaluations
- Can swap search implementations without changing agent code
- Compare different search strategies (Google vs Brave vs Tavily)
- Measure tool usage patterns separately from agent reasoning

### 5. Scalability
```
Development:     Agent + MCP Server on same machine
Production:      Agent on server A, MCP Server on server B
Multi-tenant:    Multiple agents sharing one MCP server instance
```

## Configuration

### Environment Variables

```bash
# For MCP Search Server
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_search_engine_id
```

The MCP server reads these from the environment when started by the client.

### Server Discovery

Currently, the search server path is hardcoded in the client:
```python
self.server_path = self.project_root / "mcp_servers" / "search_server" / "server.py"
```

Future improvement: Use MCP server registry for dynamic discovery.

## Adding New MCP Servers

To add a new MCP server (e.g., ArXiv paper fetcher):

1. **Create server directory:**
   ```bash
   mkdir -p mcp_servers/arxiv_server
   ```

2. **Implement server (`server.py`):**
   ```python
   from mcp.server import Server

   class ArxivMCPServer:
       def __init__(self):
           self.server = Server("arxiv-server")
           self.server.list_tools()(self.list_tools)
           self.server.call_tool()(self.call_tool)

       async def list_tools(self):
           return [Tool(name="fetch_paper", ...)]

       async def call_tool(self, name, arguments):
           # Implement tool logic
           pass
   ```

3. **Create client wrapper:**
   ```python
   class ArxivMCPClient:
       def __init__(self):
           self.client = MCPClient("arxiv-server", "path/to/server.py")

       async def fetch_paper(self, arxiv_id):
           return await self.client.call_tool("fetch_paper", {"id": arxiv_id})
   ```

4. **Use in agents:**
   ```python
   with ArxivMCPClient() as client:
       paper = client.fetch_paper("2301.12345")
   ```

## Comparison: Before vs After MCP

### Before (Direct Integration)
```python
class FeatureExtractionAgent:
    def __init__(self):
        self.search_tool = WebSearchTool()  # Tightly coupled
        self.search_tool.api_key = settings.GOOGLE_API_KEY

    def answer(self, question):
        results = self.search_tool.search(question)  # Direct call
```

**Problems:**
- Agent owns search implementation
- Hard to swap search providers
- Testing requires mocking Google API
- Can't reuse search tool in other projects

### After (MCP)
```python
class FeatureExtractionAgent:
    def answer(self, question):
        with SearchMCPClientSync() as client:  # Loose coupling
            results = client.search(question)  # Via MCP protocol
```

**Benefits:**
- Agent doesn't know about Google API
- Easy to swap MCP servers (Google → Brave)
- Testing: mock MCP server, not Google
- Search server works in any MCP-compatible project

## Performance Considerations

### Overhead
- **Process startup**: ~100-200ms (one-time per session)
- **IPC communication**: ~1-5ms per tool call (negligible)
- **Network requests**: Unchanged (Google API latency dominates)

### Optimization
- MCP client uses context managers to reuse connections
- Server stays alive across multiple tool calls
- Async architecture prevents blocking

## Future Enhancements

1. **Multiple Search Backends**
   - Add SerpAPI, Brave Search to MCP server
   - Agent selects backend via parameter

2. **Server Registry**
   - Dynamic server discovery
   - Version management
   - Health checks

3. **Caching Layer**
   - Move caching into MCP server
   - Share cache across all agents

4. **Monitoring**
   - Tool usage metrics
   - Performance tracking
   - Error rates

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/anthropics/mcp)
- [AutoGen + MCP Integration](https://microsoft.github.io/autogen/)

## Questions?

For questions about the MCP architecture in this project:
1. Check [mcp_servers/search_server/README.md](mcp_servers/search_server/README.md)
2. Review [src/tools/mcp_client.py](src/tools/mcp_client.py)
3. See example usage in [src/agents/feature_extraction/agent.py](src/agents/feature_extraction/agent.py)
