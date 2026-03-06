"""
MCP Server for CUCP Re-Evaluations
===================================
Exposes all CUCP evaluation functions as MCP tools over SSE (HTTP) transport.
Run with:  python -m src.mcp_server
Then open an ngrok tunnel to the printed port for external access.
"""

import os
import sys
import datetime
from typing import Optional

# Ensure the project root is on sys.path so `src.*` imports work
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Import the functions we want to expose
# ---------------------------------------------------------------------------
from src.cucp_reevals import (
    extract_text_from_pdf,
    run_level_1_extraction,
    run_level_2_classification,
    run_level_3_thresholds,
    generate_final_md_report,
    cucp_reevaluations,
)
from src.memory_manager import (
    get_precedents,
    get_precedent_count,
    add_precedent,
    commit_staged_precedents,
    consolidate_memory_via_llm,
)

# ---------------------------------------------------------------------------
# Create the MCP server
# ---------------------------------------------------------------------------
MCP_PORT = int(os.environ.get("MCP_PORT", 8000))

mcp = FastMCP(
    "CUCP Re-Evaluations",
    instructions="MCP server exposing the Caltrans CUCP SED re-evaluation pipeline.",
    host="0.0.0.0",
    port=MCP_PORT,
)


# ===========================  HEALTH CHECK  ================================

@mcp.tool()
def server_status() -> dict:
    """Return server health, version info, and available tool count."""
    return {
        "status": "running",
        "service": "CUCP Re-Evaluations MCP Server",
        "version": "1.1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "tools_available": 13,
    }


# ========================  CUCP EVALUATION TOOLS  =========================

@mcp.tool()
def extract_pdf_text(pdf_path: str) -> str:
    """Extract all text from a PDF file given its absolute file path."""
    return extract_text_from_pdf(pdf_path)


@mcp.tool()
def level_1_fact_extraction(
    narrative_text: str,
    firm_revenues: Optional[dict] = None,
    staged_precedents: Optional[list] = None,
) -> dict:
    """
    Level 1 – Fact Extraction (the "Perceptual" layer).
    Extracts raw facts (W5 + magnitude) from a SED narrative.

    Args:
        narrative_text: The full text of the applicant's SED narrative.
        firm_revenues: Optional dict of firm revenue data for cross-referencing.
        staged_precedents: Optional list of staged human correction objects.

    Returns:
        Dict with extracted_facts, firm_name, cross_reference_result, and narrative_pnw.
    """
    return run_level_1_extraction(narrative_text, firm_revenues, staged_precedents)


@mcp.tool()
def level_2_legal_classification(
    facts: list,
    combined_financials: str = "",
    staged_precedents: Optional[list] = None,
) -> dict:
    """
    Level 2 – Legal Classification (the "Definitional" layer).
    Classifies each extracted fact under 49 CFR §26.67 categories.

    Args:
        facts: List of fact objects (output of Level 1's 'extracted_facts').
        combined_financials: Optional plain-text financial context.
        staged_precedents: Optional list of staged human correction objects.

    Returns:
        Dict with classifications for each fact.
    """
    return run_level_2_classification(facts, combined_financials, staged_precedents)


@mcp.tool()
def level_3_evidentiary_thresholds(
    classifications: list,
    facts: list,
    pnw_result: str,
    staged_precedents: Optional[list] = None,
) -> dict:
    """
    Level 3 – Evidentiary Threshold (the "Magnitude" layer).
    Applies the 7 mandatory CUCP criteria and produces Pass/Fail decisions.

    Args:
        classifications: List of Level 2 classification objects.
        facts: List of Level 1 extracted fact objects.
        pnw_result: The PNW data point string (e.g. from cross-reference or narrative).
        staged_precedents: Optional list of staged human correction objects.

    Returns:
        Dict with criteria evaluations, final_decision, and certifier_comments.
    """
    return run_level_3_thresholds(classifications, facts, pnw_result, staged_precedents)


@mcp.tool()
def generate_evaluation_report(
    level_1_data: dict,
    level_3_data: dict,
) -> str:
    """
    Generate the final markdown evaluation report from Level 1 and Level 3 outputs.

    Args:
        level_1_data: Dict of Level 1 extraction output.
        level_3_data: Dict of Level 3 threshold output.

    Returns:
        Formatted markdown report string.
    """
    return generate_final_md_report(level_1_data, level_3_data)


@mcp.tool()
def run_full_reevaluation(
    pdf_path: str,
    firm_revenues: Optional[dict] = None,
) -> str:
    """
    End-to-end CUCP re-evaluation pipeline (PDF-based).
    Takes a PDF file path, runs all 3 levels, and returns a markdown report.

    Args:
        pdf_path: Absolute path to the applicant's PDF narrative.
        firm_revenues: Optional dict of firm revenue data.

    Returns:
        Complete markdown evaluation report.
    """
    return cucp_reevaluations(pdf_path, firm_revenues)


@mcp.tool()
def evaluate_case(
    narrative_text: str,
    firm_revenues: Optional[dict] = None,
) -> dict:
    """
    Run the full CUCP reasoning pipeline on raw narrative text (no PDF needed).
    Returns the structured output from all 3 evaluation levels.

    This is the recommended tool for Copilot Studio integrations where
    the agent has the narrative text but not a local file path.

    Args:
        narrative_text: The full text of the applicant's SED narrative.
        firm_revenues: Optional dict of firm revenue data for cross-referencing.

    Returns:
        Dict with level1, level2, and level3 evaluation results.
    """
    l1 = run_level_1_extraction(narrative_text, firm_revenues)
    l2 = run_level_2_classification(l1.get("extracted_facts", []))
    l3 = run_level_3_thresholds(
        l2.get("classifications", []),
        l1.get("extracted_facts", []),
        l1.get("cross_reference_result", "None"),
    )
    return {
        "level1": l1,
        "level2": l2,
        "level3": l3,
    }


# ======================  MEMORY / PRECEDENT TOOLS  ========================

@mcp.tool()
def get_precedents_for_level(level: int) -> list:
    """
    Retrieve all stored human-correction precedents for a given reasoning level (1, 2, or 3).

    Args:
        level: The reasoning level (1, 2, or 3).

    Returns:
        List of precedent objects.
    """
    return get_precedents(level)


@mcp.tool()
def get_precedent_count_for_level(level: int) -> int:
    """
    Return the total number of active precedents for the given level.

    Args:
        level: The reasoning level (1, 2, or 3).

    Returns:
        Integer count.
    """
    return get_precedent_count(level)


@mcp.tool()
def add_human_correction(
    level: int,
    target: str,
    correction: str,
    reasoning: str,
) -> dict:
    """
    Log a human correction as a precedent for future evaluations.

    Args:
        level: The reasoning level (1, 2, or 3).
        target: The specific fact/classification/threshold being corrected.
        correction: The correct value.
        reasoning: The human's rationale.

    Returns:
        Confirmation with level and new count.
    """
    add_precedent(level, target, correction, reasoning)
    return {
        "status": "success",
        "level": level,
        "total_precedents": get_precedent_count(level),
    }


@mcp.tool()
def commit_staged(staged_db: dict) -> dict:
    """
    Commit a batch of staged precedents to the main memory database.

    Args:
        staged_db: Dict with keys 'level_1_precedents', 'level_2_precedents', 'level_3_precedents'.

    Returns:
        Confirmation with updated counts per level.
    """
    commit_staged_precedents(staged_db)
    return {
        "status": "success",
        "level_1_count": get_precedent_count(1),
        "level_2_count": get_precedent_count(2),
        "level_3_count": get_precedent_count(3),
    }


@mcp.tool()
def consolidate_memory() -> str:
    """
    Use GPT-4o to deduplicate and synthesize overlapping human corrections
    into a clean consolidated rules set. Returns the synthesized JSON.

    Returns:
        JSON string of the consolidated rules.
    """
    return consolidate_memory_via_llm()


# ---------------------------------------------------------------------------
# Entry point — run with SSE transport + optional ngrok tunnel
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CUCP MCP Server")
    parser.add_argument("--port", type=int, default=MCP_PORT, help="Port for the SSE server (default: 8000)")
    parser.add_argument("--ngrok", action="store_true", help="Open an ngrok tunnel for external access")
    parser.add_argument("--ngrok-token", type=str, default=None, help="ngrok auth token (or set NGROK_AUTHTOKEN env var)")
    args = parser.parse_args()

    # Update the port on the mcp instance if overridden via CLI
    mcp.settings.port = args.port
    mcp.settings.host = "0.0.0.0"

    if args.ngrok:
        try:
            from pyngrok import ngrok, conf

            token = args.ngrok_token or os.environ.get("NGROK_AUTHTOKEN")
            if token:
                conf.get_default().auth_token = token

            tunnel = ngrok.connect(addr=args.port, proto="http")
            public_url = tunnel.public_url
            print("=" * 60)
            print(f"  ngrok tunnel opened!") 
            print(f"  Public URL : {public_url}")
            print(f"  MCP Endpoint: {public_url}/mcp")
            print("=" * 60)
        except ImportError:
            print("WARNING: pyngrok not installed. Run:  pip install pyngrok")
            print("Starting without ngrok tunnel...")
        except Exception as e:
            print(f"WARNING: ngrok failed to start: {e}")
            print("Starting without ngrok tunnel...")

    print(f"\nStarting CUCP MCP Server on port {args.port} (streamable-http transport)...")
    mcp.run(transport="streamable-http")
