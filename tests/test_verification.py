"""
Tests for PICO extractor and claim verifier.
Run: pytest tests/ -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
import json


# ─────────────────────────────────────────────────────────────────────────────
# PICO Extractor Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestPICOExtractor:

    @patch('services.pico_extractor.client')
    def test_extracts_valid_pico(self, mock_client):
        pico_json = json.dumps({
            "population": "Adults with hypertension",
            "intervention": "ACE inhibitors",
            "comparison": "Placebo",
            "outcome": "Reduced blood pressure",
            "claim_type": "treatment",
            "scope": "specific"
        })
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=pico_json)]
        mock_client.messages.create.return_value = mock_message

        from services.pico_extractor import extract_pico
        result = extract_pico("ACE inhibitors reduce blood pressure in hypertensive adults.")

        assert result["population"] == "Adults with hypertension"
        assert result["intervention"] == "ACE inhibitors"
        assert result["outcome"] == "Reduced blood pressure"
        assert result["claim_type"] == "treatment"

    @patch('services.pico_extractor.client')
    def test_handles_json_in_markdown_block(self, mock_client):
        pico_json = '```json\n{"population": "Adults", "intervention": "Exercise", "comparison": "Sedentary", "outcome": "Weight loss", "claim_type": "treatment", "scope": "general"}\n```'
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=pico_json)]
        mock_client.messages.create.return_value = mock_message

        from services.pico_extractor import extract_pico
        result = extract_pico("Exercise causes weight loss in adults.")

        assert result["population"] == "Adults"
        assert result["intervention"] == "Exercise"

    @patch('services.pico_extractor.client')
    def test_falls_back_on_api_error(self, mock_client):
        import anthropic
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="API Error", request=MagicMock(), body={}
        )

        from services.pico_extractor import extract_pico, FALLBACK_PICO
        result = extract_pico("Some claim about medicine.")

        assert result == FALLBACK_PICO

    @patch('services.pico_extractor.client')
    def test_falls_back_on_invalid_json(self, mock_client):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="This is not JSON at all.")]
        mock_client.messages.create.return_value = mock_message

        from services.pico_extractor import extract_pico, FALLBACK_PICO
        result = extract_pico("Some claim.")

        assert result == FALLBACK_PICO

    @patch('services.pico_extractor.client')
    def test_adds_missing_pico_fields(self, mock_client):
        # Partial JSON missing some required fields
        partial = json.dumps({
            "population": "Adults",
            "intervention": "Drug X"
            # missing comparison, outcome, claim_type, scope
        })
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=partial)]
        mock_client.messages.create.return_value = mock_message

        from services.pico_extractor import extract_pico
        result = extract_pico("Drug X treats adults.")

        assert "comparison" in result
        assert "outcome" in result
        assert "claim_type" in result


# ─────────────────────────────────────────────────────────────────────────────
# Claim Verifier Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestClaimVerifier:

    def _make_mock_claude_response(self, classification="Clinically Supported", confidence="High"):
        result = {
            "classification": classification,
            "confidence": confidence,
            "explanation": "Test explanation.",
            "key_issues": [],
            "evidence_quality": "Strong (RCT/Meta-analysis)",
            "population_match": True,
            "effect_exaggerated": False,
            "recommendation": "Test recommendation.",
            "cited_studies": ["PMID: 12345"]
        }
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(result))]
        return mock_message

    def _make_mock_papers(self):
        return [
            {
                "pmid": "12345", "title": "Test Study", "abstract": "Test abstract.",
                "year": "2022", "journal": "NEJM", "authors": ["Smith J"],
                "study_type": "Randomized Controlled Trial",
                "url": "https://pubmed.ncbi.nlm.nih.gov/12345/"
            }
        ]

    @patch('services.claim_verifier.client')
    @patch('services.claim_verifier.search_pubmed')
    @patch('services.claim_verifier.extract_pico')
    def test_full_pipeline_returns_classification(self, mock_pico, mock_search, mock_claude):
        mock_pico.return_value = {
            "population": "Adults", "intervention": "Exercise",
            "comparison": "Sedentary", "outcome": "Diabetes prevention",
            "claim_type": "prevention", "scope": "specific"
        }
        mock_search.return_value = self._make_mock_papers()
        mock_claude.messages.create.return_value = self._make_mock_claude_response("Clinically Supported")

        from services.claim_verifier import ClaimVerifier
        verifier = ClaimVerifier()
        result = verifier.verify("Exercise prevents diabetes in adults.")

        assert result["classification"] == "Clinically Supported"
        assert result["verdict_color"] == "green"
        assert result["claim"] == "Exercise prevents diabetes in adults."
        assert len(result["evidence"]) > 0
        assert "pico" in result

    @patch('services.claim_verifier.client')
    @patch('services.claim_verifier.search_pubmed')
    @patch('services.claim_verifier.extract_pico')
    def test_no_evidence_returns_insufficient(self, mock_pico, mock_search, mock_claude):
        mock_pico.return_value = {
            "population": "Adults", "intervention": "Mystery herb",
            "comparison": "not stated", "outcome": "Cures everything",
            "claim_type": "treatment", "scope": "universal"
        }
        mock_search.return_value = []  # No papers found

        from services.claim_verifier import ClaimVerifier
        verifier = ClaimVerifier()
        result = verifier.verify("Mystery herb cures everything.")

        assert result["classification"] == "Insufficient Evidence"
        assert result["evidence"] == []
        mock_claude.messages.create.assert_not_called()  # Claude not called if no evidence

    @patch('services.claim_verifier.client')
    @patch('services.claim_verifier.search_pubmed')
    @patch('services.claim_verifier.extract_pico')
    def test_verdict_colors_are_correct(self, mock_pico, mock_search, mock_claude):
        mock_pico.return_value = {
            "population": "Adults", "intervention": "Drug",
            "comparison": "Placebo", "outcome": "Outcome",
            "claim_type": "treatment", "scope": "specific"
        }
        mock_search.return_value = self._make_mock_papers()

        from services.claim_verifier import ClaimVerifier
        verifier = ClaimVerifier()

        test_cases = [
            ("Clinically Supported",          "green"),
            ("Misleading / Overgeneralized",  "yellow"),
            ("Contradicted",                  "red"),
            ("Insufficient Evidence",         "gray"),
        ]

        for classification, expected_color in test_cases:
            mock_claude.messages.create.return_value = self._make_mock_claude_response(classification)
            result = verifier.verify("Test claim.")
            assert result["verdict_color"] == expected_color, f"Expected {expected_color} for {classification}"

    @patch('services.claim_verifier.client')
    @patch('services.claim_verifier.search_pubmed')
    @patch('services.claim_verifier.extract_pico')
    def test_handles_malformed_claude_json(self, mock_pico, mock_search, mock_claude):
        mock_pico.return_value = {
            "population": "Adults", "intervention": "Drug",
            "comparison": "Placebo", "outcome": "Outcome",
            "claim_type": "treatment", "scope": "specific"
        }
        mock_search.return_value = self._make_mock_papers()

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="I cannot verify this claim. {invalid json}")]
        mock_claude.messages.create.return_value = mock_message

        from services.claim_verifier import ClaimVerifier
        verifier = ClaimVerifier()
        result = verifier.verify("Test claim.")

        # Should not raise, should return fallback
        assert "classification" in result
        assert "verdict_color" in result


# ─────────────────────────────────────────────────────────────────────────────
# Integration: Ground Truth Accuracy (requires real API — skipped in CI)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skip(reason="Requires live Anthropic API and PubMed access")
def test_ground_truth_accuracy():
    """
    Runs the full pipeline against ground_truth.json and measures classification accuracy.
    Expected accuracy: >= 75%
    """
    import json
    from services.claim_verifier import ClaimVerifier

    with open(os.path.join(os.path.dirname(__file__), '..', 'data', 'ground_truth.json')) as f:
        ground_truth = json.load(f)

    verifier = ClaimVerifier()
    correct = 0
    total = len(ground_truth)

    for item in ground_truth:
        result = verifier.verify(item["claim"])
        if result["classification"] == item["expected_classification"]:
            correct += 1

    accuracy = correct / total
    print(f"\nGround Truth Accuracy: {correct}/{total} = {accuracy:.1%}")
    assert accuracy >= 0.75, f"Accuracy {accuracy:.1%} below 75% threshold"
