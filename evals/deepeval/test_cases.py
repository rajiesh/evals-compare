"""
Test cases for DeepEval evaluation

Organized by agent specialty and difficulty level
"""

from typing import List, Dict

# Feature Extraction Agent Test Cases
FEATURE_EXTRACTION_CASES = [
    {
        "query": "What is superposition in neural networks?",
        "expected_output": (
            "Superposition is a phenomenon where neural networks represent more features "
            "than they have dimensions by storing multiple features in the same set of neurons. "
            "This happens because models can represent n features in m dimensions (where n > m) "
            "by using almost-orthogonal directions in activation space. It's a key challenge "
            "for interpretability because it makes neurons polysemantic."
        ),
        "difficulty": "medium",
        "category": "concept_explanation"
    },
    {
        "query": "How do I train a sparse autoencoder with SAELens?",
        "expected_output": (
            "To train a sparse autoencoder with SAELens: (1) Load your model using TransformerLens, "
            "(2) Collect activation data from a target layer, (3) Initialize an SAE with SAELens "
            "specifying the dictionary size and sparsity coefficient, (4) Train using the provided "
            "trainer with your activation dataset, (5) Evaluate sparsity and reconstruction loss. "
            "SAELens provides pre-trained SAEs and utilities for training custom ones."
        ),
        "difficulty": "hard",
        "category": "tool_usage"
    },
    {
        "query": "What is dictionary learning?",
        "expected_output": (
            "Dictionary learning is a technique for finding a set of basis vectors (dictionary) "
            "that can sparsely represent data. In mechanistic interpretability, it's used to "
            "decompose neural network activations into interpretable features. Sparse autoencoders "
            "perform dictionary learning by learning an overcomplete basis where activations can "
            "be represented as sparse linear combinations of dictionary elements."
        ),
        "difficulty": "medium",
        "category": "concept_explanation"
    },
    {
        "query": "Explain the difference between linear and nonlinear feature extraction",
        "expected_output": (
            "Linear feature extraction uses linear transformations (like PCA) to find features, "
            "assuming features combine linearly. Nonlinear methods (like autoencoders with "
            "nonlinear activations) can capture more complex feature relationships. For neural "
            "network interpretability, sparse autoencoders with ReLU activations are common "
            "nonlinear methods that can learn more expressive feature dictionaries than linear "
            "approaches."
        ),
        "difficulty": "hard",
        "category": "concept_explanation"
    }
]

# Circuits Analysis Agent Test Cases
CIRCUITS_ANALYSIS_CASES = [
    {
        "query": "What is the IOI circuit?",
        "expected_output": (
            "The Indirect Object Identification (IOI) circuit is a specific computational circuit "
            "discovered in GPT-2 Small that performs the task of identifying indirect objects in "
            "sentences. It involves specific attention heads working together: name mover heads "
            "that move information from previous mentions of names, duplicate token heads that "
            "detect repeated tokens, and induction heads. This circuit demonstrates how "
            "interpretable algorithms can emerge in language models."
        ),
        "difficulty": "hard",
        "category": "circuit_analysis"
    },
    {
        "query": "How does causal tracing differ from activation patching?",
        "expected_output": (
            "Causal tracing and activation patching are related but distinct. Causal tracing is "
            "a systematic method that patches activations from a clean run into a corrupted run "
            "to trace where information is processed. Activation patching is the broader technique "
            "of replacing activations. Causal tracing specifically uses it to track information "
            "flow by seeing which patches restore correct behavior, helping identify which "
            "components are causally relevant."
        ),
        "difficulty": "hard",
        "category": "technique"
    },
    {
        "query": "What are QK and OV circuits?",
        "expected_output": (
            "QK (Query-Key) and OV (Output-Value) circuits are the two main computational paths "
            "in transformer attention heads. The QK circuit determines the attention pattern by "
            "computing dot products between queries and keys. The OV circuit determines what "
            "information is moved by transforming values and combining them according to attention "
            "weights. Analyzing these circuits separately helps understand what heads attend to "
            "(QK) versus what they write to the residual stream (OV)."
        ),
        "difficulty": "medium",
        "category": "attention_head"
    },
    {
        "query": "Explain the path patching technique",
        "expected_output": (
            "Path patching is a refinement of activation patching that patches activations only "
            "along specific computational paths through the network. Instead of patching all "
            "activations at a layer, you patch only the subset that flows through a particular "
            "path (e.g., from one attention head through specific MLPs to an output). This gives "
            "more precise causal understanding by isolating individual paths and their "
            "contributions to model behavior."
        ),
        "difficulty": "hard",
        "category": "technique"
    },
    {
        "query": "What is an attention head and how does it work?",
        "expected_output": (
            "An attention head is a component in transformers that moves information between "
            "positions in a sequence. Each head computes attention patterns (which positions to "
            "attend to) using queries and keys, then moves information using values weighted by "
            "these attention scores. Different heads in a model specialize in different patterns "
            "like copying, induction, or positional attention. Multiple heads in a layer work "
            "in parallel and their outputs are combined."
        ),
        "difficulty": "medium",
        "category": "attention_head"
    }
]

# Mixed/General Test Cases
GENERAL_TEST_CASES = [
    {
        "query": "How can I get started with mechanistic interpretability research?",
        "expected_output": (
            "To get started with mechanistic interpretability: (1) Learn the fundamentals of "
            "transformers and attention mechanisms, (2) Study key papers like 'In-context Learning "
            "and Induction Heads' and 'Towards Monosemanticity', (3) Practice with TransformerLens "
            "library to analyze small models, (4) Experiment with techniques like activation "
            "patching and attention pattern analysis, (5) Join the community through Alignment "
            "Forum, LessWrong, or research discords. Start with small models like GPT-2 Small."
        ),
        "difficulty": "easy",
        "category": "general"
    },
    {
        "query": "Compare sparse autoencoders and activation patching",
        "expected_output": (
            "Sparse autoencoders and activation patching are complementary techniques. SAEs are "
            "used to decompose activations into interpretable features (feature extraction). "
            "Activation patching is used to determine which components causally matter for "
            "behaviors (causal analysis). You might use SAEs to find what features exist, then "
            "use activation patching to determine which features are causally important. Together "
            "they help both identify features and understand their role in model computation."
        ),
        "difficulty": "hard",
        "category": "general"
    }
]

# Edge cases and challenging queries
EDGE_CASES = [
    {
        "query": "sae",
        "expected_output": (
            "SAE stands for Sparse Autoencoder. SAEs are neural networks used in mechanistic "
            "interpretability to decompose model activations into sparse, interpretable features."
        ),
        "difficulty": "easy",
        "category": "abbreviation"
    },
    {
        "query": "What's the latest research on circuits in large language models?",
        "expected_output": None,  # Requires web search, no fixed expected output
        "difficulty": "hard",
        "category": "current_research"
    },
    {
        "query": "How does gradient descent relate to mechanistic interpretability?",
        "expected_output": (
            "Gradient descent is the optimization algorithm that trains neural networks, but "
            "mechanistic interpretability focuses on understanding what the trained model has "
            "learned. While gradient descent creates the circuits and features we study, "
            "interpretability research typically analyzes the final trained model. However, "
            "understanding how circuits form during training (developmental interpretability) "
            "is an emerging area that does study gradient descent's role."
        ),
        "difficulty": "hard",
        "category": "general"
    }
]


def get_all_test_cases() -> List[Dict]:
    """Get all test cases combined"""
    return (
        FEATURE_EXTRACTION_CASES +
        CIRCUITS_ANALYSIS_CASES +
        GENERAL_TEST_CASES +
        EDGE_CASES
    )


def get_test_cases_by_category(category: str) -> List[Dict]:
    """Get test cases filtered by category"""
    all_cases = get_all_test_cases()
    return [case for case in all_cases if case.get("category") == category]


def get_test_cases_by_difficulty(difficulty: str) -> List[Dict]:
    """Get test cases filtered by difficulty"""
    all_cases = get_all_test_cases()
    return [case for case in all_cases if case.get("difficulty") == difficulty]


# Quick test suite (subset for rapid iteration)
QUICK_TEST_SUITE = [
    FEATURE_EXTRACTION_CASES[0],  # Superposition
    CIRCUITS_ANALYSIS_CASES[0],   # IOI circuit
    GENERAL_TEST_CASES[0]          # Getting started
]
