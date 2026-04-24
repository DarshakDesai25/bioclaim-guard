"""
BioClaim Guard – Prompt Templates
All prompts for PICO extraction and claim verification.
"""

# ─────────────────────────────────────────────────────────────────────────────
# PICO EXTRACTION PROMPT
# Extracts Population, Intervention, Comparison, Outcome from a claim
# ─────────────────────────────────────────────────────────────────────────────

PICO_EXTRACTION_PROMPT = """You are a biomedical research specialist trained in evidence-based medicine.

Extract the PICO framework components from the medical claim below.

MEDICAL CLAIM:
{claim}

PICO Framework:
- Population: Who is the claim about? (age group, disease, demographics, biological sex)
- Intervention: What treatment, drug, behavior, or exposure is being evaluated?
- Comparison: What is it being compared to? (placebo, standard care, no treatment, or "not stated")
- Outcome: What health result or effect is claimed?
- Claim Type: One of: prevention | treatment | diagnosis | prognosis | harm | general

Return ONLY a valid JSON object — no preamble, no markdown:
{{
  "population": "...",
  "intervention": "...",
  "comparison": "...",
  "outcome": "...",
  "claim_type": "...",
  "scope": "specific" | "general" | "universal"
}}

Important:
- Use EXACTLY what is stated in the claim — do not infer or expand.
- If a PICO component is not explicitly mentioned, write "not stated".
- The "scope" field should reflect how broadly the claim applies:
  - "specific": mentions a particular group or condition
  - "general": vague but not absolute
  - "universal": uses language like "all", "everyone", "always"
"""

# ─────────────────────────────────────────────────────────────────────────────
# CLAIM VERIFICATION PROMPT
# Verifies a claim against retrieved PubMed evidence
# ─────────────────────────────────────────────────────────────────────────────

VERIFICATION_PROMPT = """You are a senior clinical evidence analyst. Your role is to critically evaluate medical claims against peer-reviewed evidence.

─────────────────────────────────
MEDICAL CLAIM TO EVALUATE:
{claim}

PICO ANALYSIS:
{pico}

RETRIEVED EVIDENCE FROM PUBMED:
{evidence}
─────────────────────────────────

EVALUATION TASK:
Carefully analyze whether the claim is supported, misleading, contradicted, or lacks sufficient evidence based on the retrieved studies.

Check for ALL of the following error types:
1. OVERGENERALIZATION — Applying findings from a specific group to the general population
2. POPULATION MISMATCH — Evidence is from a different demographic (age, sex, ethnicity, health status)
3. CAUSATION vs CORRELATION — Presenting associative findings as causal
4. STUDY DESIGN WEAKNESS — Using animal studies, in vitro data, or case reports to support human clinical claims
5. EFFECT SIZE EXAGGERATION — Inflating the magnitude or certainty of a benefit/risk
6. RECENCY BIAS — Outdated evidence contradicted by newer studies
7. MISSING CONTEXT — Omitting important conditions, dosages, or risk factors

CLASSIFICATION DEFINITIONS:
- "Clinically Supported": Multiple peer-reviewed human studies (preferably RCTs or meta-analyses) consistently support the claim for the stated population.
- "Misleading / Overgeneralized": Evidence exists but the claim is too broad, exaggerated, or missing critical qualifications.
- "Contradicted": Credible evidence directly opposes the claim.
- "Insufficient Evidence": No relevant studies found, or evidence is too weak to draw conclusions.

Return ONLY a valid JSON object — no preamble, no markdown:
{{
  "classification": "Clinically Supported" | "Misleading / Overgeneralized" | "Contradicted" | "Insufficient Evidence",
  "confidence": "High" | "Moderate" | "Low",
  "explanation": "2–3 sentence summary of why this classification was given, citing specific studies where possible.",
  "key_issues": ["issue 1", "issue 2"],
  "evidence_quality": "Strong (RCT/Meta-analysis)" | "Moderate (Cohort/Observational)" | "Weak (Case reports/Animal)" | "None found",
  "population_match": true | false,
  "effect_exaggerated": true | false,
  "recommendation": "1–2 sentence guidance for what a patient or clinician should know.",
  "cited_studies": ["PMID or study title 1", "PMID or study title 2"]
}}
"""

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH QUERY BUILDER PROMPT
# Converts a claim + PICO into an optimized PubMed search query
# ─────────────────────────────────────────────────────────────────────────────

QUERY_BUILDER_PROMPT = """You are an expert at building PubMed search queries.

Given the medical claim and its PICO components, generate an optimized PubMed search query.

CLAIM: {claim}

PICO:
{pico}

Rules:
- Focus on the intervention and outcome — these are most specific
- Include population ONLY if it is specific (e.g., "elderly", "diabetic patients")
- Use MeSH-style terms when possible
- Keep the query under 15 words
- Do NOT use boolean operators (AND/OR/NOT) — the API handles this

Return ONLY the query string, nothing else.
"""

# ─────────────────────────────────────────────────────────────────────────────
# FALLBACK MESSAGES
# Used when evidence retrieval fails or returns nothing
# ─────────────────────────────────────────────────────────────────────────────

FALLBACK_CLASSIFICATION = {
    "classification": "Insufficient Evidence",
    "confidence": "Low",
    "explanation": "No relevant peer-reviewed studies were found in PubMed for this claim. This may indicate the claim is based on anecdotal evidence, is too niche, or uses terminology not indexed in major medical databases.",
    "key_issues": ["No peer-reviewed evidence retrieved"],
    "evidence_quality": "None found",
    "population_match": False,
    "effect_exaggerated": False,
    "recommendation": "Consult a qualified healthcare professional before acting on unverified medical claims.",
    "cited_studies": [],
    "verdict_color": "gray"
}
