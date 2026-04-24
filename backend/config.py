"""
BioClaim Guard – Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Anthropic ───────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# ─── PubMed / NCBI ───────────────────────────────────────────────────────────
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "bioclaimguard@research.edu")   # Required by NCBI
NCBI_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PUBMED_MAX_RESULTS = int(os.getenv("PUBMED_MAX_RESULTS", "5"))
PUBMED_REQUEST_DELAY = 0.34  # NCBI allows ~3 requests/sec without API key

# ─── ChromaDB ────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ─── App ─────────────────────────────────────────────────────────────────────
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
MAX_CLAIM_LENGTH = 1000

# ─── Verification ────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLDS = {
    "High": 0.8,
    "Moderate": 0.5,
    "Low": 0.0
}

VERDICT_COLORS = {
    "Clinically Supported": "green",
    "Misleading / Overgeneralized": "yellow",
    "Contradicted": "red",
    "Insufficient Evidence": "gray"
}
