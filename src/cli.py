"""
CLI Interface for Mechanistic Interpretability Research Assistant

Supports multiple modes:
1. Interactive session with conversation history
2. Single query mode (for automation/eval)
3. Evaluation mode (run test suites)
4. Verbose/quiet output modes
"""

import argparse
import sys
from typing import Optional
from pathlib import Path


class CLIModes:
    """CLI operation modes"""
    INTERACTIVE = "interactive"
    SINGLE_QUERY = "query"
    EVAL = "eval"


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser with all supported modes"""
    parser = argparse.ArgumentParser(
        description="Mechanistic Interpretability Research Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with conversation history
  python src/main.py

  # Single query mode (stateless)
  python src/main.py --query "What is monosemanticity?"

  # Verbose mode (show agent collaboration)
  python src/main.py --verbose

  # Run evaluation with specific framework
  python src/main.py --eval truelens

  # Run all evaluations
  python src/main.py --eval-all

  # Run test suite
  python src/main.py --test-suite data/eval_questions.json
        """
    )

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '-q', '--query',
        type=str,
        help='Single query mode (stateless)',
        metavar='QUESTION'
    )
    mode_group.add_argument(
        '--eval',
        type=str,
        choices=['truelens', 'deepeval', 'pydantic'],
        help='Run evaluation with specified framework'
    )
    mode_group.add_argument(
        '--eval-all',
        action='store_true',
        help='Run evaluations with all frameworks'
    )

    # Output control
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose mode: show agent collaboration, routing, and search activity'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Quiet mode: only show final answers'
    )

    # Evaluation options
    parser.add_argument(
        '--test-suite',
        type=Path,
        help='Path to test suite JSON file',
        metavar='PATH'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for evaluation results (JSON)',
        default=Path('results/eval_results.json')
    )

    # Agent control
    parser.add_argument(
        '--agents',
        type=str,
        nargs='+',
        choices=['feature_extraction', 'circuits_analysis', 'research_synthesizer'],
        help='Restrict to specific agents (default: all)'
    )

    # Session options
    parser.add_argument(
        '--no-history',
        action='store_true',
        help='Disable conversation history (stateless mode)'
    )

    return parser


def print_banner():
    """Print welcome banner for interactive mode"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║   Mechanistic Interpretability Research Assistant           ║
║   Multi-Agent System powered by AutoGen                      ║
╚══════════════════════════════════════════════════════════════╝

Available Agents:
  [1] Feature Extraction & Interpretability Specialist
  [2] Circuits & Mechanistic Analysis Specialist
  [3] Research Synthesizer & Trend Analyst

Commands:
  /help     - Show help
  /agents   - List active agents
  /history  - Show conversation history
  /clear    - Clear conversation history
  /exit     - Exit the assistant

Type your question to begin...
    """
    print(banner)


def print_verbose_header(query: str):
    """Print query header in verbose mode"""
    print("\n" + "="*60)
    print(f"QUERY: {query}")
    print("="*60)


def print_agent_activity(agent_name: str, activity: str, detail: Optional[str] = None):
    """Print agent activity in verbose mode"""
    print(f"\n[{agent_name}] {activity}")
    if detail:
        print(f"  └─ {detail}")


def print_collaboration_summary(data: dict):
    """Print collaboration summary after query completion"""
    print("\n" + "-"*60)
    print("COLLABORATION SUMMARY:")
    print(f"  Agents involved: {', '.join(data.get('agents', []))}")
    print(f"  Web searches: {data.get('search_count', 0)}")
    print(f"  Response time: {data.get('time_seconds', 0):.1f}s")
    print("-"*60 + "\n")


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Determine mode
    if args.eval or args.eval_all:
        mode = CLIModes.EVAL
    elif args.query:
        mode = CLIModes.SINGLE_QUERY
    else:
        mode = CLIModes.INTERACTIVE

    # TODO: Initialize agent system here
    # from src.agent_system import AgentSystem
    # system = AgentSystem(verbose=args.verbose, agents=args.agents)

    if mode == CLIModes.INTERACTIVE:
        print_banner()
        # TODO: Start interactive session
        print("\n[INFO] Interactive mode not yet implemented")
        print("[INFO] Use --query for single query mode")

    elif mode == CLIModes.SINGLE_QUERY:
        # TODO: Process single query
        print(f"\n[Query] {args.query}")
        print("[INFO] Single query mode not yet implemented")

    elif mode == CLIModes.EVAL:
        # TODO: Run evaluation
        print(f"\n[Eval] Running {args.eval} evaluation...")
        print("[INFO] Evaluation mode not yet implemented")


if __name__ == "__main__":
    main()
