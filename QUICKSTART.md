# Quick Start Guide

Get up and running with the Mechanistic Interpretability Research Assistant in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Google Custom Search API credentials (API key + Search Engine ID)

## Installation

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required - OpenAI for LLM
OPENAI_API_KEY=sk-your-openai-key-here

# Required - Google Custom Search for MCP Search Server
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_CSE_ID=your-custom-search-engine-id-here
```

**How to get Google Custom Search credentials:**
1. **API Key**: Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Create a project (or use existing)
   - Enable "Custom Search API"
   - Create credentials → API Key
2. **Search Engine ID**: Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Create a new search engine
   - Configure it to search the entire web
   - Copy your Search Engine ID

### 4. Verify Setup

Test that everything is configured correctly:

```bash
python -c "from src.config.settings import settings; print('✓ Config loaded successfully' if settings.validate() else '✗ Config error')"
```

## Usage Examples

### Interactive Mode

Start a conversation with the research assistant:

```bash
python src/main.py
```

Example session:
```
> What is monosemanticity?
[Agent explains monosemanticity with sources...]

> How do sparse autoencoders achieve this?
[Agent explains SAEs with context from previous question...]

> /exit
```

### Single Query Mode

Ask a single question and get an answer:

```bash
python src/main.py --query "What is superposition in neural networks?"
```

### Verbose Mode

See detailed agent activity (great for understanding how it works):

```bash
python src/main.py --verbose
```

Output will show:
- Query routing decisions
- Search queries generated
- Web search results
- LLM API calls
- Collaboration summary

### Example Queries

Try these questions to explore the agent's capabilities:

**Concept Explanations:**
```bash
python src/main.py --query "What is monosemanticity?"
python src/main.py --query "Explain superposition in neural networks"
python src/main.py --query "What are the benefits of sparse autoencoders?"
```

**Tool Usage:**
```bash
python src/main.py --query "How do I use TransformerLens to extract activations?"
python src/main.py --query "What is SAELens and how do I get started?"
```

**Research Questions:**
```bash
python src/main.py --query "What recent papers discuss feature interpretability?"
python src/main.py --query "How does Anthropic's work on SAEs relate to dictionary learning?"
```

## Interactive Commands

When in interactive mode, you can use these commands:

- `/help` - Show available commands
- `/agents` - List active agents and their specialties
- `/history` - Show conversation history
- `/clear` - Clear conversation history
- `/exit` - Exit the assistant

## Troubleshooting

### "OPENAI_API_KEY is not set"

Make sure you've created a `.env` file and added your OpenAI API key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### "GOOGLE_API_KEY or GOOGLE_CSE_ID not configured"

The MCP Search Server requires Google Custom Search credentials:
1. **API Key**: [Get from Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Search Engine ID**: [Create at Programmable Search Engine](https://programmablesearchengine.google.com/)

Add both to your `.env` file.

### Import Errors

Make sure you're running from the project root directory and have activated your virtual environment:
```bash
cd /path/to/evals-comparison
source venv/bin/activate
python src/main.py
```

### Module Not Found: 'autogen' or 'mcp'

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

Key packages:
- `pyautogen` - AutoGen framework
- `mcp` - Model Context Protocol
- `openai` - OpenAI API client

## What's Next?

Now that you have Agent 1 working, you can:

1. **Test different queries** - Try various mechanistic interpretability questions
2. **Explore verbose mode** - Understand how the agent searches and reasons
3. **Wait for more agents** - Agents 2 and 3 are coming soon!
4. **Start thinking about evaluations** - What aspects of agent performance matter most to you?

## Current Status

**Fully Implemented:**
- ✅ Agent 1 (Feature Extraction Specialist) - Working with MCP-based search
- ✅ MCP Search Server - Standalone Google Custom Search server
- ✅ CLI Interface - Interactive and single-query modes
- ✅ Verbose logging and debugging

**Coming Soon:**
- Agent 2 (Circuits Analysis) - Not yet implemented
- Agent 3 (Research Synthesizer) - Not yet implemented
- Multi-agent collaboration - Not yet implemented
- Evaluation frameworks - Not yet implemented

These will be added incrementally, starting with the bottom-up approach (one agent at a time).

## Architecture Highlights

This project uses **Model Context Protocol (MCP)** for tool integration:
- **MCP Server** (`mcp_servers/search_server/`): Runs as separate process, provides web search
- **MCP Client** (`src/tools/mcp_client.py`): Agents connect to MCP servers
- **Benefits**: Clean separation, reusable tools, easier testing

## Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your `.env` configuration
3. Try running in verbose mode to see detailed logs
4. Check that all dependencies are installed correctly

## Example Output

Here's what to expect when you run a query:

```bash
$ python src/main.py --query "What is monosemanticity?" --verbose

============================================================
QUERY: What is monosemanticity?
============================================================

[Routing] Forwarding to Feature Extraction Specialist

[Feature Extraction Agent] Processing question
  └─ Question type: concept_explanation

[Feature Extraction Agent] Generating search queries...
  └─ Query 1: monosemanticity neural networks anthropic
  └─ Query 2: sparse autoencoders monosemantic features

[Feature Extraction Agent] Searching web...
  └─ Searching for: 'monosemanticity neural networks anthropic'
  └─ Found 5 results via SerpAPI

[Feature Extraction Agent] Found 10 total results

[Feature Extraction Agent] Generating answer...
  └─ Calling gpt-4 (temp=0.7)
  └─ Response received (1243 tokens)

============================================================
ANSWER:
============================================================

Monosemanticity refers to the property of neural network features...
[Full answer with sources]

------------------------------------------------------------
COLLABORATION SUMMARY:
  Agents involved: Feature Extraction Specialist
  Web searches: 2
  Response time: 8.3s
------------------------------------------------------------
```

Happy researching!
