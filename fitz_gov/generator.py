# fitz_gov/generator.py
"""
Synthetic test case generator for fitz-gov benchmark.

Generates governance test cases from an existing corpus using LLM.
This enables creating custom benchmark suites for specific domains.

Usage:
    from fitz_gov.generator import FitzGovGenerator

    generator = FitzGovGenerator(llm_client=your_client)
    cases = generator.generate_all(your_chunks, cases_per_category=50)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

from .schema import AnswerMode, FitzGovCase, FitzGovCategory


class LLMClient(Protocol):
    """Protocol for LLM client compatibility."""

    def complete(self, prompt: str) -> str:
        """Generate completion for prompt."""
        ...


@dataclass
class ChunkLike:
    """Minimal chunk interface for generator."""

    text: str
    source: str = ""
    metadata: dict[str, Any] | None = None


class FitzGovGenerator:
    """
    Generate fitz-gov test cases from an existing corpus.

    Uses LLM to identify scenarios that should trigger different
    governance modes, creating a custom test suite for your data.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize generator.

        Args:
            llm_client: LLM client with a complete(prompt) method.
                       Works with OpenAI, Anthropic, or any compatible client.
        """
        self._llm = llm_client

    def generate_all(
        self,
        chunks: list[Any],
        cases_per_category: int = 20,
        output_dir: str | None = None,
    ) -> list[FitzGovCase]:
        """
        Generate test cases for all categories.

        Args:
            chunks: Corpus chunks to generate cases from.
            cases_per_category: Number of cases per category.
            output_dir: If provided, saves each category incrementally.

        Returns:
            List of generated FitzGovCase objects.
        """
        all_cases: list[FitzGovCase] = []

        categories = [
            ("abstention", self.generate_abstention_cases),
            ("dispute", self.generate_dispute_cases),
            ("qualification", self.generate_qualification_cases),
            ("confidence", self.generate_confidence_cases),
            ("grounding", self.generate_grounding_cases),
            ("relevance", self.generate_relevance_cases),
        ]

        for i, (name, gen_func) in enumerate(categories, 1):
            print(f"[{i}/6] Generating {name} cases...", flush=True)
            cases = gen_func(chunks, cases_per_category)
            all_cases.extend(cases)
            print(f"       Generated {len(cases)} {name} cases", flush=True)

            # Save incrementally if output_dir provided
            if output_dir:
                self._save_category(cases, name, output_dir)

        return all_cases

    def generate_category(
        self,
        category: str,
        chunks: list[Any],
        num_cases: int,
        output_dir: str,
    ) -> list[FitzGovCase]:
        """Generate just one category (for retries)."""
        gen_funcs = {
            "abstention": self.generate_abstention_cases,
            "dispute": self.generate_dispute_cases,
            "qualification": self.generate_qualification_cases,
            "confidence": self.generate_confidence_cases,
            "grounding": self.generate_grounding_cases,
            "relevance": self.generate_relevance_cases,
        }

        gen_func = gen_funcs.get(category)
        if not gen_func:
            raise ValueError(f"Unknown category: {category}")

        print(f"Generating {category} cases...", flush=True)
        cases = gen_func(chunks, num_cases)
        print(f"Generated {len(cases)} cases", flush=True)

        if cases:
            self._save_category(cases, category, output_dir)

        return cases

    def _save_category(self, cases: list[FitzGovCase], category: str, output_dir: str) -> None:
        """Save a single category to disk."""
        import json
        from pathlib import Path

        output_path = Path(output_dir)
        cat_dir = output_path / "cases" / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Group by subcategory
        by_subcat: dict[str, list[FitzGovCase]] = {}
        for case in cases:
            subcat = case.subcategory
            if subcat not in by_subcat:
                by_subcat[subcat] = []
            by_subcat[subcat].append(case)

        for subcat, subcat_cases in by_subcat.items():
            output_file = cat_dir / f"{subcat}.json"
            data = {
                "category": category,
                "subcategory": subcat,
                "description": f"fitz-gov {category} cases - {subcat}",
                "cases": [c.to_dict() for c in subcat_cases],
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"       Saved to {cat_dir}/", flush=True)

    def generate_abstention_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate abstention test cases.

        Creates questions that the corpus cannot answer, paired with
        chunks that are tangentially related but insufficient.
        """
        cases: list[FitzGovCase] = []
        chunk_texts = self._extract_texts(chunks[:10])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

Given these document excerpts, generate {num_cases} questions that:
1. Are related to the general topic/domain
2. CANNOT be answered from the provided information
3. Would require external knowledge or data not present

The goal is to test if a RAG system correctly ABSTAINS when it lacks sufficient context.

Document excerpts:
{self._format_chunks(chunk_texts)}

Return as JSON:
{{
  "cases": [
    {{
      "query": "What was the company's Q4 2024 revenue?",
      "description": "Financial data not present in context",
      "rationale": "Context discusses company history but contains no financial figures"
    }}
  ]
}}

Generate {num_cases} diverse cases covering different types of missing information."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        for i, case_data in enumerate(generated[:num_cases]):
            # Pair with chunks that are related but won't answer the question
            contexts = chunk_texts[:3]
            cases.append(
                FitzGovCase(
                    id=f"gen_abstain_{i:03d}",
                    category=FitzGovCategory.ABSTENTION,
                    subcategory="out_of_scope",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.ABSTAIN,
                    description=case_data.get("description", "Generated abstention case"),
                    rationale=case_data.get("rationale", "Information not in context"),
                )
            )

        return cases

    def generate_dispute_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate dispute test cases.

        Creates questions where context contains conflicting information,
        testing if the system correctly flags the dispute.
        """
        cases: list[FitzGovCase] = []
        chunk_texts = self._extract_texts(chunks[:15])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

Analyze these document excerpts and generate {num_cases} scenarios where you:
1. Create a question that could have multiple answers
2. Provide 2-3 context passages with CONTRADICTING information
3. The system should flag the DISPUTE rather than picking one answer

Document excerpts (for topic inspiration):
{self._format_chunks(chunk_texts[:5])}

Return as JSON:
{{
  "cases": [
    {{
      "query": "What is the recommended dosage?",
      "contexts": [
        "The recommended dosage is 10mg twice daily.",
        "Studies show 5mg once daily is optimal.",
        "Clinical guidelines suggest 15mg as needed."
      ],
      "description": "Conflicting dosage recommendations",
      "rationale": "Three sources provide different dosage recommendations"
    }}
  ]
}}

Generate {num_cases} diverse conflict scenarios."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        for i, case_data in enumerate(generated[:num_cases]):
            contexts = case_data.get("contexts", chunk_texts[:2])
            cases.append(
                FitzGovCase(
                    id=f"gen_dispute_{i:03d}",
                    category=FitzGovCategory.DISPUTE,
                    subcategory="contradicting_facts",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.DISPUTED,
                    description=case_data.get("description", "Generated dispute case"),
                    rationale=case_data.get("rationale", "Sources provide conflicting information"),
                )
            )

        return cases

    def generate_qualification_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate qualification test cases.

        Creates questions where the answer requires hedging, such as:
        - Causal claims without evidence
        - Predictions without certainty
        - Generalizations from limited data
        """
        cases: list[FitzGovCase] = []
        chunk_texts = self._extract_texts(chunks[:10])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

Generate {num_cases} questions that should receive QUALIFIED/HEDGED answers:
1. "Why" questions that imply causation but context only shows correlation
2. Prediction questions where data is limited
3. Generalization questions where context has few examples

The context should provide SOME relevant information, but not enough
for a confident answer. The system should QUALIFY its response.

Document excerpts (for topic inspiration):
{self._format_chunks(chunk_texts[:5])}

Return as JSON:
{{
  "cases": [
    {{
      "query": "Why do users prefer feature X over feature Y?",
      "contexts": [
        "Survey shows 60% of users selected feature X.",
        "Feature X was released 6 months before feature Y."
      ],
      "description": "Causal question with only correlational data",
      "rationale": "Context shows preference data but no causal evidence for WHY"
    }}
  ]
}}

Generate {num_cases} diverse qualification scenarios."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        for i, case_data in enumerate(generated[:num_cases]):
            contexts = case_data.get("contexts", chunk_texts[:2])
            cases.append(
                FitzGovCase(
                    id=f"gen_qualify_{i:03d}",
                    category=FitzGovCategory.QUALIFICATION,
                    subcategory="uncertain_evidence",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.QUALIFIED,
                    description=case_data.get("description", "Generated qualification case"),
                    rationale=case_data.get(
                        "rationale", "Evidence is insufficient for confident answer"
                    ),
                )
            )

        return cases

    def generate_confidence_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate confidence test cases.

        Creates questions where context clearly supports a confident answer,
        testing that the system doesn't over-hedge.
        """
        cases: list[FitzGovCase] = []
        chunks_with_ids = self._extract_chunks_with_ids(chunks[:15])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

For each document excerpt below, generate a question where the answer is CLEARLY supported:
1. Factual questions with explicit answers in the text
2. Definition questions where the term is clearly defined
3. Procedural questions where steps are clearly listed

The system should answer CONFIDENTLY without unnecessary hedging.

Document excerpts (with IDs):
{self._format_chunks_with_ids(chunks_with_ids)}

Return as JSON:
{{
  "cases": [
    {{
      "query": "What are the three main components of the system?",
      "doc_ids": ["doc_123", "doc_456"],
      "description": "Direct factual question with explicit answer",
      "rationale": "Context explicitly lists the three components"
    }}
  ]
}}

Generate {num_cases} clear-cut confidence scenarios. Include the doc_ids that contain the answer."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        # Build ID to text mapping
        id_to_text = {c["id"]: c["text"] for c in chunks_with_ids}

        for i, case_data in enumerate(generated[:num_cases]):
            doc_ids = case_data.get("doc_ids", [])
            # Get contexts from referenced doc IDs
            contexts = [id_to_text[did] for did in doc_ids if did in id_to_text]
            # Fallback if no valid doc IDs
            if not contexts:
                contexts = [chunks_with_ids[i % len(chunks_with_ids)]["text"]]
                doc_ids = [chunks_with_ids[i % len(chunks_with_ids)]["id"]]

            cases.append(
                FitzGovCase(
                    id=f"gen_confident_{i:03d}",
                    category=FitzGovCategory.CONFIDENCE,
                    subcategory="clear_evidence",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.CONFIDENT,
                    description=case_data.get("description", "Generated confidence case"),
                    rationale=case_data.get("rationale", "Context clearly supports the answer"),
                    relevant_doc_ids=doc_ids,
                )
            )

        return cases

    def generate_grounding_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate grounding test cases (hallucination traps).

        Creates questions where context is partially relevant, making it
        tempting to hallucinate details not actually present.
        """
        cases: list[FitzGovCase] = []
        chunks_with_ids = self._extract_chunks_with_ids(chunks[:10])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

Generate {num_cases} "hallucination trap" scenarios:
1. Question asks for specific detail (number, date, name)
2. Context discusses the topic but LACKS that specific detail
3. A hallucinating system might make up a plausible-sounding answer

Include "forbidden_claims" - specific fabrications that would indicate hallucination.

Document excerpts (with IDs):
{self._format_chunks_with_ids(chunks_with_ids[:5])}

Return as JSON:
{{
  "cases": [
    {{
      "query": "When was the company founded?",
      "doc_ids": ["doc_123"],
      "forbidden_claims": ["1998", "1999", "2000", "2001", "2005", "2010"],
      "description": "Founding date not mentioned but context discusses company",
      "rationale": "Context describes company but never mentions founding date"
    }}
  ]
}}

Generate {num_cases} diverse hallucination trap scenarios. Include doc_ids of the relevant (but incomplete) documents."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        # Build ID to text mapping
        id_to_text = {c["id"]: c["text"] for c in chunks_with_ids}

        for i, case_data in enumerate(generated[:num_cases]):
            doc_ids = case_data.get("doc_ids", [])
            contexts = [id_to_text[did] for did in doc_ids if did in id_to_text]
            if not contexts:
                contexts = [chunks_with_ids[i % len(chunks_with_ids)]["text"]]
                doc_ids = [chunks_with_ids[i % len(chunks_with_ids)]["id"]]

            cases.append(
                FitzGovCase(
                    id=f"gen_ground_{i:03d}",
                    category=FitzGovCategory.GROUNDING,
                    subcategory="hallucination_trap",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.CONFIDENT,  # Should answer but stay grounded
                    description=case_data.get("description", "Generated grounding case"),
                    rationale=case_data.get("rationale", "Tests if system hallucinates details"),
                    forbidden_claims=case_data.get("forbidden_claims", []),
                    relevant_doc_ids=doc_ids,
                )
            )

        return cases

    def generate_relevance_cases(
        self,
        chunks: list[Any],
        num_cases: int = 20,
    ) -> list[FitzGovCase]:
        """
        Generate relevance test cases (off-topic traps).

        Creates questions where the answer must address specific aspects,
        testing if the system stays on-topic.
        """
        cases: list[FitzGovCase] = []
        chunks_with_ids = self._extract_chunks_with_ids(chunks[:10])

        prompt = f"""You are generating test cases for a RAG governance benchmark.

Generate {num_cases} "relevance trap" scenarios:
1. Question asks about specific aspect A
2. Context contains information about both A and related aspects B, C
3. A poor system might discuss B or C instead of directly answering about A

Include "required_elements" - things that MUST appear in a relevant answer.

Document excerpts (with IDs):
{self._format_chunks_with_ids(chunks_with_ids[:5])}

Return as JSON:
{{
  "cases": [
    {{
      "query": "What are the SECURITY features of the product?",
      "doc_ids": ["doc_123"],
      "required_elements": ["encryption", "authentication", "audit"],
      "description": "Asks specifically about security, not general features",
      "rationale": "Answer should focus on security features, not UI or performance"
    }}
  ]
}}

Generate {num_cases} diverse relevance trap scenarios. Include doc_ids of relevant documents."""

        response = self._llm.complete(prompt)
        generated = self._parse_json_response(response).get("cases", [])

        # Build ID to text mapping
        id_to_text = {c["id"]: c["text"] for c in chunks_with_ids}

        for i, case_data in enumerate(generated[:num_cases]):
            doc_ids = case_data.get("doc_ids", [])
            contexts = [id_to_text[did] for did in doc_ids if did in id_to_text]
            if not contexts:
                contexts = [chunks_with_ids[i % len(chunks_with_ids)]["text"]]
                doc_ids = [chunks_with_ids[i % len(chunks_with_ids)]["id"]]

            cases.append(
                FitzGovCase(
                    id=f"gen_relevance_{i:03d}",
                    category=FitzGovCategory.RELEVANCE,
                    subcategory="off_topic_trap",
                    query=case_data["query"],
                    contexts=contexts,
                    expected_mode=AnswerMode.CONFIDENT,  # Should answer the actual question
                    description=case_data.get("description", "Generated relevance case"),
                    rationale=case_data.get("rationale", "Tests if system stays on topic"),
                    required_elements=case_data.get("required_elements", []),
                    relevant_doc_ids=doc_ids,
                )
            )

        return cases

    def _extract_texts(self, chunks: list[Any]) -> list[str]:
        """Extract text from chunk-like objects."""
        texts = []
        for chunk in chunks:
            if hasattr(chunk, "text"):
                texts.append(chunk.text)
            elif isinstance(chunk, dict) and "text" in chunk:
                texts.append(chunk["text"])
            elif isinstance(chunk, str):
                texts.append(chunk)
            else:
                texts.append(str(chunk))
        return texts

    def _extract_chunks_with_ids(self, chunks: list[Any]) -> list[dict[str, str]]:
        """Extract text and IDs from chunk-like objects."""
        result = []
        for i, chunk in enumerate(chunks):
            if isinstance(chunk, dict):
                text = chunk.get("text", str(chunk))
                doc_id = chunk.get("id", f"doc_{i}")
            elif hasattr(chunk, "text"):
                text = chunk.text
                doc_id = getattr(chunk, "id", f"doc_{i}")
            elif isinstance(chunk, str):
                text = chunk
                doc_id = f"doc_{i}"
            else:
                text = str(chunk)
                doc_id = f"doc_{i}"
            result.append({"text": text, "id": doc_id})
        return result

    def _format_chunks(self, texts: list[str], max_chars: int = 500) -> str:
        """Format chunk texts for prompt."""
        lines = []
        for i, text in enumerate(texts):
            truncated = text[:max_chars] + "..." if len(text) > max_chars else text
            lines.append(f"[{i}] {truncated}")
        return "\n\n".join(lines)

    def _format_chunks_with_ids(self, chunks: list[dict[str, str]], max_chars: int = 500) -> str:
        """Format chunks with their IDs for prompt."""
        lines = []
        for chunk in chunks:
            text = chunk["text"]
            doc_id = chunk["id"]
            truncated = text[:max_chars] + "..." if len(text) > max_chars else text
            lines.append(f"[{doc_id}] {truncated}")
        return "\n\n".join(lines)

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from LLM response."""
        try:
            # Try to extract JSON from response
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass
        return {}


def save_cases(cases: list[FitzGovCase], output_dir: str | None = None) -> None:
    """
    Save generated cases to JSON files organized by category.

    Args:
        cases: List of FitzGovCase objects.
        output_dir: Directory to save to. Defaults to ./generated_data/
    """
    from pathlib import Path

    output_path = Path(output_dir) if output_dir else Path("./generated_data")

    # Group by category
    by_category: dict[FitzGovCategory, list[FitzGovCase]] = {}
    for case in cases:
        if case.category not in by_category:
            by_category[case.category] = []
        by_category[case.category].append(case)

    # Save each category
    for category, cat_cases in by_category.items():
        cat_dir = output_path / category.value
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Group by subcategory
        by_subcat: dict[str, list[FitzGovCase]] = {}
        for case in cat_cases:
            if case.subcategory not in by_subcat:
                by_subcat[case.subcategory] = []
            by_subcat[case.subcategory].append(case)

        # Save each subcategory file
        for subcat, subcat_cases in by_subcat.items():
            output_file = cat_dir / f"{subcat}.json"
            data = {
                "description": f"Generated {category.value} cases - {subcat}",
                "cases": [case.to_dict() for case in subcat_cases],
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    print(f"Saved {len(cases)} cases to {output_path}")
