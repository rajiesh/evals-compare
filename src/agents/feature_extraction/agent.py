"""
Feature Extraction & Interpretability Specialist Agent (AutoGen 0.10+)

Expert in:
- Monosemanticity and polysemanticity
- Sparse Autoencoders (SAEs) and dictionary learning
- Feature visualization and attribution
- TransformerLens and SAELens usage
"""

import asyncio
from typing import Dict, Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.tools.mcp_client import SearchMCPClientSync
from src.config.settings import settings
from src.agents.feature_extraction.prompts import SYSTEM_PROMPT


# Define web search tool for AutoGen
def web_search_tool(query: str) -> str:
    """
    Search the web for mechanistic interpretability research.

    Args:
        query: The search query string

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    try:
        with SearchMCPClientSync(verbose=False) as client:
            results = client.search(query, num_results=5)
            return results
    except Exception as e:
        return f"Search error: {str(e)}"


class FeatureExtractionAgent:
    """Feature Extraction & Interpretability Specialist using AutoGen 0.10+"""

    def __init__(self, verbose: bool = False):
        """
        Initialize the Feature Extraction agent

        Args:
            verbose: Enable verbose logging of agent activities
        """
        self.verbose = verbose

        # Create OpenAI client for AutoGen
        self.model_client = OpenAIChatCompletionClient(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

        # Create AutoGen Assistant Agent with tools
        self.agent = AssistantAgent(
            name="FeatureExtractionSpecialist",
            model_client=self.model_client,
            tools=[web_search_tool],
            system_message=SYSTEM_PROMPT,
        )

    def answer_question(
        self,
        question: str,
        on_search: Optional[callable] = None,
        search_web: bool = True
    ) -> Dict:
        """
        Answer a question about feature extraction and interpretability

        Args:
            question: User's question
            on_search: Optional callback called when searches are performed
            search_web: Whether to enable web search (for compatibility)

        Returns:
            Dictionary with answer and metadata
        """
        # Run async AutoGen chat
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                self._run_chat(question, on_search)
            )
            return result
        finally:
            # Properly clean up pending tasks before closing loop
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()

                # Wait for all tasks to finish (with cancellation)
                if pending:
                    loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception:
                pass  # Ignore cleanup errors
            finally:
                loop.close()

    async def _run_chat(
        self,
        question: str,
        on_search: Optional[callable] = None
    ) -> Dict:
        """
        Run the AutoGen chat asynchronously

        Args:
            question: User's question
            on_search: Optional callback for search events

        Returns:
            Dictionary with answer and metadata
        """
        # Send message to agent
        message = TextMessage(content=question, source="User")
        response = await self.agent.on_messages([message], cancellation_token=None)

        # Extract answer from response
        if hasattr(response, 'chat_message'):
            answer = str(response.chat_message.content) if hasattr(response.chat_message, 'content') else str(response.chat_message)
        else:
            answer = str(response)

        return {
            "answer": answer,
            "agent": "Feature Extraction & Interpretability Specialist",
            "question_type": "autogen_handled",
            "search_queries": [],  # AutoGen handles this internally
            "search_results_text": "",
            "used_search": True,  # Assume search might have been used
            "sources": []
        }
