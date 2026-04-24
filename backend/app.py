"""
BioClaim Guard – Healthcare AI Verification System
Flask Backend API
Author: Darshak Desai
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from services.claim_verifier import ClaimVerifier
from services.pubmed_service import search_pubmed
import traceback
import time

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

verifier = ClaimVerifier()


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "BioClaim Guard API", "version": "1.0.0"})


@app.route("/api/verify", methods=["POST"])
def verify_claim():
    """
    Main claim verification endpoint.
    Accepts a medical claim and returns structured verification result.
    
    Request Body:
        { "claim": "string" }
    
    Response:
        {
            "claim": "original claim",
            "classification": "Clinically Supported|Misleading/Overgeneralized|Contradicted|Insufficient Evidence",
            "confidence": "High|Moderate|Low",
            "explanation": "...",
            "pico": { population, intervention, comparison, outcome },
            "evidence": [ { pmid, title, abstract, year, journal, url } ],
            "key_issues": [...],
            "evidence_quality": "...",
            "recommendation": "...",
            "verdict_color": "green|yellow|red|gray",
            "processing_time_ms": int
        }
    """
    try:
        data = request.get_json()
        if not data or "claim" not in data:
            return jsonify({"error": "Request body must include a 'claim' field."}), 400

        claim = data["claim"].strip()
        if len(claim) < 10:
            return jsonify({"error": "Claim is too short. Please provide a complete medical statement."}), 400
        if len(claim) > 1000:
            return jsonify({"error": "Claim is too long. Please limit to 1000 characters."}), 400

        start_time = time.time()
        result = verifier.verify(claim)
        result["processing_time_ms"] = int((time.time() - start_time) * 1000)

        return jsonify(result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error. Please try again.", "detail": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def search_evidence():
    """
    Direct PubMed search endpoint for testing retrieval.
    
    Request Body:
        { "query": "string", "max_results": int (optional, default 5) }
    """
    try:
        data = request.get_json()
        if not data or "query" not in data:
            return jsonify({"error": "Request body must include a 'query' field."}), 400

        query = data["query"].strip()
        max_results = min(int(data.get("max_results", 5)), 10)

        papers = search_pubmed(query, max_results=max_results)
        return jsonify({"query": query, "results": papers, "count": len(papers)})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/examples", methods=["GET"])
def get_examples():
    """Return example claims for the frontend demo."""
    examples = [
        {
            "claim": "Aspirin prevents heart attacks in all adults.",
            "category": "Overgeneralization",
            "expected": "Misleading / Overgeneralized"
        },
        {
            "claim": "Regular exercise reduces the risk of type 2 diabetes in overweight adults.",
            "category": "Evidence-based",
            "expected": "Clinically Supported"
        },
        {
            "claim": "Vitamin C cures the common cold.",
            "category": "Exaggerated",
            "expected": "Contradicted"
        },
        {
            "claim": "Coffee consumption causes pancreatic cancer.",
            "category": "Outdated",
            "expected": "Contradicted"
        },
        {
            "claim": "High-dose omega-3 supplements prevent Alzheimer's disease.",
            "category": "Insufficient",
            "expected": "Insufficient Evidence"
        }
    ]
    return jsonify({"examples": examples})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed."}), 405


if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")
