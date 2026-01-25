"""
Main entry point for Mechanistic Interpretability Research Assistant
"""

import sys
import argparse
import time
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.cli import create_parser, print_banner, print_verbose_header, print_collaboration_summary, CLIModes
from src.agents.feature_extraction.agent import FeatureExtractionAgent
from src.agents.circuits_analysis.agent import CircuitsAnalysisAgent

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient


class ResearchAssistant:
    """Main research assistant orchestrator with tool-based routing"""

    def __init__(self, verbose: bool = False, quiet: bool = False):
        """
        Initialize research assistant

        Args:
            verbose: Show detailed agent activity
            quiet: Only show final answers
        """
        self.verbose = verbose and not quiet
        self.quiet = quiet

        # Initialize specialist agents
        self.feature_agent = FeatureExtractionAgent(verbose=self.verbose)
        self.circuits_agent = CircuitsAnalysisAgent(verbose=self.verbose)

        # Track active agents
        self.active_agents = {
            "feature_extraction": self.feature_agent,
            "circuits_analysis": self.circuits_agent,
        }

        # Create orchestrator agent with tool-based routing
        self.model_client = OpenAIChatCompletionClient(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

        # Create orchestrator with specialist agents as tools
        self.orchestrator = AssistantAgent(
            name="QueryOrchestrator",
            model_client=self.model_client,
            tools=[self._route_to_feature_specialist, self._route_to_circuits_specialist],
            system_message=self._get_orchestrator_prompt(),
        )

    def _get_orchestrator_prompt(self) -> str:
        """Get the system prompt for the orchestrator agent"""
        return """You are a query routing orchestrator for a Mechanistic Interpretability Research Assistant.

Your role is to analyze user questions and route them to the most appropriate specialist agent by calling the right tool function.

Available specialists:

1. **Feature Extraction & Interpretability Specialist** - Use for questions about:
   - Monosemanticity and polysemanticity
   - Sparse Autoencoders (SAEs) and dictionary learning
   - Feature visualization and attribution
   - TransformerLens and SAELens tools and usage
   - Superposition and feature representations

2. **Circuits & Mechanistic Analysis Specialist** - Use for questions about:
   - Circuit discovery and analysis (IOI, greater-than, etc.)
   - Attention head patterns and behavior
   - Induction heads and attention mechanisms
   - Causal interventions (activation patching, causal tracing)
   - Ablation studies and information flow
   - QK and OV circuits

Instructions:
- Analyze the user's question carefully
- Determine which specialist is most appropriate
- Call the corresponding tool function with the user's question
- Return the specialist's answer directly

If a question covers multiple areas, route to the specialist whose expertise is most relevant to the core question."""

    def _route_to_feature_specialist(self, question: str) -> str:
        """
        Route question to Feature Extraction & Interpretability Specialist.

        Use this for questions about monosemanticity, polysemanticity, sparse autoencoders (SAEs),
        dictionary learning, feature visualization, superposition, TransformerLens, and SAELens.

        Args:
            question: The user's question about feature extraction or interpretability

        Returns:
            The specialist's answer
        """
        if self.verbose:
            print("\n[Routing] Forwarding to Feature Extraction & Interpretability Specialist")

        result = self.feature_agent.answer_question(question, search_web=True)
        self._last_agent_result = result
        self._last_agent_name = "Feature Extraction & Interpretability Specialist"
        return result["answer"]

    def _route_to_circuits_specialist(self, question: str) -> str:
        """
        Route question to Circuits & Mechanistic Analysis Specialist.

        Use this for questions about circuit discovery, attention heads, induction heads,
        activation patching, causal tracing, ablation studies, and information flow.

        Args:
            question: The user's question about circuits or mechanistic analysis

        Returns:
            The specialist's answer
        """
        if self.verbose:
            print("\n[Routing] Forwarding to Circuits & Mechanistic Analysis Specialist")

        result = self.circuits_agent.answer_question(question, search_web=True)
        self._last_agent_result = result
        self._last_agent_name = "Circuits & Mechanistic Analysis Specialist"
        return result["answer"]

    def process_query(self, query: str) -> dict:
        """
        Process a user query using tool-based routing

        Args:
            query: User's question

        Returns:
            Response dictionary with answer and metadata
        """
        start_time = time.time()

        if self.verbose:
            print_verbose_header(query)

        # Initialize tracking variables
        self._last_agent_result = None
        self._last_agent_name = None

        # Use orchestrator to route query via tool-based routing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            answer = loop.run_until_complete(self._route_with_orchestrator(query))
        finally:
            # Clean up async resources
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception:
                pass
            finally:
                loop.close()

        end_time = time.time()
        elapsed = end_time - start_time

        # Build response from orchestrator result
        if self._last_agent_result:
            response = self._last_agent_result.copy()
            response["answer"] = answer
        else:
            # Fallback if orchestrator didn't call a tool
            response = {
                "answer": answer,
                "agent": "Orchestrator",
                "question_type": "direct",
                "search_queries": [],
                "search_results_text": "",
                "used_search": False,
                "sources": []
            }

        # Add metadata
        response["time_seconds"] = elapsed
        response["agents"] = [self._last_agent_name] if self._last_agent_name else ["Orchestrator"]
        response["search_count"] = len(response.get("search_queries", []))

        return response

    async def _route_with_orchestrator(self, query: str) -> str:
        """
        Use orchestrator agent to route query via function calling

        Args:
            query: User's question

        Returns:
            Answer from the routed specialist agent
        """
        message = TextMessage(content=query, source="User")
        response = await self.orchestrator.on_messages([message], cancellation_token=None)

        # Extract answer from response
        if hasattr(response, 'chat_message'):
            answer = str(response.chat_message.content) if hasattr(response.chat_message, 'content') else str(response.chat_message)
        else:
            answer = str(response)

        return answer

    def interactive_mode(self):
        """Run interactive session with conversation history"""
        print_banner()

        conversation_history = []

        print("\nReady! Type your question or /help for commands.\n")

        while True:
            try:
                user_input = input("> ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/exit" or user_input == "/quit":
                        print("\nGoodbye!")
                        break
                    elif user_input == "/help":
                        self._print_help()
                        continue
                    elif user_input == "/agents":
                        self._print_agents()
                        continue
                    elif user_input == "/history":
                        self._print_history(conversation_history)
                        continue
                    elif user_input == "/clear":
                        conversation_history = []
                        print("\nConversation history cleared.")
                        continue
                    else:
                        print(f"Unknown command: {user_input}")
                        print("Type /help for available commands.")
                        continue

                # Process query
                response = self.process_query(user_input)

                # Save to history
                conversation_history.append({
                    "query": user_input,
                    "response": response
                })

                # Display answer
                if not self.quiet:
                    print(f"\n{'='*60}")
                    print("ANSWER:")
                    print(f"{'='*60}\n")

                print(response["answer"])

                # Display sources if verbose
                if self.verbose and response.get("sources"):
                    print(f"\n{'-'*60}")
                    print("SOURCES:")
                    for i, source in enumerate(response["sources"][:5], 1):
                        print(f"[{i}] {source.title}")
                        print(f"    {source.url}")

                # Display collaboration summary
                if self.verbose:
                    print_collaboration_summary(response)
                else:
                    print()  # Empty line for spacing

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /exit to quit or continue asking questions.")
                continue
            except Exception as e:
                print(f"\nError: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                continue

    def single_query_mode(self, query: str):
        """Process a single query and exit"""
        response = self.process_query(query)

        # Print answer
        print(response["answer"])

        # Print summary if verbose
        if self.verbose:
            print_collaboration_summary(response)

    def _print_help(self):
        """Print help message"""
        help_text = """
Available Commands:
  /help     - Show this help message
  /agents   - List active agents and their specialties
  /history  - Show conversation history
  /clear    - Clear conversation history
  /exit     - Exit the assistant

Tips:
  - Ask questions about mechanistic interpretability concepts
  - Request explanations of techniques like SAEs, monosemanticity
  - Get help using tools like TransformerLens or SAELens
  - Inquire about recent research and developments
        """
        print(help_text)

    def _print_agents(self):
        """Print active agents"""
        print("\nActive Agents:")
        print("  [1] Feature Extraction & Interpretability Specialist")
        print("      - Monosemanticity, SAEs, dictionary learning")
        print("      - TransformerLens and SAELens expertise")
        print()
        print("  [2] Circuits & Mechanistic Analysis Specialist")
        print("      - Circuit discovery and analysis")
        print("      - Attention head patterns and behavior")
        print("      - Causal interventions and ablation studies")
        print()
        print("Coming soon:")
        print("  [3] Research Synthesizer & Trend Analyst")
        print()

    def _print_history(self, history: list):
        """Print conversation history"""
        if not history:
            print("\nNo conversation history yet.")
            return

        print(f"\nConversation History ({len(history)} exchanges):")
        print("-" * 60)
        for i, exchange in enumerate(history, 1):
            print(f"\n[{i}] Q: {exchange['query']}")
            # Print first 100 chars of answer
            answer_preview = exchange['response']['answer'][:100]
            print(f"    A: {answer_preview}...")
        print()


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Validate configuration
    if not settings.validate():
        print("\nPlease configure your .env file with required API keys.")
        print("See .env.example for reference.")
        sys.exit(1)

    # Determine verbosity
    verbose = args.verbose if hasattr(args, 'verbose') else False
    quiet = args.quiet if hasattr(args, 'quiet') else False

    # Initialize assistant
    assistant = ResearchAssistant(verbose=verbose, quiet=quiet)

    # Determine mode
    if hasattr(args, 'eval') and args.eval:
        print(f"\n[Eval] Running {args.eval} evaluation...")
        print("[INFO] Evaluation mode not yet implemented")
    elif hasattr(args, 'eval_all') and args.eval_all:
        print("\n[Eval] Running all evaluations...")
        print("[INFO] Evaluation mode not yet implemented")
    elif hasattr(args, 'query') and args.query:
        assistant.single_query_mode(args.query)
    else:
        assistant.interactive_mode()


if __name__ == "__main__":
    main()
