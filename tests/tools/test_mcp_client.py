"""
Unit tests for MCP Client

Tests the synchronous MCP client wrapper used by agents
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.tools.mcp_client import SearchMCPClientSync


class TestSearchMCPClientSync:
    """Test suite for synchronous SearchMCPClient wrapper"""

    def test_initialization(self):
        """Test sync client initializes"""
        client = SearchMCPClientSync(verbose=False)
        assert client.verbose is False
        assert client._async_client is None
        assert client._loop is None

    def test_initialization_verbose(self):
        """Test sync client verbose mode"""
        client = SearchMCPClientSync(verbose=True)
        assert client.verbose is True

    def test_search_not_initialized(self):
        """Test search raises error when not in context manager"""
        client = SearchMCPClientSync(verbose=False)

        with pytest.raises(RuntimeError, match="Client not initialized"):
            client.search("test query")

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_context_manager_lifecycle(self, mock_asyncio, mock_async_client_class):
        """Test context manager creates and tears down client"""
        # Mock event loop
        mock_loop = MagicMock()
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_asyncio.set_event_loop = MagicMock()

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        # Enter and exit context
        with SearchMCPClientSync(verbose=False) as client:
            # Inside context, async client should be created
            assert client._async_client is not None
            assert client._loop is not None

        # After exit, loop should be closed
        mock_loop.run_until_complete.assert_called()
        mock_loop.close.assert_called_once()

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_search_calls_async_method(self, mock_asyncio, mock_async_client_class):
        """Test that sync search calls async search with correct parameters"""
        # Mock event loop
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = "Search results"
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client.search = MagicMock(return_value="Search results")
        mock_async_client_class.return_value = mock_async_client

        with SearchMCPClientSync(verbose=False) as client:
            result = client.search("test query", num_results=3)

        # Verify async search was called
        assert mock_loop.run_until_complete.called
        assert result == "Search results"

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_search_default_num_results(self, mock_asyncio, mock_async_client_class):
        """Test search with default num_results parameter"""
        # Mock event loop
        mock_loop = MagicMock()
        mock_loop.run_until_complete.return_value = "Results"
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        with SearchMCPClientSync(verbose=False) as client:
            client.search("query")  # No num_results specified

        # Should have been called with async client.search
        mock_loop.run_until_complete.assert_called()

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_multiple_searches(self, mock_asyncio, mock_async_client_class):
        """Test multiple searches in same context"""
        # Mock event loop
        mock_loop = MagicMock()
        # side_effect order: connect, search1, search2, search3, disconnect
        mock_loop.run_until_complete.side_effect = [None, "Result 1", "Result 2", "Result 3", None]
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        with SearchMCPClientSync(verbose=False) as client:
            result1 = client.search("query 1")
            result2 = client.search("query 2")
            result3 = client.search("query 3")

        assert result1 == "Result 1"
        assert result2 == "Result 2"
        assert result3 == "Result 3"

        # Should have called run_until_complete 5 times (connect + 3 searches + disconnect)
        assert mock_loop.run_until_complete.call_count == 5

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_exception_handling(self, mock_asyncio, mock_async_client_class):
        """Test that exceptions are properly raised"""
        # Mock event loop that raises an exception
        mock_loop = MagicMock()
        mock_loop.run_until_complete.side_effect = [None, RuntimeError("Search failed"), None]
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        with pytest.raises(RuntimeError, match="Search failed"):
            with SearchMCPClientSync(verbose=False) as client:
                client.search("query")

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_verbose_flag_passed_to_async_client(self, mock_asyncio, mock_async_client_class):
        """Test that verbose flag is passed to async client"""
        # Mock event loop
        mock_loop = MagicMock()
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        with SearchMCPClientSync(verbose=True) as client:
            pass

        # Verify SearchMCPClient was instantiated with verbose=True
        mock_async_client_class.assert_called_once_with(verbose=True)

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_cleanup_on_exception(self, mock_asyncio, mock_async_client_class):
        """Test that cleanup happens even when exception occurs"""
        # Mock event loop
        mock_loop = MagicMock()
        mock_asyncio.new_event_loop.return_value = mock_loop

        # Mock async client
        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        try:
            with SearchMCPClientSync(verbose=False) as client:
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Loop should still be closed
        mock_loop.close.assert_called_once()


class TestSearchMCPClientIntegration:
    """Integration tests with minimal mocking"""

    @patch('src.tools.mcp_client.SearchMCPClient')
    @patch('src.tools.mcp_client.asyncio')
    def test_realistic_usage_pattern(self, mock_asyncio, mock_async_client_class):
        """Test usage pattern similar to how agents use it"""
        # Setup mocks to return realistic data
        mock_loop = MagicMock()
        search_results = [
            "Found 5 search results:\n\n[1] Test Result\n    URL: https://example.com\n    Snippet",
            "Found 3 search results:\n\n[1] Another Result\n    URL: https://test.com\n    Info"
        ]
        mock_loop.run_until_complete.side_effect = [None, search_results[0], search_results[1], None]
        mock_asyncio.new_event_loop.return_value = mock_loop

        mock_async_client = MagicMock()
        mock_async_client_class.return_value = mock_async_client

        # Simulate agent usage
        queries = ["monosemanticity", "sparse autoencoders"]
        results = []

        with SearchMCPClientSync(verbose=False) as client:
            for query in queries:
                result = client.search(query, num_results=5)
                results.append(result)

        # Verify results
        assert len(results) == 2
        assert results[0] == search_results[0]
        assert results[1] == search_results[1]
