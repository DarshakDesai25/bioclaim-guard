"""
BioClaim Guard – Claim Verification Service
Core pipeline: PICO extraction → PubMed retrieval → Claude verification
"""

import anthropic
import json
import logging
from typing import Optional

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, VERDICT_COLORS
from services.pico_extractor import extract_pico
from services.pubmed_service import search_pubmed, build_pico_query
from prompts.templates import VERIFICATION_PROMPT, FALLBACK_CLASSIFICATION

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


class ClaimVerifier:
    """
    Orchestrates the full BioClaim Guard verification pipeline:
    
    1. Extract PICO framework from the claim (Claude)
    2. Build optimized PubMed search query
    3. Retrieve top-k peer-reviewed papers (PubMed API)
    4. Verify claim against evidence (Claude)
    5. Return structured classification with citations
    """

    def verify(self, claim: str) -> dict:
        """
        Full verification pipeline for a single medical claim.
        
        Args:
            claim: Raw medical claim text
        
        Returns:
            Structured dict with classification, explanation, evidence, PICO, etc.
        """
        logger.info(f"Starting verification for: {claim[:100]}")

        # ── Step 1: Extract PICO ─────────────────────────────────────────────
        pico = extract_pico(claim)
        logger.info(f"PICO: {pico}")

        # ── Step 2: Build PubMed search query ───────────────────────────────
        query = build_pico_query(pico, claim)
        logger.info(f"PubMed query: {query}")

        # ── Step 3: Retrieve evidence ────────────────────────────────────────
        papers = search_pubmed(query, max_results=5)
        logger.info(f"Retrieved {len(papers)} papers")

        # ── Step 4: Handle no-evidence case ──────────────────────────────────
        if not papers:
            result = dict(FALLBACK_CLASSIFICATION)
            result["claim"] = claim
            result["pico"] = pico
            result["evidence"] = []
            result["query_used"] = query
            return result

        # ── Step 5: Verify with Claude ────────────────────────────────────────
        evidence_text = self._format_evidence(papers)
        pico_text = json.dumps(pico, indent=2)

        try:
            message = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1500,
                system=(
                    "You are a senior clinical evidence analyst. "
                    "Always respond with valid JSON only. No preamble or explanation outside the JSON."
                ),
                messages=[
                    {
                        "role": "user",
                        "content": VERIFICATION_PROMPT.format(
                            claim=claim,
                            pico=pico_text,
                            evidence=evidence_text
                        )
                    }
                ]
            )

            result_text = message.content[0].text.strip()
            result = self._parse_verification_response(result_text)

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error during verification: {e}")
            result = dict(FALLBACK_CLASSIFICATION)

        # ── Step 6: Enrich result ─────────────────────────────────────────────
        result["claim"] = claim
        result["pico"] = pico
        result["evidence"] = papers[:3]   # Return top 3 papers
        result["query_used"] = query
        result["total_papers_retrieved"] = len(papers)
        
        # Set verdict color
        classification = result.get("classification", "Insufficient Evidence")
        result["verdict_color"] = VERDICT_COLORS.get(classification, "gray")

        logger.info(f"Verification complete: {classification}")
        return result

    # ─────────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _format_evidence(self, papers: list) -> str:
        """Format retrieved papers into a structured evidence block for the prompt."""
        sections = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper.get("authors", []))
            section = (
                f"[Study {i}]\n"
                f"PMID: {paper.get('pmid', 'N/A')}\n"
                f"Title: {paper.get('title', 'N/A')}\n"
                f"Authors: {authors_str or 'N/A'}\n"
                f"Year: {paper.get('year', 'N/A')}\n"
                f"Journal: {paper.get('journal', 'N/A')}\n"
                f"Study Type: {paper.get('study_type', 'N/A')}\n"
                f"Abstract: {paper.get('abstract', 'N/A')[:800]}\n"
                f"URL: {paper.get('url', 'N/A')}"
            )
            sections.append(section)
        return "\n\n" + "\n\n".join(sections) + "\n"

    def _parse_verification_response(self, text: str) -> dict:
        """
        Parse Claude's JSON verification response.
        Handles markdown code blocks and partial JSON gracefully.
        """
        # Strip markdown wrappers
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            logger.warning("No JSON found in verification response.")
            return dict(FALLBACK_CLASSIFICATION)

        json_str = text[start:end]

        try:
            data = json.loads(json_str)
            # Ensure all expected fields exist
            defaults = {
                "classification": "Insufficient Evidence",
                "confidence": "Low",
                "explanation": "Unable to parse verification result.",
                "key_issues": [],
                "evidence_quality": "None found",
                "population_match": False,
                "effect_exaggerated": False,
                "recommendation": "Consult a qualified healthcare professional.",
                "cited_studies": []
            }
            for key, default in defaults.items():
                if key not in data:
                    data[key] = default
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in verification response: {e}")
            return dict(FALLBACK_CLASSIFICATION)
