"""
Tests for PubMed retrieval service.
Run: pytest tests/test_pubmed.py -v
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from unittest.mock import patch, MagicMock
from services.pubmed_service import (
    search_pubmed,
    build_pico_query,
    _classify_study_type,
    _parse_xml
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

SAMPLE_ESEARCH_RESPONSE = {
    "esearchresult": {
        "count": "2",
        "retmax": "5",
        "idlist": ["12345678", "87654321"]
    }
}

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <Journal>
          <Title>New England Journal of Medicine</Title>
          <JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue>
        </Journal>
        <ArticleTitle>Aspirin in Primary Prevention of Cardiovascular Disease</ArticleTitle>
        <Abstract>
          <AbstractText>This randomized controlled trial evaluated aspirin in primary prevention.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><LastName>Smith</LastName><ForeName>John</ForeName></Author>
          <Author><LastName>Doe</LastName><ForeName>Jane</ForeName></Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType>Randomized Controlled Trial</PublicationType>
        </PublicationTypeList>
        <ELocationID EIdType="doi">10.1056/test.12345</ELocationID>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="doi">10.1056/test.12345</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>"""


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestSearchPubMed:

    @patch('services.pubmed_service.requests.get')
    def test_returns_papers_on_success(self, mock_get):
        mock_esearch = MagicMock()
        mock_esearch.json.return_value = SAMPLE_ESEARCH_RESPONSE
        mock_esearch.raise_for_status = MagicMock()

        mock_efetch = MagicMock()
        mock_efetch.text = SAMPLE_XML
        mock_efetch.raise_for_status = MagicMock()

        mock_get.side_effect = [mock_esearch, mock_efetch]

        papers = search_pubmed("aspirin cardiovascular prevention", max_results=5)

        assert len(papers) == 1
        assert papers[0]["pmid"] == "12345678"
        assert papers[0]["journal"] == "New England Journal of Medicine"
        assert papers[0]["year"] == "2020"
        assert papers[0]["study_type"] == "Randomized Controlled Trial"
        assert "pubmed.ncbi.nlm.nih.gov/12345678" in papers[0]["url"]

    @patch('services.pubmed_service.requests.get')
    def test_returns_empty_when_no_results(self, mock_get):
        mock_esearch = MagicMock()
        mock_esearch.json.return_value = {"esearchresult": {"idlist": []}}
        mock_esearch.raise_for_status = MagicMock()

        mock_get.return_value = mock_esearch
        papers = search_pubmed("xyzzy_nonexistent_medical_term_12345")

        assert papers == []

    @patch('services.pubmed_service.requests.get')
    def test_handles_network_error_gracefully(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        papers = search_pubmed("aspirin")
        assert papers == []


class TestBuildPicoQuery:

    def test_uses_intervention_and_outcome(self):
        pico = {
            "population": "not stated",
            "intervention": "metformin",
            "comparison": "not stated",
            "outcome": "blood glucose reduction"
        }
        query = build_pico_query(pico, "Metformin reduces blood glucose")
        assert "metformin" in query.lower()
        assert "blood glucose" in query.lower()

    def test_includes_specific_population(self):
        pico = {
            "population": "elderly patients",
            "intervention": "aspirin",
            "outcome": "stroke prevention"
        }
        query = build_pico_query(pico, "aspirin for elderly")
        assert "elderly" in query.lower()

    def test_excludes_general_population(self):
        pico = {
            "population": "general population",
            "intervention": "vitamin C",
            "outcome": "cold prevention"
        }
        query = build_pico_query(pico, "Vitamin C prevents colds")
        assert "general population" not in query.lower()

    def test_falls_back_to_claim_when_pico_empty(self):
        pico = {
            "population": "not stated",
            "intervention": "not stated",
            "outcome": "not stated"
        }
        claim = "some medical claim"
        query = build_pico_query(pico, claim)
        assert query == claim

    def test_truncates_long_query(self):
        pico = {
            "population": "a" * 100,
            "intervention": "b" * 100,
            "outcome": "c" * 100
        }
        query = build_pico_query(pico, "test claim")
        assert len(query) <= 200


class TestClassifyStudyType:

    def test_identifies_rct(self):
        assert _classify_study_type(["Randomized Controlled Trial"]) == "Randomized Controlled Trial"

    def test_identifies_meta_analysis(self):
        assert _classify_study_type(["Meta-Analysis"]) == "Meta-Analysis"

    def test_identifies_systematic_review(self):
        assert _classify_study_type(["Systematic Review"]) == "Systematic Review"

    def test_defaults_to_observational(self):
        assert _classify_study_type(["Journal Article"]) == "Observational Study"

    def test_meta_analysis_takes_priority(self):
        result = _classify_study_type(["Meta-Analysis", "Systematic Review"])
        assert result == "Meta-Analysis"


class TestParseXML:

    def test_parses_valid_xml(self):
        papers = _parse_xml(SAMPLE_XML)
        assert len(papers) == 1
        assert papers[0]["title"] == "Aspirin in Primary Prevention of Cardiovascular Disease"

    def test_handles_malformed_xml(self):
        papers = _parse_xml("<invalid xml>")
        assert papers == []

    def test_handles_empty_xml(self):
        papers = _parse_xml('<?xml version="1.0"?><PubmedArticleSet></PubmedArticleSet>')
        assert papers == []
