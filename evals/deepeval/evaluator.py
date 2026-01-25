"""
DeepEval Evaluator for Mechanistic Interpretability Research Assistant

Evaluates the AI research assistant using DeepEval metrics:
- Answer Relevancy: Is the answer relevant to the question?
- Faithfulness: Is the answer grounded in retrieved sources?
- Contextual Precision: Are relevant sources ranked highly?
- Contextual Recall: Are all relevant sources retrieved?
- Correctness: Is the answer factually correct?
- Custom Metrics: Domain-specific evaluations
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    GEval
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from src.main import ResearchAssistant
from src.config.settings import settings


class DeepEvalEvaluator:
    """DeepEval-based evaluator for the research assistant"""

    def __init__(self, verbose: bool = False):
        """
        Initialize DeepEval evaluator

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.assistant = ResearchAssistant(verbose=verbose)
        self.results_dir = Path("evals/deepeval/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def create_test_case(
        self,
        input_query: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[List[str]] = None
    ) -> LLMTestCase:
        """
        Create a DeepEval test case

        Args:
            input_query: The user's question
            actual_output: The assistant's answer
            expected_output: Optional ground truth answer
            retrieval_context: Optional list of retrieved documents

        Returns:
            LLMTestCase object
        """
        return LLMTestCase(
            input=input_query,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context
        )

    def evaluate_single_query(
        self,
        query: str,
        expected_output: Optional[str] = None,
        use_all_metrics: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate a single query using DeepEval metrics

        Args:
            query: User question
            expected_output: Optional ground truth answer
            use_all_metrics: Whether to use all available metrics

        Returns:
            Dictionary with evaluation results
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"[DeepEval] Evaluating query: {query}")
            print(f"{'='*60}")

        # Get answer from assistant
        start_time = time.time()
        response = self.assistant.process_query(query)
        inference_time = time.time() - start_time

        actual_output = response.get("answer", "")
        search_results_text = response.get("search_results_text", "")

        # Parse retrieval context from search results
        retrieval_context = self._parse_retrieval_context(search_results_text)

        # Create test case
        test_case = self.create_test_case(
            input_query=query,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context if retrieval_context else None
        )

        # Define metrics to evaluate
        metrics = []

        # Answer Relevancy - measures how relevant the answer is to the question
        # Use gpt-4o-mini which supports structured outputs and is cost-effective
        metrics.append(AnswerRelevancyMetric(
            threshold=0.7,
            model="gpt-4o-mini",
            include_reason=True
        ))

        if retrieval_context:
            # Faithfulness - checks if answer is grounded in retrieved sources
            metrics.append(FaithfulnessMetric(
                threshold=0.7,
                model="gpt-4o-mini",
                include_reason=True
            ))

            # Contextual Precision - checks if relevant contexts are ranked high
            if expected_output:
                metrics.append(ContextualPrecisionMetric(
                    threshold=0.7,
                    model="gpt-4o-mini",
                    include_reason=True
                ))

            # Contextual Recall - checks if all relevant info is retrieved
            if expected_output:
                metrics.append(ContextualRecallMetric(
                    threshold=0.7,
                    model="gpt-4o-mini",
                    include_reason=True
                ))

        # Custom G-Eval metric for technical correctness
        if use_all_metrics:
            correctness_metric = GEval(
                name="Correctness",
                criteria="Determine whether the actual output is factually correct based on the expected output.",
                evaluation_params=[
                    LLMTestCaseParams.INPUT,
                    LLMTestCaseParams.ACTUAL_OUTPUT,
                    LLMTestCaseParams.EXPECTED_OUTPUT
                ],
                threshold=0.7,
                model="gpt-4o-mini"
            )
            if expected_output:
                metrics.append(correctness_metric)

            # Domain-specific metric for mechanistic interpretability
            mech_interp_metric = GEval(
                name="Technical Accuracy",
                criteria=(
                    "Evaluate if the answer demonstrates accurate understanding of "
                    "mechanistic interpretability concepts, correctly uses technical "
                    "terminology, and provides precise explanations."
                ),
                evaluation_params=[
                    LLMTestCaseParams.INPUT,
                    LLMTestCaseParams.ACTUAL_OUTPUT
                ],
                threshold=0.7,
                model="gpt-4o-mini"
            )
            metrics.append(mech_interp_metric)

        # Run evaluation
        if self.verbose:
            print(f"\n[DeepEval] Running {len(metrics)} metrics...")

        results = {}
        for metric in metrics:
            metric_start = time.time()
            try:
                metric.measure(test_case)
                metric_time = time.time() - metric_start

                metric_name = metric.__name__
                results[metric_name] = {
                    "score": metric.score,
                    "threshold": metric.threshold,
                    "success": metric.is_successful(),
                    "reason": getattr(metric, "reason", None),
                    "evaluation_time": metric_time
                }

                if self.verbose:
                    status = "✓" if metric.is_successful() else "✗"
                    print(f"  {status} {metric_name}: {metric.score:.3f} (threshold: {metric.threshold})")

            except Exception as e:
                metric_name = getattr(metric, '__name__', 'Unknown')
                if self.verbose:
                    print(f"  ✗ {metric_name}: Error - {str(e)}")
                results[metric_name] = {
                    "score": 0.0,
                    "threshold": getattr(metric, 'threshold', 0.0),
                    "success": False,
                    "error": str(e)
                }

        # Compile full results
        eval_results = {
            "query": query,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "agent_used": response.get("agents", ["Unknown"])[0],
            "question_type": response.get("question_type", "unknown"),
            "search_queries": response.get("search_queries", []),
            "num_retrieval_contexts": len(retrieval_context) if retrieval_context else 0,
            "inference_time": inference_time,
            "metrics": results,
            "overall_success": all(m.get("success", False) for m in results.values()),
            "timestamp": datetime.now().isoformat()
        }

        return eval_results

    def evaluate_test_suite(
        self,
        test_cases: List[Dict[str, str]],
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases

        Args:
            test_cases: List of dicts with 'query' and optional 'expected_output'
            save_results: Whether to save results to JSON

        Returns:
            Dictionary with aggregated results
        """
        if self.verbose:
            print(f"\n[DeepEval] Evaluating {len(test_cases)} test cases...")

        all_results = []
        start_time = time.time()

        for i, test_case in enumerate(test_cases, 1):
            if self.verbose:
                print(f"\n[{i}/{len(test_cases)}] Processing test case...")

            query = test_case["query"]
            expected = test_case.get("expected_output")

            result = self.evaluate_single_query(query, expected)
            all_results.append(result)

        total_time = time.time() - start_time

        # Calculate aggregate statistics
        aggregate_stats = self._calculate_aggregate_stats(all_results)
        aggregate_stats["total_test_cases"] = len(test_cases)
        aggregate_stats["total_evaluation_time"] = total_time
        aggregate_stats["avg_time_per_case"] = total_time / len(test_cases)

        final_results = {
            "evaluation_framework": "DeepEval",
            "model": settings.OPENAI_MODEL,
            "timestamp": datetime.now().isoformat(),
            "aggregate_stats": aggregate_stats,
            "individual_results": all_results
        }

        # Save results
        if save_results:
            output_file = self.results_dir / f"deepeval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(final_results, f, indent=2)

            if self.verbose:
                print(f"\n[DeepEval] Results saved to {output_file}")

        return final_results

    def _parse_retrieval_context(self, search_results_text: str) -> List[str]:
        """
        Parse search results into list of context strings

        Args:
            search_results_text: Formatted search results text

        Returns:
            List of context strings (snippets)
        """
        if not search_results_text:
            return []

        contexts = []
        # Split by result markers like [1], [2], etc.
        import re
        results = re.split(r'\[\d+\]', search_results_text)

        for result in results[1:]:  # Skip first empty split
            lines = result.strip().split('\n')
            # Extract snippet (last non-empty line)
            snippet = None
            for line in reversed(lines):
                line = line.strip()
                if line and not line.startswith('URL:'):
                    snippet = line
                    break

            if snippet:
                contexts.append(snippet)

        return contexts

    def _calculate_aggregate_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate statistics from individual results

        Args:
            results: List of individual evaluation results

        Returns:
            Dictionary with aggregate statistics
        """
        total_cases = len(results)
        successful_cases = sum(1 for r in results if r["overall_success"])

        # Collect metric scores
        metric_scores = {}
        for result in results:
            for metric_name, metric_data in result["metrics"].items():
                if metric_name not in metric_scores:
                    metric_scores[metric_name] = []
                if "score" in metric_data and isinstance(metric_data["score"], (int, float)):
                    metric_scores[metric_name].append(metric_data["score"])

        # Calculate averages
        avg_metric_scores = {
            name: sum(scores) / len(scores) if scores else 0.0
            for name, scores in metric_scores.items()
        }

        # Agent routing stats
        agent_usage = {}
        for result in results:
            agent = result.get("agent_used", "Unknown")
            agent_usage[agent] = agent_usage.get(agent, 0) + 1

        return {
            "total_cases": total_cases,
            "successful_cases": successful_cases,
            "success_rate": successful_cases / total_cases if total_cases > 0 else 0.0,
            "average_inference_time": sum(r["inference_time"] for r in results) / total_cases,
            "average_metric_scores": avg_metric_scores,
            "agent_usage": agent_usage
        }


# Predefined test cases for mechanistic interpretability domain
MECH_INTERP_TEST_CASES = [
    {
        "query": "What are sparse autoencoders and how do they help with interpretability?",
        "expected_output": (
            "Sparse autoencoders (SAEs) are neural networks that learn to represent data "
            "using sparse activations. In mechanistic interpretability, they help decompose "
            "neural network activations into interpretable features by learning a "
            "overcomplete dictionary of features where only a few are active at once. "
            "This helps address the superposition problem where models represent many "
            "features in fewer dimensions."
        )
    },
    {
        "query": "Explain what induction heads are in transformer models",
        "expected_output": (
            "Induction heads are attention head patterns that implement in-context learning "
            "in transformers. They work by copying information from previous positions where "
            "a similar pattern appeared. An induction head consists of a previous token head "
            "that attends to the token before the current one, and an induction head that "
            "attends to positions after instances of that token earlier in the sequence."
        )
    },
    {
        "query": "How does activation patching work?",
        "expected_output": (
            "Activation patching is a causal intervention technique where you replace "
            "(patch) activations at specific components of a neural network with activations "
            "from a different input, then measure the effect on the output. This helps "
            "determine which components are causally important for specific behaviors or "
            "outputs. It's more precise than ablation because you replace with meaningful "
            "values rather than zeros."
        )
    },
    {
        "query": "What is the difference between monosemanticity and polysemanticity?",
        "expected_output": (
            "Monosemanticity means a neuron responds to a single, interpretable feature or "
            "concept. Polysemanticity means a neuron responds to multiple unrelated features. "
            "Polysemanticity makes interpretability harder because you can't assign a clear "
            "meaning to the neuron. It arises from superposition, where models represent "
            "more features than they have dimensions by storing multiple features in the "
            "same neuron."
        )
    },
    {
        "query": "How can I use TransformerLens to analyze attention patterns?",
        "expected_output": (
            "TransformerLens provides tools to hook into transformer models and extract "
            "attention patterns. You can use cache hooks to capture attention weights, "
            "visualize attention patterns across heads and layers, and analyze which tokens "
            "attend to which. Key methods include running models with caching enabled, "
            "accessing the cache for attention patterns, and using built-in visualization "
            "utilities to plot attention heatmaps."
        )
    }
]


def run_demo_evaluation(verbose: bool = True):
    """
    Run a demo evaluation with predefined test cases

    Args:
        verbose: Enable verbose output
    """
    evaluator = DeepEvalEvaluator(verbose=verbose)

    print("\n" + "="*70)
    print("DeepEval Evaluation Demo - Mechanistic Interpretability Assistant")
    print("="*70)

    # Run evaluation on test suite
    results = evaluator.evaluate_test_suite(
        test_cases=MECH_INTERP_TEST_CASES,
        save_results=True
    )

    # Print summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)

    stats = results["aggregate_stats"]
    print(f"\nTotal Test Cases: {stats['total_cases']}")
    print(f"Successful Cases: {stats['successful_cases']} ({stats['success_rate']*100:.1f}%)")
    print(f"Avg Inference Time: {stats['average_inference_time']:.2f}s")
    print(f"\nAgent Usage:")
    for agent, count in stats['agent_usage'].items():
        print(f"  - {agent}: {count} queries")

    print(f"\nAverage Metric Scores:")
    for metric, score in stats['average_metric_scores'].items():
        print(f"  - {metric}: {score:.3f}")

    print("\n" + "="*70)

    return results


if __name__ == "__main__":
    # Run demo evaluation
    run_demo_evaluation(verbose=True)
