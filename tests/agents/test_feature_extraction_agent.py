"""
Unit tests for Feature Extraction Agent

Uses mocks to avoid LLM API calls and costs
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agents.feature_extraction.agent import FeatureExtractionAgent


class TestFeatureExtractionAgent:
    """Test suite for Feature Extraction Agent"""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return FeatureExtractionAgent(verbose=False)

    @pytest.fixture
    def mock_llm_interface(self):
        """Mock LLM interface to avoid API calls"""
        with patch('src.agents.feature_extraction.agent.LLMInterface') as mock:
            instance = mock.return_value
            # Mock chat_completion to return predictable responses
            instance.chat_completion.return_value = "Mocked LLM response"
            instance.create_system_message.return_value = {"role": "system", "content": "system"}
            instance.create_user_message.return_value = {"role": "user", "content": "user"}
            yield instance

    @pytest.fixture
    def mock_mcp_client(self):
        """Mock MCP client to avoid search API calls"""
        with patch('src.agents.feature_extraction.agent.SearchMCPClientSync') as mock:
            instance = mock.return_value.__enter__.return_value
            # Mock search to return predictable results
            instance.search.return_value = "Found 5 search results:\n\n[1] Test Result\n    URL: https://example.com\n    Test snippet\n\n"
            yield instance

    def test_agent_initialization(self, agent):
        """Test that agent initializes correctly"""
        assert agent is not None
        assert agent.verbose is False
        assert agent.llm is not None

    def test_classify_question_type_tool_usage(self, agent):
        """Test classification of tool usage questions"""
        questions = [
            "How do I use TransformerLens?",
            "How to use SAELens for feature extraction?",
            "Show me code example for TransformerLens"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "tool_usage", f"Failed for: {q}"

    def test_classify_question_type_concept(self, agent):
        """Test classification of concept explanation questions"""
        questions = [
            "What is monosemanticity?",
            "Explain sparse autoencoders",
            "Define superposition in neural networks"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "concept_explanation", f"Failed for: {q}"

    def test_classify_question_type_general(self, agent):
        """Test classification of general questions"""
        questions = [
            "Tell me about recent research",
            "Compare different approaches",
            "What are the benefits?"
        ]
        for q in questions:
            result = agent._classify_question_type(q)
            assert result == "general", f"Failed for: {q}"

    def test_generate_search_queries(self, agent, mock_llm_interface):
        """Test search query generation"""
        agent.llm = mock_llm_interface

        # Mock LLM to return multiple queries
        mock_llm_interface.chat_completion.return_value = "query one\nquery two\nquery three"

        queries = agent._generate_search_queries("What is monosemanticity?")

        assert len(queries) == 3
        assert queries[0] == "query one"
        assert queries[1] == "query two"
        assert queries[2] == "query three"

        # Verify LLM was called
        assert mock_llm_interface.chat_completion.called

    def test_generate_search_queries_filters_empty_lines(self, agent, mock_llm_interface):
        """Test that empty lines are filtered from search queries"""
        agent.llm = mock_llm_interface

        # Mock LLM to return queries with empty lines
        mock_llm_interface.chat_completion.return_value = "query one\n\nquery two\n\n\nquery three"

        queries = agent._generate_search_queries("test question")

        assert len(queries) == 3
        assert "" not in queries

    @patch('src.agents.feature_extraction.agent.SearchMCPClientSync')
    def test_answer_question_no_search(self, mock_mcp, agent, mock_llm_interface):
        """Test answering without web search"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "This is the answer"

        result = agent.answer_question(
            question="What is monosemanticity?",
            search_web=False
        )

        assert result["answer"] == "This is the answer"
        assert result["search_queries"] == []
        assert result["question_type"] == "concept_explanation"

        # MCP client should not be used
        mock_mcp.assert_not_called()

    @patch('src.agents.feature_extraction.agent.SearchMCPClientSync')
    def test_answer_question_with_search(self, mock_mcp, agent, mock_llm_interface):
        """Test answering with web search"""
        agent.llm = mock_llm_interface

        # Mock search queries generation
        mock_llm_interface.chat_completion.side_effect = [
            "query one\nquery two",  # First call: generate queries
            "This is the answer with sources"  # Second call: generate answer
        ]

        # Mock MCP client
        mock_client_instance = MagicMock()
        mock_client_instance.search.return_value = "Search result text"
        mock_mcp.return_value.__enter__.return_value = mock_client_instance

        result = agent.answer_question(
            question="What is monosemanticity?",
            search_web=True
        )

        assert result["answer"] == "This is the answer with sources"
        assert len(result["search_queries"]) == 2
        assert result["question_type"] == "concept_explanation"

        # Verify MCP client was used
        mock_mcp.assert_called_once()
        assert mock_client_instance.search.call_count == 2

    def test_answer_question_tool_usage_prompt(self, agent, mock_llm_interface):
        """Test that tool usage questions use the correct prompt"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "Mock response"

        result = agent.answer_question(
            question="How do I use TransformerLens?",
            search_web=False
        )

        assert result["question_type"] == "tool_usage"

        # Verify the correct prompt was used (check call arguments)
        call_args = mock_llm_interface.chat_completion.call_args
        messages = call_args[0][0]

        # Should have system and user messages
        assert len(messages) == 2

    def test_answer_question_concept_prompt(self, agent, mock_llm_interface):
        """Test that concept questions use the correct prompt"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "Mock response"

        result = agent.answer_question(
            question="What is superposition?",
            search_web=False
        )

        assert result["question_type"] == "concept_explanation"

    def test_on_search_callback(self, agent, mock_llm_interface):
        """Test that on_search callback is called for each query"""
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.side_effect = [
            "query one\nquery two",
            "Answer"
        ]

        callback_calls = []
        def callback(query):
            callback_calls.append(query)

        with patch('src.agents.feature_extraction.agent.SearchMCPClientSync') as mock_mcp:
            mock_client = MagicMock()
            mock_client.search.return_value = "Results"
            mock_mcp.return_value.__enter__.return_value = mock_client

            agent.answer_question(
                question="Test question",
                search_web=True,
                on_search=callback
            )

        # Callback should be called for each query
        assert len(callback_calls) == 2
        assert callback_calls[0] == "query one"
        assert callback_calls[1] == "query two"

    def test_verbose_mode_no_errors(self, mock_llm_interface):
        """Test that verbose mode doesn't cause errors"""
        agent = FeatureExtractionAgent(verbose=True)
        agent.llm = mock_llm_interface

        mock_llm_interface.chat_completion.return_value = "Answer"

        # Should not raise any errors
        result = agent.answer_question(
            question="Test question",
            search_web=False
        )

        assert result["answer"] == "Answer"


class TestFeatureExtractionAgentIntegration:
    """Integration tests that test multiple components together"""

    @pytest.fixture
    def agent(self):
        return FeatureExtractionAgent(verbose=False)

    @patch('src.agents.feature_extraction.agent.SearchMCPClientSync')
    @patch('src.agents.feature_extraction.agent.LLMInterface')
    def test_full_workflow(self, mock_llm_class, mock_mcp_class, agent):
        """Test complete workflow from question to answer"""
        # Setup mocks
        mock_llm = mock_llm_class.return_value
        mock_llm.chat_completion.side_effect = [
            "search query 1\nsearch query 2",
            "Final answer based on search results"
        ]
        mock_llm.create_system_message.return_value = {"role": "system", "content": "system"}
        mock_llm.create_user_message.return_value = {"role": "user", "content": "user"}

        mock_client = MagicMock()
        mock_client.search.return_value = "Search results"
        mock_mcp_class.return_value.__enter__.return_value = mock_client

        # Recreate agent with mocks
        agent = FeatureExtractionAgent(verbose=False)

        # Execute
        result = agent.answer_question(
            question="Explain monosemanticity in neural networks",
            search_web=True
        )

        # Verify
        assert result["answer"] == "Final answer based on search results"
        assert len(result["search_queries"]) == 2
        assert result["question_type"] == "concept_explanation"
        assert result["sources"] == []  # MCP returns text, not structured sources
