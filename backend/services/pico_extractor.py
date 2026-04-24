"""
BioClaim Guard – PICO Extractor Service
Uses Claude to decompose medical claims into PICO components.
"""

import anthropic
import json
import logging
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from prompts.templates import PICO_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Default PICO used when extraction fails
FALLBACK_PICO = {
    "population": "General population",
    "intervention": "Not stated",
    "comparison": "Not stated",
    "outcome": "Not stated",
    "claim_type": "general",
    "scope": "general"
}


def extract_pico(claim: str) -> dict:
    """
    Extract PICO components from a medical claim using Claude.
    
    Args:
        claim: Raw medical claim string
    
    Returns:
        Dict with keys: population, intervention, comparison, outcome, claim_type, scope
    """
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": PICO_EXTRACTION_PROMPT.format(claim=claim)
                }
            ]
        )

        response_text = message.content[0].text.strip()
        pico = _parse_json_response(response_text)

        if pico:
            logger.info(f"PICO extracted: {pico}")
            return pico
        else:
            logger.warning("PICO extraction returned empty — using fallback.")
            return FALLBACK_PICO

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error during PICO extraction: {e}")
        return FALLBACK_PICO
    except Exception as e:
        logger.error(f"Unexpected error during PICO extraction: {e}")
        return FALLBACK_PICO


def _parse_json_response(text: str) -> dict:
    """
    Safely extract and parse a JSON object from Claude's response.
    Handles cases where Claude wraps JSON in markdown code blocks.
    """
    # Strip markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Find first { ... } block
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {}

    json_str = text[start:end]
    
    try:
        parsed = json.loads(json_str)
        # Validate required keys
        required_keys = {"population", "intervention", "comparison", "outcome", "claim_type", "scope"}
        for key in required_keys:
            if key not in parsed:
                parsed[key] = FALLBACK_PICO.get(key, "not stated")
        return parsed
    except json.JSONDecodeError:
        return {}
