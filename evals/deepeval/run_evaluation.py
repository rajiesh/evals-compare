#!/usr/bin/env python3
"""
Convenient runner for DeepEval evaluations

Usage:
    python evals/deepeval/run_evaluation.py --quick       # Run quick test suite
    python evals/deepeval/run_evaluation.py --full        # Run full test suite
    python evals/deepeval/run_evaluation.py --category circuits  # Run category
    python evals/deepeval/run_evaluation.py --difficulty easy    # Run by difficulty
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from evals.deepeval.evaluator import DeepEvalEvaluator, MECH_INTERP_TEST_CASES
from evals.deepeval.test_cases import (
    get_all_test_cases,
    get_test_cases_by_category,
    get_test_cases_by_difficulty,
    QUICK_TEST_SUITE,
    FEATURE_EXTRACTION_CASES,
    CIRCUITS_ANALYSIS_CASES,
    GENERAL_TEST_CASES
)


def main():
    parser = argparse.ArgumentParser(
        description="Run DeepEval evaluations on the Research Assistant"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick test suite (3 cases)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full test suite (all cases)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo test suite (predefined in evaluator)"
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["circuit_analysis", "technique", "attention_head",
                 "concept_explanation", "tool_usage", "general"],
        help="Run test cases from specific category"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        help="Run test cases of specific difficulty"
    )
    parser.add_argument(
        "--agent",
        type=str,
        choices=["feature", "circuits", "general"],
        help="Run test cases for specific agent"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Enable verbose output (default: True)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable verbose output"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to file"
    )

    args = parser.parse_args()

    # Determine test cases to run
    test_cases = None
    description = ""

    if args.quick:
        test_cases = QUICK_TEST_SUITE
        description = "Quick Test Suite"
    elif args.full:
        test_cases = get_all_test_cases()
        description = "Full Test Suite"
    elif args.demo:
        test_cases = MECH_INTERP_TEST_CASES
        description = "Demo Test Suite"
    elif args.category:
        test_cases = get_test_cases_by_category(args.category)
        description = f"Category: {args.category}"
    elif args.difficulty:
        test_cases = get_test_cases_by_difficulty(args.difficulty)
        description = f"Difficulty: {args.difficulty}"
    elif args.agent:
        if args.agent == "feature":
            test_cases = FEATURE_EXTRACTION_CASES
            description = "Feature Extraction Agent Tests"
        elif args.agent == "circuits":
            test_cases = CIRCUITS_ANALYSIS_CASES
            description = "Circuits Analysis Agent Tests"
        else:
            test_cases = GENERAL_TEST_CASES
            description = "General Tests"
    else:
        # Default to quick suite
        test_cases = QUICK_TEST_SUITE
        description = "Quick Test Suite (default)"

    if not test_cases:
        print(f"No test cases found for the specified criteria")
        return 1

    # Run evaluation
    verbose = args.verbose and not args.quiet
    save_results = not args.no_save

    print("\n" + "="*70)
    print(f"DeepEval Evaluation - {description}")
    print(f"Test Cases: {len(test_cases)}")
    print("="*70)

    evaluator = DeepEvalEvaluator(verbose=verbose)
    results = evaluator.evaluate_test_suite(
        test_cases=test_cases,
        save_results=save_results
    )

    # Print summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)

    stats = results["aggregate_stats"]
    print(f"\nTest Suite: {description}")
    print(f"Total Cases: {stats['total_cases']}")
    print(f"Successful: {stats['successful_cases']} ({stats['success_rate']*100:.1f}%)")
    print(f"Avg Inference Time: {stats['average_inference_time']:.2f}s")
    print(f"Total Evaluation Time: {stats['total_evaluation_time']:.2f}s")

    print(f"\nAgent Routing:")
    for agent, count in stats['agent_usage'].items():
        print(f"  • {agent}: {count} queries")

    print(f"\nMetric Scores (Average):")
    for metric, score in sorted(stats['average_metric_scores'].items()):
        # Color code based on score
        if score >= 0.7:
            status = "✓"
        else:
            status = "✗"
        print(f"  {status} {metric}: {score:.3f}")

    print("\n" + "="*70)

    # Print failed cases if any
    failed_cases = [
        r for r in results["individual_results"]
        if not r["overall_success"]
    ]

    if failed_cases:
        print("\nFAILED TEST CASES:")
        print("="*70)
        for i, case in enumerate(failed_cases, 1):
            print(f"\n[{i}] Query: {case['query']}")
            print(f"    Agent: {case['agent_used']}")
            for metric_name, metric_data in case['metrics'].items():
                if not metric_data.get('success', False):
                    score = metric_data.get('score', 0)
                    threshold = metric_data.get('threshold', 0)
                    print(f"    ✗ {metric_name}: {score:.3f} (threshold: {threshold})")
                    if 'reason' in metric_data and metric_data['reason']:
                        print(f"      Reason: {metric_data['reason'][:200]}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
