# Search MCP Server

A Model Context Protocol (MCP) server providing Google Custom Search functionality.

## Features

- Google Custom Search API integration
- Configurable number of results (1-10)
- Formatted output optimized for LLM consumption
- Async/await architecture for performance

## Configuration

The server requires two environment variables:

```bash
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

## Running the Server

The server runs as a subprocess managed by your MCP client (e.g., AutoGen agents):

```bash
python mcp_servers/search_server/server.py
```

## Available Tools

### web_search

Search the web using Google Custom Search.

**Parameters:**
- `query` (string, required): The search query
- `num_results` (integer, optional): Number of results to return (1-10, default: 5)

**Returns:**
Formatted text with search results including titles, URLs, and snippets.

**Example:**
```json
{
  "name": "web_search",
  "arguments": {
    "query": "sparse autoencoders mechanistic interpretability",
    "num_results": 5
  }
}
```

## Integration with Agents

This MCP server is designed to work with the Mechanistic Interpretability Research Assistant agents. It provides web search capabilities for:

- Finding research papers
- Locating documentation
- Discovering technical resources
- Tracking recent developments in the field

## Future Enhancements

Possible additions:
- SerpAPI backend support
- Brave Search integration
- Result caching
- Domain filtering
- Date range filtering
- Advanced search operators
