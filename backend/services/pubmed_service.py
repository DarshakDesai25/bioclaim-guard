"""
BioClaim Guard – PubMed Retrieval Service
Fetches peer-reviewed evidence from NCBI PubMed using the Entrez E-utilities API.
"""

import requests
import xml.etree.ElementTree as ET
import time
import logging
from typing import List, Dict, Optional
from config import NCBI_BASE_URL, NCBI_EMAIL, PUBMED_REQUEST_DELAY

logger = logging.getLogger(__name__)


def search_pubmed(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search PubMed for relevant papers and return structured results.
    
    Args:
        query: Search query string
        max_results: Maximum number of papers to retrieve (max 10)
    
    Returns:
        List of paper dicts with pmid, title, abstract, year, journal, authors, url
    """
    try:
        pmids = _esearch(query, max_results)
        if not pmids:
            logger.info(f"No results for query: {query}")
            return []
        
        time.sleep(PUBMED_REQUEST_DELAY)  # Respect NCBI rate limits
        papers = _efetch(pmids)
        logger.info(f"Retrieved {len(papers)} papers for query: {query}")
        return papers

    except requests.exceptions.RequestException as e:
        logger.error(f"PubMed request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in search_pubmed: {e}")
        return []


def _esearch(query: str, max_results: int) -> List[str]:
    """Search PubMed and return a list of PMIDs."""
    url = f"{NCBI_BASE_URL}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "email": NCBI_EMAIL,
        "sort": "relevance",
        "usehistory": "n"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def _efetch(pmids: List[str]) -> List[Dict]:
    """Fetch full records for a list of PMIDs."""
    url = f"{NCBI_BASE_URL}efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract",
        "email": NCBI_EMAIL
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    return _parse_xml(response.text)


def _parse_xml(xml_text: str) -> List[Dict]:
    """Parse PubMed XML response into structured paper dicts."""
    papers = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        logger.error(f"XML parse error: {e}")
        return []

    for article in root.findall(".//PubmedArticle"):
        try:
            pmid = article.findtext(".//PMID", default="")
            title = _clean_text(article.findtext(".//ArticleTitle", default="No title"))
            
            # Handle structured and unstructured abstracts
            abstract_parts = article.findall(".//AbstractText")
            if abstract_parts:
                abstract_segments = []
                for part in abstract_parts:
                    label = part.get("Label", "")
                    text = part.text or ""
                    if label:
                        abstract_segments.append(f"{label}: {text}")
                    else:
                        abstract_segments.append(text)
                abstract = " ".join(abstract_segments)
            else:
                abstract = "Abstract not available."
            
            # Limit abstract length to avoid token overflow
            abstract = abstract[:2000]

            # Publication year
            year = (
                article.findtext(".//PubDate/Year")
                or article.findtext(".//PubDate/MedlineDate", "")[:4]
                or "N/A"
            )

            journal = article.findtext(".//Journal/Title", default="Unknown Journal")

            # Authors (up to 4)
            authors = []
            for author in article.findall(".//Author")[:4]:
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{last} {fore}".strip())
            
            if len(article.findall(".//Author")) > 4:
                authors.append("et al.")

            # Study type from publication types
            pub_types = [
                pt.text for pt in article.findall(".//PublicationType") if pt.text
            ]
            study_type = _classify_study_type(pub_types)

            # DOI
            doi = ""
            for id_elem in article.findall(".//ArticleId"):
                if id_elem.get("IdType") == "doi":
                    doi = id_elem.text or ""
                    break

            papers.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "year": year,
                "journal": journal,
                "authors": authors,
                "study_type": study_type,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

        except Exception as e:
            logger.warning(f"Failed to parse article: {e}")
            continue

    return papers


def _classify_study_type(pub_types: List[str]) -> str:
    """Classify study design based on PubMed publication types."""
    pub_types_lower = [pt.lower() for pt in pub_types]
    
    if any("meta-analysis" in pt for pt in pub_types_lower):
        return "Meta-Analysis"
    if any("systematic review" in pt for pt in pub_types_lower):
        return "Systematic Review"
    if any("randomized controlled trial" in pt for pt in pub_types_lower):
        return "Randomized Controlled Trial"
    if any("clinical trial" in pt for pt in pub_types_lower):
        return "Clinical Trial"
    if any("review" in pt for pt in pub_types_lower):
        return "Review"
    if any("case reports" in pt for pt in pub_types_lower):
        return "Case Report"
    return "Observational Study"


def _clean_text(text: str) -> str:
    """Remove XML artifacts and extra whitespace from text."""
    if not text:
        return ""
    return " ".join(text.split())


def build_pico_query(pico: dict, original_claim: str) -> str:
    """
    Build an optimized PubMed search query from PICO components.
    Prioritizes intervention + outcome as these are most distinctive.
    """
    parts = []

    intervention = pico.get("intervention", "")
    outcome = pico.get("outcome", "")
    population = pico.get("population", "")

    if intervention and intervention.lower() != "not stated":
        parts.append(intervention)
    if outcome and outcome.lower() != "not stated":
        parts.append(outcome)
    if population and population.lower() not in ("not stated", "general population", "general"):
        parts.append(population)

    query = " ".join(parts) if parts else original_claim
    
    # Truncate to reasonable length
    return query[:200]
