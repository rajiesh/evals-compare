"""
Main entry point for Mechanistic Interpretability Research Assistant
"""

import sys
import argparse
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.cli import create_parser, print_banner, print_verbose_header, print_collaboration_summary, CLIModes
from src.agents.feature_extraction.agent import FeatureExtractionAgent
from src.agents.circuits_analysis.agent import CircuitsAnalysisAgent


class ResearchAssistant:
    """Main research assistant orchestrator"""

    def __init__(self, verbose: bool = False, quiet: bool = False):
        """
        Initialize research assistant

        Args:
            verbose: Show detailed agent activity
            quiet: Only show final answers
        """
        self.verbose = verbose and not quiet
        self.quiet = quiet

        # Initialize agents
        self.feature_agent = FeatureExtractionAgent(verbose=self.verbose)
        self.circuits_agent = CircuitsAnalysisAgent(verbose=self.verbose)

        # Track active agents
        self.active_agents = {
            "feature_extraction": self.feature_agent,
            "circuits_analysis": self.circuits_agent,
            # "research_synthesizer": None,  # TODO: Implement
        }

    def _route_query(self, query: str) -> tuple[str, any]:
        """
        Route query to the most appropriate agent

        Args:
            query: User's question

        Returns:
            Tuple of (agent_name, agent_instance)
        """
        query_lower = query.lower()

        # Keywords for Circuits Analysis Agent
        circuits_keywords = [
            "circuit", "attention head", "induction head", "mechanism",
            "activation patching", "causal tracing", "ablation",
            "information flow", "path patching", "logit attribution",
            "attention pattern", "qk circuit", "ov circuit",
            "indirect object identification", "ioi"
        ]

        # Keywords for Feature Extraction Agent
        features_keywords = [
            "monosemanticity", "polysemanticity", "sparse autoencoder", "sae",
            "dictionary learning", "feature visualization", "superposition",
            "transformerlens", "saelens", "feature extraction"
        ]

        # Check for circuits-related queries
        circuits_score = sum(1 for keyword in circuits_keywords if keyword in query_lower)
        features_score = sum(1 for keyword in features_keywords if keyword in query_lower)

        # Route based on keyword matching
        if circuits_score > features_score:
            return "Circuits & Mechanistic Analysis Specialist", self.circuits_agent
        else:
            # Default to Feature Extraction agent
            return "Feature Extraction & Interpretability Specialist", self.feature_agent

    def process_query(self, query: str) -> dict:
        """
        Process a user query

        Args:
            query: User's question

        Returns:
            Response dictionary with answer and metadata
        """
        start_time = time.time()

        if self.verbose:
            print_verbose_header(query)

        # Route query to appropriate agent
        agent_name, agent = self._route_query(query)

        if self.verbose:
            print(f"\n[Routing] Forwarding to {agent_name}")

        response = agent.answer_question(
            question=query,
            search_web=True
        )

        end_time = time.time()
        elapsed = end_time - start_time

        # Add metadata
        response["time_seconds"] = elapsed
        response["agents"] = [agent_name]
        response["search_count"] = len(response.get("search_queries", []))

        return response

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
