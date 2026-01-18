"""
Unit tests for Circuits Analysis Agent

Uses mocks to avoid LLM API calls and costs
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.circuits_analysis.agent import CircuitsAnalysisAgent


class TestCircuitsAnalysisAgent:
    """Test suite for Circuits Analysis Agent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return CircuitsAnalysisAgent(verbose=False)

    @pytest.fixture
    def mock_llm_interface(self):
        """Mock LLM interface to avoid API calls"""
        with patch('src.agents.circuits_analysis.agent.LLMInterface') as mock:
            instance = mock.return_value
            instance.chat_completion.return_value = "Mocked LLM response"
            instance.create_system_message.return_value = {"role": "system", "content": "system"}
            instance.create_user_message.return_value = {"role": "user", "content": "user"}
            yield instance

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent is not None
        assert agent.verbose is False
        assert agent.llm is not None

    def test_classify_question_type_circuit_analysis(self, agent):
        """Test classification of circuit analysis questions"""
        questions = [
            "How does the IOI circuit work?",
            "What is the mechanism behind modular arithmetic?",
            "Explain the implementation of the greater-than circuit",
            "How do circuits perform this algorithm?"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "circuit_analysis", f"Failed for: {q}"

    def test_classify_question_type_technique(self, agent):
        """Test classification of technique questions"""
        questions = [
            "How does activation patching work?",
            "Explain causal tracing methodology",
            "What is ablation study?",
            "How to do path patching?",
            "Explain logit attribution technique"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "technique", f"Failed for: {q}"

    def test_classify_question_type_attention_head(self, agent):
        """Test classification of attention head questions"""
        questions = [
            "What are induction heads?",
            "Explain attention patterns in GPT-2",
            "How do attention heads work?",
            "What is key-query attention?",
            "Describe OV circuit behavior"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "attention_head", f"Failed for: {q}"

    def test_classify_question_type_general(self, agent):
        """Test classification of general questions"""
        questions = [
            "Tell me about recent research",
            "What is mechanistic interpretability?",
            "Compare different approaches"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "general", f"Failed for: {q}"

    def test_generate_search_queries(self, agent, mock_llm_interface):
        """Test search query generation"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "circuit query 1\ncircuit query 2"

        queries = agent._generate_search_queries("What are induction heads?")

        assert len(queries) == 2
        assert "circuit query 1" in queries
        assert "circuit query 2" in queries

        # Verify LLM was called
        assert mock_llm_interface.chat_completion.called

    @patch('src.agents.circuits_analysis.agent.SearchMCPClientSync')
    def test_answer_question_circuit_analysis(self, mock_mcp, agent, mock_llm_interface):
        """Test answering circuit analysis questions"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.side_effect = [
            "query one\nquery two",
            "Circuit analysis answer"
        ]

        mock_client = MagicMock()
        mock_client.search.return_value = "Search results"
        mock_mcp.return_value.__enter__.return_value = mock_client

        result = agent.answer_question(
            question="How does the IOI circuit work?",
            search_web=True
        )

        assert result["answer"] == "Circuit analysis answer"
        assert result["question_type"] == "circuit_analysis"
        assert len(result["search_queries"]) == 2

    @patch('src.agents.circuits_analysis.agent.SearchMCPClientSync')
    def test_answer_question_technique(self, mock_mcp, agent, mock_llm_interface):
        """Test answering technique questions"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.side_effect = [
            "technique query",
            "Technique explanation answer"
        ]

        mock_client = MagicMock()
        mock_client.search.return_value = "Search results"
        mock_mcp.return_value.__enter__.return_value = mock_client

        result = agent.answer_question(
            question="How does activation patching work?",
            search_web=True
        )

        assert result["answer"] == "Technique explanation answer"
        assert result["question_type"] == "technique"

    @patch('src.agents.circuits_analysis.agent.SearchMCPClientSync')
    def test_answer_question_attention_head(self, mock_mcp, agent, mock_llm_interface):
        """Test answering attention head questions"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.side_effect = [
            "attention query",
            "Attention head answer"
        ]

        mock_client = MagicMock()
        mock_client.search.return_value = "Search results"
        mock_mcp.return_value.__enter__.return_value = mock_client

        result = agent.answer_question(
            question="What are induction heads?",
            search_web=True
        )

        assert result["answer"] == "Attention head answer"
        assert result["question_type"] == "attention_head"

    def test_answer_question_no_search(self, agent, mock_llm_interface):
        """Test answering without web search"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "Answer without search"

        result = agent.answer_question(
            question="What are circuits?",
            search_web=False
        )

        assert result["answer"] == "Answer without search"
        assert result["search_queries"] == []

    def test_on_search_callback(self, agent, mock_llm_interface):
        """Test that on_search callback is invoked"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.side_effect = [
            "query 1\nquery 2",
            "Answer"
        ]

        callback_calls = []
        def callback(query):
            callback_calls.append(query)

        with patch('src.agents.circuits_analysis.agent.SearchMCPClientSync') as mock_mcp:
            mock_client = MagicMock()
            mock_client.search.return_value = "Results"
            mock_mcp.return_value.__enter__.return_value = mock_client

            agent.answer_question(
                question="Test",
                search_web=True,
                on_search=callback
            )

        assert len(callback_calls) == 2

    def test_verbose_mode(self, mock_llm_interface):
        """Test verbose mode doesn't cause errors"""
        agent = CircuitsAnalysisAgent(verbose=True)
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "Answer"

        result = agent.answer_question(
            question="Test question",
            search_web=False
        )

        assert result["answer"] == "Answer"
