# Agentic AI Evaluation Framework Comparison

A comprehensive project comparing three evaluation libraries (TrueLens, DeepEval, and Pydantic Eval) for assessing an AutoGen-based multi-agent research assistant in Mechanistic Interpretability.

## Project Overview

This project consists of two main components:

1. **AutoGen Multi-Agent System**: A research assistant specialized in Mechanistic Interpretability with three domain-expert agents
2. **Evaluation Framework**: Comparative evaluation using TrueLens, DeepEval, and Pydantic Eval

## Agent Architecture

### Agent 1: Feature Extraction & Interpretability Specialist
**Domain expertise:**
- Monosemanticity and polysemanticity concepts
- Sparse Autoencoders (SAEs) and dictionary learning
- Feature visualization and attribution techniques
- Superposition and disentanglement

**Tool proficiency:** TransformerLens, SAELens (as applied to feature extraction)

**Handles questions like:**
- "Explain how SAEs achieve monosemanticity in GPT-4"
- "What is superposition and why does it matter?"
- "How do I extract interpretable features using SAELens?"

### Agent 2: Circuits & Mechanistic Analysis Specialist
**Domain expertise:**
- Attention head analysis and patterns
- MLP layer interpretation
- Circuit discovery and reverse engineering
- Causal interventions and ablation studies
- Information flow through networks

**Tool proficiency:** TransformerLens for circuit analysis, activation patching

**Handles questions like:**
- "What circuits implement indirect object identification?"
- "How do attention heads compose in transformers?"
- "How can I use activation patching to test causal hypotheses?"

### Agent 3: Research Synthesizer & Trend Analyst
**Domain expertise:**
- Current state-of-the-art in mechanistic interpretability
- Key research papers and breakthroughs
- Emerging techniques and open problems
- Cross-domain connections and future directions

**Responsibilities:**
- Tracks latest publications (arXiv, research blogs, conferences)
- Synthesizes insights from other agents
- Identifies knowledge gaps and research opportunities
- Provides high-level overviews and summaries

**Handles questions like:**
- "What are the latest developments in mechanistic interpretability?"
- "What are the open problems in the field?"
- "How does recent SAE research build on earlier work?"

## Project Structure

```
evals-comparison/
├── src/
│   ├── agents/                    # AutoGen agent implementations
│   │   ├── feature_extraction/   # Agent 1: Feature & Interpretability
│   │   ├── circuits_analysis/    # Agent 2: Circuits & Mechanisms
│   │   └── research_synthesizer/ # Agent 3: Research & Trends
│   ├── tools/                    # Shared tools
│   │   ├── mcp_client.py         # MCP client for connecting to servers
│   │   └── llm_interface.py      # OpenAI LLM interface
│   ├── config/                   # Configuration files
│   └── main.py                   # Application entry point
├── mcp_servers/                  # MCP server implementations
│   └── search_server/            # Google Custom Search MCP server
│       ├── server.py             # MCP server implementation
│       └── README.md             # Server documentation
├── evals/                        # Evaluation frameworks
│   ├── truelens/                 # TrueLens evaluator
│   ├── deepeval/                 # DeepEval evaluator
│   └── pydantic_eval/           # Pydantic Eval evaluator
├── tests/                        # Unit and integration tests
├── data/                         # Research papers and cached data
├── results/                      # Evaluation results (JSON)
├── logs/                         # Application logs
└── notebooks/                    # Jupyter notebooks for analysis

```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

### Quick Start

**Interactive mode** (with conversation history):
```bash
python src/main.py
```

**Single query mode** (for automation):
```bash
python src/main.py --query "What is monosemanticity?"
```

**Verbose mode** (see agent collaboration and search activity):
```bash
python src/main.py --verbose
```

### Current Status

**Implemented:**
- Agent 1: Feature Extraction & Interpretability Specialist (fully functional)
  - **MCP-based web search** via Google Custom Search
  - Domain expertise in SAEs, monosemanticity, TransformerLens/SAELens
  - Interactive and single-query modes
  - Verbose logging for debugging
- **MCP Search Server**: Standalone search server using Model Context Protocol
  - Google Custom Search integration
  - Clean separation of concerns
  - Reusable across projects

**Coming Soon:**
- Agent 2: Circuits & Mechanistic Analysis Specialist
- Agent 3: Research Synthesizer & Trend Analyst
- Multi-agent collaboration
- Evaluation frameworks (TrueLens, DeepEval, Pydantic Eval)

### Example Usage

```bash
# Ask about a concept
$ python src/main.py --query "What is monosemanticity?" --verbose

# Interactive session
$ python src/main.py
> What are sparse autoencoders?
[Answer appears...]
> How do they relate to dictionary learning?
[Follow-up answer with context...]
> /exit
```

### Running Tests
```bash
pytest tests/
```

## Evaluation Metrics

The project evaluates agents across multiple dimensions using DeepEval:

### Core Metrics
- **Answer Relevancy**: Measures how relevant the answer is to the question
- **Technical Accuracy**: Evaluates correct use of mechanistic interpretability concepts and terminology
- **Correctness**: Assesses factual correctness against expected outputs
- **Research Quality**: Evaluates depth, structure, examples, and completeness of research responses

### Context-Based Metrics (when sources are retrieved)
- **Faithfulness**: Checks if answers are grounded in retrieved sources
- **Source Credibility**: Evaluates quality, recency, and authority of sources used
- **Contextual Precision**: Measures if relevant sources are ranked highly
- **Contextual Recall**: Checks if all relevant information is retrieved

### System Performance Metrics
- **Response Time**: Tracks inference time for each query
- **Agent Collaboration Effectiveness**: Composite metric evaluating:
  - Routing effectiveness (correct specialist selection)
  - Response time efficiency
  - Answer quality (aggregate of quality metrics)
  - Resource utilization (appropriate search usage)

Results are stored in JSON format in the `evals/deepeval/results/` directory for comparative analysis.

## Contributing

This is a research and comparison project. Contributions are welcome.

## License

MIT License
