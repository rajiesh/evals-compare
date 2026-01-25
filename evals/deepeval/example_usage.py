"""
Example usage of DeepEval evaluator

Shows how to:
1. Create custom test cases
2. Run single query evaluation
3. Run batch evaluation
4. Access and analyze results
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from evals.deepeval.evaluator import DeepEvalEvaluator


def example_1_single_query():
    """Example 1: Evaluate a single query"""
    print("\n" + "="*70)
    print("Example 1: Single Query Evaluation")
    print("="*70)

    evaluator = DeepEvalEvaluator(verbose=True)

    result = evaluator.evaluate_single_query(
        query="What are sparse autoencoders?",
        expected_output=(
            "Sparse autoencoders are neural networks that learn to represent data "
            "using sparse activations, commonly used in mechanistic interpretability "
            "to decompose model activations into interpretable features."
        )
    )

    print("\n" + "-"*70)
    print("Results:")
    print("-"*70)
    print(f"Query: {result['query']}")
    print(f"Agent: {result['agent_used']}")
    print(f"Success: {result['overall_success']}")
    print(f"Inference Time: {result['inference_time']:.2f}s")
    print("\nMetric Scores:")
    for metric, data in result['metrics'].items():
        status = "✓" if data.get('success', False) else "✗"
        print(f"  {status} {metric}: {data.get('score', 0):.3f}")


def example_2_batch_evaluation():
    """Example 2: Batch evaluation with custom test cases"""
    print("\n" + "="*70)
    print("Example 2: Batch Evaluation")
    print("="*70)

    # Define custom test cases
    test_cases = [
        {
            "query": "What is monosemanticity?",
            "expected_output": "Monosemanticity means a neuron responds to a single interpretable feature."
        },
        {
            "query": "How does activation patching work?",
            "expected_output": "Activation patching replaces activations to measure causal effects."
        },
        {
            "query": "What are induction heads?",
            "expected_output": "Induction heads are attention patterns that enable in-context learning."
        }
    ]

    evaluator = DeepEvalEvaluator(verbose=False)  # Less verbose for batch

    results = evaluator.evaluate_test_suite(
        test_cases=test_cases,
        save_results=True
    )

    # Analyze results
    stats = results['aggregate_stats']

    print("\n" + "-"*70)
    print("Batch Results:")
    print("-"*70)
    print(f"Total Cases: {stats['total_cases']}")
    print(f"Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"Avg Inference Time: {stats['average_inference_time']:.2f}s")

    print("\nMetric Averages:")
    for metric, score in stats['average_metric_scores'].items():
        print(f"  {metric}: {score:.3f}")

    print("\nAgent Usage:")
    for agent, count in stats['agent_usage'].items():
        print(f"  {agent}: {count}")


def example_3_no_expected_output():
    """Example 3: Evaluation without expected output (real-world usage)"""
    print("\n" + "="*70)
    print("Example 3: Evaluation Without Expected Output")
    print("="*70)

    evaluator = DeepEvalEvaluator(verbose=True)

    # When you don't have expected output, only some metrics can run
    result = evaluator.evaluate_single_query(
        query="Explain the QK circuit in transformers",
        expected_output=None  # No ground truth
    )

    print("\n" + "-"*70)
    print("Results (without expected output):")
    print("-"*70)
    print(f"Available Metrics: {list(result['metrics'].keys())}")
    print("\nNote: Contextual Precision/Recall require expected output")


def example_4_analyze_failures():
    """Example 4: Analyzing failed test cases"""
    print("\n" + "="*70)
    print("Example 4: Analyzing Failures")
    print("="*70)

    test_cases = [
        {
            "query": "What is gradient descent?",  # Off-topic
            "expected_output": "An optimization algorithm"
        },
        {
            "query": "How do I use TransformerLens?",
            "expected_output": "TransformerLens is a library for interpretability"
        }
    ]

    evaluator = DeepEvalEvaluator(verbose=False)
    results = evaluator.evaluate_test_suite(test_cases, save_results=False)

    # Find failures
    failed = [r for r in results['individual_results'] if not r['overall_success']]

    print(f"\nFound {len(failed)} failed cases:")
    for fail in failed:
        print(f"\n  Query: {fail['query']}")
        print(f"  Agent: {fail['agent_used']}")
        print("  Failed Metrics:")
        for metric, data in fail['metrics'].items():
            if not data.get('success', False):
                print(f"    - {metric}: {data.get('score', 0):.3f}")
                if 'reason' in data:
                    print(f"      Reason: {data['reason'][:100]}...")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("DeepEval Evaluator - Usage Examples")
    print("="*70)

    # Comment out examples you don't want to run
    example_1_single_query()
    # example_2_batch_evaluation()
    # example_3_no_expected_output()
    # example_4_analyze_failures()

    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70)


if __name__ == "__main__":
    main()
