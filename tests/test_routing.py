"""
Unit tests for query routing logic

Tests the intelligent routing between agents
"""

import pytest
from unittest.mock import Mock, patch
from src.main import ResearchAssistant


class TestRouting:
    """Test suite for query routing"""

    @pytest.fixture
    def assistant(self):
        """Create ResearchAssistant with mocked agents"""
        with patch('src.main.FeatureExtractionAgent') as mock_feature, \
             patch('src.main.CircuitsAnalysisAgent') as mock_circuits:

            assistant = ResearchAssistant(verbose=False)

            # Store mock agents for verification
            assistant.mock_feature_agent = mock_feature.return_value
            assistant.mock_circuits_agent = mock_circuits.return_value

            return assistant

    def test_route_to_circuits_agent_circuit_keyword(self, assistant):
        """Test routing circuit-related queries to Circuits Agent"""
        queries = [
            "Explain the IOI circuit",
            "How does this circuit work?",
            "What circuits are involved?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Circuits & Mechanistic Analysis Specialist", f"Failed for: {query}"
            assert agent == assistant.circuits_agent

    def test_route_to_circuits_agent_attention_head(self, assistant):
        """Test routing attention head queries to Circuits Agent"""
        queries = [
            "What are induction heads?",
            "Explain attention patterns",
            "How do attention heads work?",
            "Describe the QK circuit"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Circuits & Mechanistic Analysis Specialist", f"Failed for: {query}"

    def test_route_to_circuits_agent_technique(self, assistant):
        """Test routing technique queries to Circuits Agent"""
        queries = [
            "How does activation patching work?",
            "Explain causal tracing",
            "What is ablation study?",
            "How to do path patching?",
            "What is logit attribution?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Circuits & Mechanistic Analysis Specialist", f"Failed for: {query}"

    def test_route_to_feature_agent_monosemanticity(self, assistant):
        """Test routing monosemanticity queries to Feature Agent"""
        queries = [
            "What is monosemanticity?",
            "Explain polysemanticity",
            "How does monosemanticity relate to interpretability?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Feature Extraction & Interpretability Specialist", f"Failed for: {query}"
            assert agent == assistant.feature_agent

    def test_route_to_feature_agent_sae(self, assistant):
        """Test routing SAE queries to Feature Agent"""
        queries = [
            "What is a sparse autoencoder?",
            "How do SAEs work?",
            "Explain dictionary learning",
            "What is feature extraction?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Feature Extraction & Interpretability Specialist", f"Failed for: {query}"

    def test_route_to_feature_agent_tools(self, assistant):
        """Test routing tool queries to Feature Agent"""
        queries = [
            "How to use TransformerLens?",
            "SAELens documentation",
            "TransformerLens feature extraction"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Feature Extraction & Interpretability Specialist", f"Failed for: {query}"

    def test_route_to_feature_agent_superposition(self, assistant):
        """Test routing superposition queries to Feature Agent"""
        queries = [
            "What is superposition?",
            "Explain feature visualization",
            "How does superposition affect interpretability?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Feature Extraction & Interpretability Specialist", f"Failed for: {query}"

    def test_route_default_to_feature_agent(self, assistant):
        """Test that ambiguous queries default to Feature Agent"""
        queries = [
            "What is mechanistic interpretability?",
            "Tell me about recent research",
            "How do neural networks work?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Feature Extraction & Interpretability Specialist", f"Failed for: {query}"

    def test_route_mixed_keywords_circuits_wins(self, assistant):
        """Test routing when query has both types of keywords, circuits wins"""
        # Query with more circuits keywords
        query = "How do attention heads use activation patching to analyze circuits?"

        agent_name, agent = assistant._route_query(query)
        assert agent_name == "Circuits & Mechanistic Analysis Specialist"

    def test_route_mixed_keywords_features_wins(self, assistant):
        """Test routing when query has both types of keywords, features wins"""
        # Query with more features keywords
        query = "How do sparse autoencoders relate to monosemanticity and feature extraction?"

        agent_name, agent = assistant._route_query(query)
        assert agent_name == "Feature Extraction & Interpretability Specialist"

    def test_route_case_insensitive(self, assistant):
        """Test that routing is case-insensitive"""
        queries = [
            "WHAT ARE INDUCTION HEADS?",
            "what is monosemanticity?",
            "How Does ACTIVATION PATCHING Work?"
        ]

        # Should not raise errors and should route correctly
        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name is not None
            assert agent is not None

    def test_route_ioi_keyword(self, assistant):
        """Test that IOI specifically routes to Circuits Agent"""
        queries = [
            "Explain the IOI circuit",
            "What is indirect object identification?",
            "How does IOI work?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Circuits & Mechanistic Analysis Specialist", f"Failed for: {query}"

    def test_route_mechanism_keyword(self, assistant):
        """Test that mechanism queries route to Circuits Agent"""
        queries = [
            "What is the mechanism behind this?",
            "Explain the underlying mechanism",
            "How does the mechanism work?"
        ]

        for query in queries:
            agent_name, agent = assistant._route_query(query)
            assert agent_name == "Circuits & Mechanistic Analysis Specialist", f"Failed for: {query}"


class TestProcessQuery:
    """Test the complete process_query workflow"""

    @pytest.fixture
    def assistant(self):
        """Create assistant with fully mocked agents"""
        with patch('src.main.FeatureExtractionAgent') as mock_feature, \
             patch('src.main.CircuitsAnalysisAgent') as mock_circuits:

            # Mock agent responses
            mock_feature.return_value.answer_question.return_value = {
                "answer": "Feature agent answer",
                "sources": [],
                "search_queries": ["query1", "query2"],
                "question_type": "concept"
            }

            mock_circuits.return_value.answer_question.return_value = {
                "answer": "Circuits agent answer",
                "sources": [],
                "search_queries": ["query1"],
                "question_type": "circuit_analysis"
            }

            assistant = ResearchAssistant(verbose=False)
            return assistant

    def test_process_query_routes_and_adds_metadata(self, assistant):
        """Test that process_query routes correctly and adds metadata"""
        result = assistant.process_query("What are induction heads?")

        # Should have routed to circuits agent
        assert "answer" in result
        assert "time_seconds" in result
        assert "agents" in result
        assert "search_count" in result

        # Metadata should be correct
        assert isinstance(result["time_seconds"], float)
        assert result["time_seconds"] >= 0
        assert len(result["agents"]) == 1
        assert result["search_count"] >= 0

    def test_process_query_feature_agent_called(self, assistant):
        """Test that Feature Agent is called for appropriate queries"""
        result = assistant.process_query("What is monosemanticity?")

        # Verify Feature Agent was called
        assert assistant.feature_agent.answer_question.called
        assert result["agents"] == ["Feature Extraction & Interpretability Specialist"]

    def test_process_query_circuits_agent_called(self, assistant):
        """Test that Circuits Agent is called for appropriate queries"""
        result = assistant.process_query("What are induction heads?")

        # Verify Circuits Agent was called
        assert assistant.circuits_agent.answer_question.called
        assert result["agents"] == ["Circuits & Mechanistic Analysis Specialist"]
