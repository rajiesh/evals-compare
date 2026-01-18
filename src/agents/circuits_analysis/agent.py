"""
Circuits & Mechanistic Analysis Specialist Agent

Expert in:
- Circuit discovery and analysis
- Attention head patterns and behavior
- Causal interventions and ablation studies
- Information flow in transformers
"""

from typing import List, Dict, Optional, Callable

from src.tools.mcp_client import SearchMCPClientSync
from src.tools.llm_interface import LLMInterface
from src.config.settings import settings
from src.agents.circuits_analysis.prompts import (
    SYSTEM_PROMPT,
    SEARCH_QUERY_PROMPT,
    ANSWER_WITH_SOURCES_PROMPT,
    CIRCUIT_ANALYSIS_PROMPT,
    TECHNIQUE_EXPLANATION_PROMPT,
    ATTENTION_HEAD_PROMPT
)


class CircuitsAnalysisAgent:
    """Circuits & Mechanistic Analysis Specialist"""

    def __init__(self, verbose: bool = False):
        """
        Initialize the Circuits Analysis agent

        Args:
            verbose: Enable verbose logging of agent activities
        """
        self.verbose = verbose
        self.llm = LLMInterface(verbose=verbose)

    def _generate_search_queries(self, question: str) -> List[str]:
        """
        Generate focused search queries for a user question

        Args:
            question: User's question

        Returns:
            List of search queries
        """
        prompt = SEARCH_QUERY_PROMPT.format(question=question)

        if self.verbose:
            print(f"\n[Circuits Analysis Agent] Generating search queries...")

        response = self.llm.chat_completion([
            self.llm.create_user_message(prompt)
        ])

        # Parse queries (one per line)
        queries = [q.strip() for q in response.strip().split('\n') if q.strip()]

        if self.verbose:
            for i, query in enumerate(queries, 1):
                print(f"  └─ Query {i}: {query}")

        return queries

    def _classify_question_type(self, question: str) -> str:
        """
        Classify the type of question to use appropriate prompt template

        Returns:
            One of: "circuit_analysis", "technique", "attention_head", "general"
        """
        question_lower = question.lower()

        # Check for technique/methodology questions FIRST (more specific)
        technique_keywords = ["activation patching", "causal tracing", "ablation", "intervention",
                             "path patching", "logit attribution", "how to analyze"]
        if any(keyword in question_lower for keyword in technique_keywords):
            return "technique"

        # Check for attention head questions
        attention_keywords = ["attention head", "attention pattern", "induction head",
                            "key-query", "qk circuit", "ov circuit"]
        if any(keyword in question_lower for keyword in attention_keywords):
            return "attention_head"

        # Check for circuit analysis questions (more general, check last)
        # Removed "how does" as it's too generic
        circuit_keywords = ["circuit", "mechanism", "implementation", "algorithm"]
        if any(keyword in question_lower for keyword in circuit_keywords):
            return "circuit_analysis"

        return "general"

    def answer_question(
        self,
        question: str,
        search_web: bool = True,
        on_search: Optional[Callable] = None
    ) -> Dict[str, any]:
        """
        Answer a user question about circuits and mechanistic analysis

        Args:
            question: User's question
            search_web: Whether to perform web search
            on_search: Optional callback for search events (for verbose CLI)

        Returns:
            Dictionary containing:
                - answer: The agent's response
                - sources: List of SearchResult objects used
                - search_queries: List of search queries executed
                - question_type: Classified question type
        """
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"[Circuits Analysis Agent] Processing question")
            print(f"{'='*60}")

        question_type = self._classify_question_type(question)
        if self.verbose:
            print(f"  └─ Question type: {question_type}")

        search_results_text = ""
        search_queries = []

        # Perform web search if enabled
        if search_web:
            queries = self._generate_search_queries(question)
            search_queries = queries

            # Use MCP client for searching
            with SearchMCPClientSync(verbose=self.verbose) as client:
                all_results = []
                for query in queries:
                    if on_search:
                        on_search(query)

                    results = client.search(query, num_results=5)
                    all_results.append(results)

                search_results_text = "\n\n".join(all_results)

            if self.verbose:
                print(f"\n[Circuits Analysis Agent] Completed {len(queries)} searches via MCP")

        # Select appropriate prompt based on question type
        if question_type == "circuit_analysis":
            prompt_template = CIRCUIT_ANALYSIS_PROMPT
            prompt = prompt_template.format(
                question=question,
                search_results=search_results_text
            )
        elif question_type == "technique":
            prompt_template = TECHNIQUE_EXPLANATION_PROMPT
            prompt = prompt_template.format(
                question=question,
                search_results=search_results_text
            )
        elif question_type == "attention_head":
            prompt_template = ATTENTION_HEAD_PROMPT
            prompt = prompt_template.format(
                question=question,
                search_results=search_results_text
            )
        else:
            prompt_template = ANSWER_WITH_SOURCES_PROMPT
            prompt = prompt_template.format(
                question=question,
                search_results=search_results_text
            )

        # Get answer from LLM
        if self.verbose:
            print(f"\n[Circuits Analysis Agent] Generating answer...")

        messages = [
            self.llm.create_system_message(SYSTEM_PROMPT),
            self.llm.create_user_message(prompt)
        ]

        answer = self.llm.chat_completion(messages)

        if self.verbose:
            print(f"\n[Circuits Analysis Agent] Answer generated")

        return {
            "answer": answer,
            "sources": [],  # MCP returns formatted text, not structured objects
            "search_queries": search_queries,
            "question_type": question_type,
            "search_results_text": search_results_text
        }
