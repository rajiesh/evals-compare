# DeepEval Evaluation Framework

DeepEval integration for evaluating the Mechanistic Interpretability Research Assistant.

## Overview

This directory contains DeepEval-based evaluations that measure:

- **Answer Relevancy**: How relevant is the answer to the question?
- **Faithfulness**: Is the answer grounded in retrieved sources?
- **Contextual Precision**: Are relevant sources ranked highly?
- **Contextual Recall**: Are all relevant sources retrieved?
- **Technical Accuracy**: Domain-specific accuracy for mech interp concepts
- **Correctness**: Factual correctness compared to expected output

## Quick Start

### Run Quick Evaluation (3 test cases)

```bash
python evals/deepeval/run_evaluation.py --quick
```

### Run Full Evaluation Suite

```bash
python evals/deepeval/run_evaluation.py --full
```

### Run by Category

```bash
# Circuits-related queries
python evals/deepeval/run_evaluation.py --category circuit_analysis

# Feature extraction queries
python evals/deepeval/run_evaluation.py --category concept_explanation

# Technique/methodology queries
python evals/deepeval/run_evaluation.py --category technique
```

### Run by Agent

```bash
# Test Feature Extraction Agent
python evals/deepeval/run_evaluation.py --agent feature

# Test Circuits Analysis Agent
python evals/deepeval/run_evaluation.py --agent circuits
```

### Run by Difficulty

```bash
python evals/deepeval/run_evaluation.py --difficulty easy
python evals/deepeval/run_evaluation.py --difficulty medium
python evals/deepeval/run_evaluation.py --difficulty hard
```

## Files

- `evaluator.py` - Main DeepEval evaluator implementation
- `test_cases.py` - Predefined test cases organized by category and difficulty
- `run_evaluation.py` - CLI tool for running evaluations
- `results/` - Evaluation results (JSON format)

## Metrics Explained

### Answer Relevancy
Measures how relevant the answer is to the user's question. Uses GPT-4 to evaluate if the answer addresses the query.

**Threshold**: 0.7

### Faithfulness
Checks if the answer is grounded in the retrieved sources. Ensures the model doesn't hallucinate information not present in search results.

**Threshold**: 0.7

### Contextual Precision
Evaluates if the most relevant search results are ranked highest. Requires expected output to determine relevance.

**Threshold**: 0.7

### Contextual Recall
Checks if all relevant information from sources is retrieved. Measures completeness of retrieval.

**Threshold**: 0.7

### Technical Accuracy (Custom G-Eval)
Domain-specific metric that evaluates:
- Correct use of mechanistic interpretability terminology
- Accuracy of technical concepts
- Precision of explanations

**Threshold**: 0.7

### Correctness (Custom G-Eval)
Compares actual output to expected output for factual correctness. Only runs when expected output is provided.

**Threshold**: 0.7

## Test Cases

Test cases are organized by:

1. **Agent**: Which agent should handle this query
   - Feature Extraction Agent
   - Circuits Analysis Agent
   - General queries

2. **Category**: Type of question
   - `circuit_analysis` - Questions about specific circuits
   - `technique` - Questions about interpretability methods
   - `attention_head` - Questions about attention mechanisms
   - `concept_explanation` - Conceptual questions
   - `tool_usage` - How to use tools like TransformerLens, SAELens
   - `general` - General mechanistic interpretability questions

3. **Difficulty**: Complexity level
   - `easy` - Simple questions, basic concepts
   - `medium` - Requires deeper understanding
   - `hard` - Complex concepts, multi-part questions

## Adding New Test Cases

Edit `test_cases.py` and add to the appropriate list:

```python
{
    "query": "Your question here",
    "expected_output": "Expected answer (optional)",
    "difficulty": "easy|medium|hard",
    "category": "circuit_analysis|technique|etc"
}
```

## Results

Results are saved as JSON in `evals/deepeval/results/` with format:

```json
{
  "evaluation_framework": "DeepEval",
  "timestamp": "2026-01-18T...",
  "aggregate_stats": {
    "total_cases": 10,
    "successful_cases": 8,
    "success_rate": 0.8,
    "average_inference_time": 4.2,
    "average_metric_scores": {
      "Answer Relevancy": 0.85,
      "Faithfulness": 0.78,
      ...
    },
    "agent_usage": {
      "Feature Extraction Agent": 5,
      "Circuits Analysis Agent": 5
    }
  },
  "individual_results": [...]
}
```

## Cost Considerations

Each metric evaluation uses GPT-4 API calls:
- Answer Relevancy: 1 call per test case
- Faithfulness: 1 call per test case
- Contextual Precision: 1 call per test case
- Contextual Recall: 1 call per test case
- Technical Accuracy: 1 call per test case
- Correctness: 1 call per test case

**Estimated cost per test case**: ~6 GPT-4 API calls (varies based on which metrics apply)

**Quick suite (3 cases)**: ~18 GPT-4 calls (~$0.50)
**Full suite (~15 cases)**: ~90 GPT-4 calls (~$2.50)

## Programmatic Usage

```python
from evals.deepeval.evaluator import DeepEvalEvaluator
from evals.deepeval.test_cases import QUICK_TEST_SUITE

evaluator = DeepEvalEvaluator(verbose=True)

# Evaluate single query
result = evaluator.evaluate_single_query(
    query="What are sparse autoencoders?",
    expected_output="SAEs are neural networks..."
)

# Evaluate test suite
results = evaluator.evaluate_test_suite(
    test_cases=QUICK_TEST_SUITE,
    save_results=True
)

print(f"Success rate: {results['aggregate_stats']['success_rate']}")
```

## Next Steps

After running evaluations:

1. Review results in `evals/deepeval/results/`
2. Identify failing test cases
3. Analyze metric scores to find weaknesses
4. Compare with TrueLens and Pydantic eval results
5. Iterate on prompts and agent logic
