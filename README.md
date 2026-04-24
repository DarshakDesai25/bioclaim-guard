# BioClaim Guard – Healthcare AI Verification System

> **Verifying medical AI claims against peer-reviewed evidence using RAG + PICO + Claude.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Claude-orange.svg)](https://anthropic.com)

---

## Overview

Most AI systems **generate** medical answers. BioClaim Guard **verifies** them.

BioClaim Guard is a healthcare AI verification system that:
1. Accepts a medical claim as input
2. Decomposes it using the **PICO framework** (Population · Intervention · Comparison · Outcome)
3. Retrieves peer-reviewed studies from **PubMed** via the NCBI E-utilities API
4. Uses **Claude** to verify the claim against the evidence
5. Returns a structured verdict: **Clinically Supported**, **Misleading / Overgeneralized**, **Contradicted**, or **Insufficient Evidence**

---

## Architecture

```
User Input (React)
     │
     ▼
Flask API (/api/verify)
     │
     ├──► PICO Extractor (Claude)
     │         └── Extracts Population, Intervention, Comparison, Outcome
     │
     ├──► PubMed Retriever (NCBI E-utilities)
     │         └── Searches and fetches top-k peer-reviewed papers
     │
     └──► Claim Verifier (Claude + RAG)
               └── Compares claim against evidence → Classification + Explanation
```

**Core Components Implemented:**
- ✅ **Retrieval-Augmented Generation (RAG)** — PubMed search + contextual verification
- ✅ **Prompt Engineering** — PICO extraction, structured verification, edge case handling

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key

### 1. Clone the repository
```bash
git clone https://github.com/darshakdesai/bioclaim-guard.git
cd bioclaim-guard
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Frontend setup
```bash
cd ../frontend
npm install
```

### 4. Run the app
**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## API Reference

### `POST /api/verify`
Verify a medical claim.

**Request:**
```json
{ "claim": "Aspirin prevents heart attacks in all adults." }
```

**Response:**
```json
{
  "claim": "Aspirin prevents heart attacks in all adults.",
  "classification": "Misleading / Overgeneralized",
  "confidence": "High",
  "explanation": "While aspirin has proven benefit in secondary prevention...",
  "pico": {
    "population": "All adults",
    "intervention": "Aspirin",
    "comparison": "No aspirin",
    "outcome": "Prevention of heart attacks",
    "claim_type": "prevention",
    "scope": "universal"
  },
  "evidence": [...],
  "key_issues": ["Overgeneralization — claim applies to all adults without risk stratification"],
  "evidence_quality": "Strong (RCT/Meta-analysis)",
  "population_match": false,
  "effect_exaggerated": true,
  "recommendation": "Aspirin is recommended only for high-risk individuals...",
  "verdict_color": "yellow",
  "processing_time_ms": 8432
}
```

### `POST /api/search`
Direct PubMed search for testing.

### `GET /api/examples`
Returns 5 example claims with expected verdicts.

### `GET /api/health`
Health check endpoint.

---

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Classification Accuracy | % correct vs. ground truth | ≥ 75% |
| Retrieval Recall | Relevant studies retrieved | ≥ 0.70 |
| Faithfulness Score | Output aligned with retrieved evidence | ≥ 0.80 |
| Human Agreement | Alignment with clinical expert judgment | ≥ 0.75 |

Run evaluation against ground truth:
```bash
cd backend
pytest tests/test_verification.py::test_ground_truth_accuracy -v -s
```

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

Expected output: **17 tests pass** (integration test skipped without API key).

---

## Ethical Considerations

1. **Not medical advice** — BioClaim Guard is a research and education tool only.
2. **Data sources** — Only publicly available, de-identified PubMed data is used.
3. **Bias awareness** — Clinical trial populations are often non-representative. The system explicitly flags population mismatches.
4. **Uncertainty communication** — All outputs include confidence levels and evidence quality ratings.
5. **Transparency** — Every verdict links to the original PubMed studies.
6. **No personal data** — No user data is collected or stored.

---

## Project Structure

```
bioclaim-guard/
├── backend/
│   ├── app.py                    # Flask API
│   ├── config.py                 # Configuration
│   ├── requirements.txt
│   ├── services/
│   │   ├── pubmed_service.py     # PubMed RAG retrieval
│   │   ├── pico_extractor.py     # PICO decomposition (Claude)
│   │   └── claim_verifier.py    # Verification pipeline
│   └── prompts/
│       └── templates.py         # All prompt templates
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── api/client.js
│       └── components/
│           ├── ClaimInput.jsx
│           ├── ResultCard.jsx
│           ├── PICOBreakdown.jsx
│           ├── EvidenceCard.jsx
│           └── LoadingState.jsx
├── data/
│   └── ground_truth.json        # 8 labeled test claims
├── tests/
│   ├── test_pubmed.py
│   └── test_verification.py
└── README.md
```

---

## Author

**Darshak Desai** | NUID: 002021808  
Graduate student, Information Systems (AI track)

---

## Disclaimer

BioClaim Guard is a research prototype and does not constitute medical advice.
Always consult a qualified healthcare professional for medical decisions.
