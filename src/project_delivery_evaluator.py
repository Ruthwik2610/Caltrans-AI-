import json
import datetime
from io import BytesIO
from openai import OpenAI
from docx import Document
from src.delivery_method_kb import DELIVERY_METHOD_KB_TEXT

def _get_client():
    return OpenAI()

# ==============================================================================
# RUBRIC: 25 Questions extracted from AltDeliveryNominFactSheet Tables 3-8
# ==============================================================================
RUBRIC_QUESTIONS = [
    # --- Section A: Project Scope & Characteristics (Table 3, A1-A10) ---
    {
        "id": "A1", "section": "A: Project Scope & Characteristics",
        "question": "Where is the Project in the project development process?",
        "option_a": "Detailed or final engineering stage (60% design or later).",
        "option_b": "Preliminary design (30% design).",
        "option_c": "Conceptual engineering stage (before PA&ED).",
    },
    {
        "id": "A2", "section": "A: Project Scope & Characteristics",
        "question": "What is the size of the Project?",
        "option_a": "Small project (less than $25 million construction capital cost).",
        "option_b": "Medium size project (between $25 to $75 million construction capital cost).",
        "option_c": "Large project (greater than $75 million construction capital cost).",
    },
    {
        "id": "A3", "section": "A: Project Scope & Characteristics",
        "question": "What is the complexity of the Project?",
        "option_a": "Relatively simple project with no need for specialized outside expertise.",
        "option_b": "Project with more technically complex components and schedule complexity.",
        "option_c": "Very complex project with significant schedule complexity (e.g., multiple phases, extensive third-party issues, and/or specialized expertise needed).",
    },
    {
        "id": "A4", "section": "A: Project Scope & Characteristics",
        "question": "Does the Project involve significant impacts to highway users and local businesses/community during construction?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A5", "section": "A: Project Scope & Characteristics",
        "question": "Does the Project present right of way limitations that would benefit from the Entity's assistance?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A6", "section": "A: Project Scope & Characteristics",
        "question": "Does the Project present environmental permitting issues that would benefit from the Entity's assistance?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A7", "section": "A: Project Scope & Characteristics",
        "question": "Does the Project present utility or third-party issues that would benefit from the Entity's assistance?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A8", "section": "A: Project Scope & Characteristics",
        "question": "Does the Project present unique work restrictions (e.g., strict environmental windows, railroad restrictions) or traffic maintenance requirements that would benefit from the Entity's assistance?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A9", "section": "A: Project Scope & Characteristics",
        "question": "Would the Project benefit by packaging features of work to allow early lock-in of construction materials/labor pricing?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "A10", "section": "A: Project Scope & Characteristics",
        "question": "Would the Project benefit by raising quality standards/benchmarks to minimize maintenance and achieve lower life-cycle cost?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    # --- Section B: Schedule Issues (Table 4, B1-B2) ---
    {
        "id": "B1", "section": "B: Schedule Issues",
        "question": "Can time savings be realized through concurrent design and construction activities (fast-tracking)?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "B2", "section": "B: Schedule Issues",
        "question": "Can the schedule be compressed?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    # --- Section C: Opportunity for Innovation (Table 5, C1-C2) ---
    {
        "id": "C1", "section": "C: Opportunity for Innovation",
        "question": "Will the Project scope allow for innovation (e.g., alternate designs, traffic management, construction means and methods, etc.)?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "C2", "section": "C: Opportunity for Innovation",
        "question": "Must the Project scope be primarily defined in terms of prescriptive specifications, or can performance specifications be used, or a combination of both?",
        "option_a": "Primarily prescriptive specifications.",
        "option_b": "Combination of prescriptive and performance specifications.",
        "option_c": "Performance specifications for significant elements.",
    },
    # --- Section D: Quality Enhancement (Table 6, D1-D3) ---
    {
        "id": "D1", "section": "D: Quality Enhancement",
        "question": "Will there be opportunities for the Entity to provide materials or methods that provide greater value than normally specified by the state on similar projects?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "D2", "section": "D: Quality Enhancement",
        "question": "Will there be the opportunity for realization of greater value due to designs tailored to Entity's area of expertise?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "D3", "section": "D: Quality Enhancement",
        "question": "Will warranties or maintenance agreements be used?",
        "option_a": "No.",
        "option_b": "Limited to short-term workmanship and materials.",
        "option_c": "Much more than typical.",
    },
    # --- Section E: Cost Issues (Table 7, E1-E5) ---
    {
        "id": "E1", "section": "E: Cost Issues",
        "question": "Will there be opportunities for the Entity to provide designs with lower initial construction costs than those typically specified by the state?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "E2", "section": "E: Cost Issues",
        "question": "Will there be opportunities for the Entity to provide alternate design concepts with lower lifecycle costs than those typically specified by the state?",
        "option_a": "No more than typical.",
        "option_b": "More than typical.",
        "option_c": "Much more than typical.",
    },
    {
        "id": "E3", "section": "E: Cost Issues",
        "question": "Is funding for the Project committed and available?",
        "option_a": "Secured for design phase only or cannot support accelerated construction.",
        "option_b": "Funding can accommodate fast-tracking to some extent.",
        "option_c": "Funding will accommodate compressed schedule/fast-tracking.",
    },
    {
        "id": "E4", "section": "E: Cost Issues",
        "question": "Will the cost of procurement affect the number of bidders?",
        "option_a": "Procurement cost would significantly limit competition.",
        "option_b": "Procurement cost could affect the number of bidders.",
        "option_c": "Procurement cost would not be a significant issue given the size or complexity of the Project.",
    },
    {
        "id": "E5", "section": "E: Cost Issues",
        "question": "Will Project budget control benefit from the use of formal contingencies?",
        "option_a": "No benefit.",
        "option_b": "A formal contingency may permit the Department to add Project scope or enhance quality within the constraints of its published budget.",
        "option_c": "A formal contingency is required to allow the Department to maximize Project scope and quality within the constraints of its published budget.",
    },
    # --- Section F: Staffing Issues (Table 8, F1-F3) ---
    {
        "id": "F1", "section": "F: Staffing Issues",
        "question": "Does the Department have the expertise and resources necessary for a complicated procurement process?",
        "option_a": "Inadequate resources or expertise.",
        "option_b": "Limited resources or expertise.",
        "option_c": "Adequate resources and expertise.",
    },
    {
        "id": "F2", "section": "F: Staffing Issues",
        "question": "Are resources available to complete the design?",
        "option_a": "Resources are available to complete design.",
        "option_b": "Resources are available for partial design.",
        "option_c": "Specialized expertise, not available in-house, is required.",
    },
    {
        "id": "F3", "section": "F: Staffing Issues",
        "question": "Are resources available to provide construction oversight?",
        "option_a": "Resources are available.",
        "option_b": "Full-time construction oversight could strain staff resources.",
        "option_c": "Resources are unavailable.",
    },
]

# Section weights for scoring matrix
SECTION_WEIGHTS = {
    "A": 0.30,  # Project Scope & Characteristics (10 questions)
    "B": 0.15,  # Schedule Issues (2 questions)
    "C": 0.12,  # Opportunity for Innovation (2 questions)
    "D": 0.10,  # Quality Enhancement (3 questions)
    "E": 0.20,  # Cost Issues (5 questions)
    "F": 0.13,  # Staffing Issues (3 questions)
}

RATING_VALUES = {"A": 1, "B": 2, "C": 3}


# ==============================================================================
# DOCUMENT EXTRACTION
# ==============================================================================
def extract_text_from_uploaded_pdf(file) -> str:
    """Extract text from an uploaded PDF file object."""
    from PyPDF2 import PdfReader
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_text_from_docx(file) -> tuple:
    """Extract narrative text and any pre-filled ratings from a nomination fact sheet DOCX.

    Returns:
        (narrative_text, existing_ratings) where existing_ratings is a dict like {"A1": "B", ...}
    """
    doc = Document(file)

    # Extract paragraph text (Sections 1-12, stop at Section 13)
    narrative_parts = []
    stop_keywords = [
        "Project Risk Assessment",
        "Construction Manager Tasks",
        "Glossary of Preconstruction",
        "District Single Point Signature",
    ]
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if any(kw.lower() in text.lower() for kw in stop_keywords):
            break
        narrative_parts.append(text)
    narrative_text = "\n".join(narrative_parts)

    # Extract pre-filled ratings from Tables 3-8 (evaluation question tables)
    existing_ratings = {}
    for table in doc.tables:
        if len(table.columns) != 3:
            continue
        header_cells = [cell.text.strip().upper() for cell in table.rows[0].cells]
        if "QUESTION NO." not in header_cells[0] and "QUESTION" not in header_cells[0]:
            continue
        # This is a rubric question table
        for row in table.rows[1:]:
            cells = [cell.text.strip() for cell in row.cells]
            question_id = cells[0].strip()
            rating_text = cells[2].strip().upper() if len(cells) > 2 else ""
            if question_id and rating_text in ("A", "B", "C"):
                existing_ratings[question_id] = rating_text

    return narrative_text, existing_ratings


def load_delivery_method_kb() -> str:
    """Return the embedded delivery method knowledge base text."""
    return DELIVERY_METHOD_KB_TEXT


# ==============================================================================
# SYSTEM PROMPT CONSTRUCTION
# ==============================================================================
def _build_rubric_text() -> str:
    """Format the 25 rubric questions for prompt injection."""
    lines = ["RUBRIC - 25 EVALUATION QUESTIONS:", "For each question, select exactly one rating: A (first option), B (second option), or C (third option).", ""]
    current_section = ""
    for q in RUBRIC_QUESTIONS:
        if q["section"] != current_section:
            current_section = q["section"]
            lines.append(f"--- {current_section} ---")
        lines.append(f'[{q["id"]}] {q["question"]}')
        lines.append(f'  A: {q["option_a"]}')
        lines.append(f'  B: {q["option_b"]}')
        lines.append(f'  C: {q["option_c"]}')
        lines.append("")
    return "\n".join(lines)


def _build_system_prompt(kb_text: str, existing_ratings: dict = None) -> str:
    """Build the full system prompt for the delivery evaluation."""

    persona = """You are a Senior Alternative Contracting Expert at Caltrans Headquarters, Office of Innovative Design and Delivery (OIDD). You have 20+ years of experience evaluating project delivery method nominations across California. Your role is to objectively evaluate a district's nomination fact sheet against the 25-question delivery selection rubric.

You are meticulous, evidence-based, and transparent about uncertainty. When the narrative lacks information for a question, you flag it clearly rather than guessing confidently."""

    kb_section = f"""DELIVERY METHOD COMPARISON KNOWLEDGE BASE:
Use the following reference to understand how each delivery method performs across different project factors (Project Requirements, Delivery Schedule, Complexity & Innovation, Level of Design, Cost, Risk Characteristics, Site Conditions, Utilities, Environmental, ROW, Third-Party Involvement):

{kb_text}"""

    design_sequencing = """ADDITIONAL METHOD - DESIGN-SEQUENCING:
Design-Sequencing is NOT in the comparison PDF above. Key characteristics:
- A variant of Design-Bid-Build where design packages are released sequentially
- Allows construction to begin on early packages while later packages are still being designed
- Department retains full design control (like DBB)
- Lower procurement complexity than DB or CMGC
- Appropriate when: project is moderately complex, schedule benefits from partial overlap, but full design-build risk transfer is not warranted
- Does not require contractor input during design (unlike CMGC)"""

    rubric_text = _build_rubric_text()

    baseline_norms = """CALTRANS BASELINE NORMS (apply these quantitative thresholds when data is available):
- A1 (Development Stage): 60%+ design = A, ~30% design = B, before PA&ED = C
- A2 (Project Size): <$25M construction capital = A, $25-75M = B, >$75M = C
- E3 (Funding): Secured for design only = A, can accommodate some fast-tracking = B, full compressed schedule = C
- E4 (Procurement Cost): Significantly limits competition = A, could affect bidders = B, not significant = C
- F1 (Procurement Expertise): Inadequate = A, Limited = B, Adequate = C
- F2 (Design Resources): Available to complete = A, Available for partial = B, Specialized expertise needed = C
- F3 (Construction Oversight): Available = A, Could strain staff = B, Unavailable = C
For questions using "No more than typical / More than typical / Much more than typical", use these guidelines:
- A (No more than typical): Standard Caltrans project, no unusual factors
- B (More than typical): Notable complexity or needs beyond standard, but manageable
- C (Much more than typical): Exceptional complexity, significant challenges requiring specialized approaches"""

    few_shot = """EVALUATION METHODOLOGY:
For each of the 25 questions, follow this chain-of-thought:
1. EXTRACT: Find all evidence in the narrative relevant to this question. Quote or summarize directly.
2. ANALYZE: Apply the rubric criteria. Compare evidence against options A, B, and C.
3. RATE: Select the rating that best matches.
4. FLAG: If insufficient evidence, set missing_info to true and estimate using domain knowledge. Lower confidence to 0.2-0.4 for estimates.

When a question has no direct evidence, check if related questions provide indirect evidence. For example, if A3 (complexity) has evidence of high complexity, that indirectly supports higher ratings for C1 (innovation opportunity) and B1 (fast-tracking benefit).

EXAMPLE 1 - Question A2 (Project Size):
extracted_evidence: "The construction capital cost is estimated at $45 million."
rubric_analysis: "$45M falls between $25M and $75M per Caltrans thresholds for A2."
selected_rating: "B"
confidence: 0.95
missing_info: false

EXAMPLE 2 - Question A7 (Utility/Third-Party Issues):
extracted_evidence: "The project requires coordination with BNSF railroad for track closures and PG&E for gas line relocation. Multiple utility relocations are anticipated."
rubric_analysis: "Railroad and utility coordination involving multiple parties goes beyond typical. Two major utility entities plus railroad suggests 'More than typical' but not necessarily 'Much more than typical' unless additional complexity exists."
selected_rating: "B"
confidence: 0.85
missing_info: false

EXAMPLE 3 - Question C1 (Innovation) with missing info:
extracted_evidence: "No explicit discussion of innovation opportunities found in the narrative."
rubric_analysis: "The narrative does not address innovation. Based on the project's complexity (if A3 suggests moderate complexity) and highway scope, moderate innovation potential is plausible but unconfirmed."
selected_rating: "B"
confidence: 0.35
missing_info: true"""

    exclusion = """IMPORTANT EXCLUSIONS:
- Do NOT evaluate any content from Sections 13, 14, or 15 of the fact sheet (Risk Register, CMGC Task Selection, Glossary).
- Evaluate ONLY based on the project narrative from Sections 1-12 and any supplementary project details.
- Your evaluation must cover ALL 25 questions (A1 through F3). Do not skip any."""

    existing_ratings_text = ""
    if existing_ratings:
        ratings_str = ", ".join(f"{k}={v}" for k, v in sorted(existing_ratings.items()))
        existing_ratings_text = f"""
DISTRICT PRE-FILLED RATINGS:
The district has pre-filled these ratings: {ratings_str}
Evaluate independently based on the evidence. After your independent evaluation, if your rating differs from the district's, note the disagreement in your rubric_analysis."""

    output_schema = """OUTPUT FORMAT:
You must output ONLY valid JSON in the following format. Replace all placeholders with real values extracted from the narrative.

{
  "project_name": "<extract project name or description from the narrative>",
  "project_ea": "<extract Project EA number or NOT PROVIDED>",
  "district": "<extract district name/number or NOT PROVIDED>",
  "evaluation_date": "<today's date in YYYY-MM-DD format>",
  "ratings": [
    {
      "question_id": "A1",
      "question_text": "Where is the Project in the project development process?",
      "extracted_evidence": "<direct quote or summary from narrative, or 'No direct evidence found'>",
      "rubric_analysis": "<chain-of-thought reasoning explaining how the evidence maps to the selected rating>",
      "selected_rating": "A or B or C",
      "confidence": 0.0 to 1.0,
      "missing_info": true or false
    }
  ],
  "missing_questions": ["list of question_ids where missing_info is true"],
  "summary": "<2-3 sentence overall assessment of the project and evaluation quality>"
}

CRITICAL: The "ratings" array must contain EXACTLY 25 items, one for each question A1 through F3, in order."""

    return "\n\n".join([
        persona, kb_section, design_sequencing, rubric_text,
        baseline_norms, few_shot, exclusion, existing_ratings_text, output_schema
    ])


# ==============================================================================
# CORE EVALUATION FUNCTION
# ==============================================================================
def run_delivery_evaluation(narrative_text: str, kb_text: str, existing_ratings: dict = None) -> dict:
    """Run the 25-question delivery method evaluation using GPT-4o.

    Args:
        narrative_text: Extracted text from the nomination fact sheet
        kb_text: Text from the DeliveryMethodComparison PDF
        existing_ratings: Optional dict of district pre-filled ratings {"A1": "B", ...}

    Returns:
        Dict with evaluation results or {"error": "..."} on failure
    """
    system_prompt = _build_system_prompt(kb_text, existing_ratings)

    user_message = f"""Please evaluate the following Alternative Delivery Nomination Fact Sheet against all 25 rubric questions.

NOMINATION FACT SHEET CONTENT:
{narrative_text}"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.0,
        )
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Retry once on malformed JSON
            retry = client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.0,
            )
            return json.loads(retry.choices[0].message.content)
    except Exception as e:
        return {"error": f"AI service error during delivery evaluation: {str(e)}"}


# ==============================================================================
# SCORING MATRIX & DELIVERY METHOD RECOMMENDATION
# ==============================================================================
def compute_delivery_recommendation(ratings: list) -> dict:
    """Apply weighted scoring matrix to 25 A/B/C ratings and recommend a delivery method.

    Args:
        ratings: List of 25 dicts with "question_id" and "selected_rating" keys

    Returns:
        Dict with composite_score, section_scores, recommended_method, etc.
    """
    # Group ratings by section
    section_ratings = {"A": [], "B": [], "C": [], "D": [], "E": [], "F": []}
    rating_lookup = {}
    for r in ratings:
        qid = r.get("question_id", "")
        rating = r.get("selected_rating", "B").upper()
        if qid and qid[0] in section_ratings:
            section_ratings[qid[0]].append(RATING_VALUES.get(rating, 2))
            rating_lookup[qid] = rating

    # Compute section averages
    section_scores = {}
    for section, values in section_ratings.items():
        section_scores[section] = sum(values) / len(values) if values else 2.0

    # Compute weighted composite score
    composite = sum(
        section_scores[s] * SECTION_WEIGHTS[s] for s in SECTION_WEIGHTS
    )

    # Determine recommended method
    recommended, runner_up, is_borderline, comparison = _determine_method(
        composite, section_scores, rating_lookup
    )

    return {
        "composite_score": round(composite, 3),
        "section_scores": {k: round(v, 3) for k, v in section_scores.items()},
        "recommended_method": recommended,
        "runner_up_method": runner_up,
        "is_borderline": is_borderline,
        "comparison_text": comparison,
    }


def _determine_method(composite: float, section_scores: dict, rating_lookup: dict) -> tuple:
    """Determine the delivery method from composite and sub-scores.

    Returns: (recommended, runner_up, is_borderline, comparison_text)
    """
    thresholds = [
        (1.40, "Design-Bid-Build"),
        (1.70, "Design-Sequencing"),
        (2.10, None),  # Sub-score dependent
        (2.50, None),  # Sub-score dependent
        (3.01, "Progressive Design-Build"),
    ]

    # Check borderline (within 0.15 of a threshold boundary)
    is_borderline = False
    for t, _ in thresholds:
        if abs(composite - t) < 0.15:
            is_borderline = True
            break

    # Primary mapping
    if composite <= 1.40:
        recommended = "Design-Bid-Build"
        runner_up = "Design-Sequencing"
    elif composite <= 1.70:
        recommended = "Design-Sequencing"
        runner_up = "Design-Bid-Build" if composite < 1.55 else "CM/GC"
    elif composite <= 2.10:
        recommended, runner_up = _mid_range_method(section_scores, rating_lookup)
    elif composite <= 2.50:
        recommended, runner_up = _upper_range_method(section_scores, rating_lookup)
    else:
        recommended = "Progressive Design-Build"
        runner_up = "CM/GC"

    comparison = ""
    if is_borderline:
        comparison = _build_comparison(recommended, runner_up, composite, section_scores)

    return recommended, runner_up, is_borderline, comparison


def _mid_range_method(section_scores: dict, rating_lookup: dict) -> tuple:
    """Determine method for composite scores 1.71-2.10.

    In this mid-range, CM/GC is the most common recommendation because the
    project is complex enough to benefit from collaboration but not so
    extreme as to require full design-build risk transfer.
    """
    a_avg = section_scores.get("A", 2.0)
    b_avg = section_scores.get("B", 2.0)
    c_avg = section_scores.get("C", 2.0)
    d_avg = section_scores.get("D", 2.0)
    f_avg = section_scores.get("F", 2.0)

    if b_avg >= 2.5 and c_avg >= 2.0:
        # Strong schedule + innovation signals -> Design-Build
        return "Design-Build/Best-Value", "CM/GC"
    if b_avg >= 2.5 and c_avg < 2.0:
        return "Design-Build/Low-Bid", "CM/GC"
    # PDB only if complexity AND scope are both very high in mid-range
    if a_avg >= 2.5 and rating_lookup.get("A3") == "C" and rating_lookup.get("E3") == "C":
        return "Progressive Design-Build", "CM/GC"
    # CM/GC is the default for mid-range — collaborative approach for complex projects
    if c_avg >= 2.0:
        return "CM/GC", "Design-Build/Best-Value"
    return "CM/GC", "Design-Sequencing"


def _upper_range_method(section_scores: dict, rating_lookup: dict) -> tuple:
    """Determine method for composite scores 2.11-2.50."""
    c_avg = section_scores.get("C", 2.0)
    d_avg = section_scores.get("D", 2.0)
    f_avg = section_scores.get("F", 2.0)

    if c_avg < 1.5:
        return "Design-Build/Low-Bid", "CM/GC"
    if c_avg >= 2.0 and d_avg >= 2.0:
        return "Design-Build/Best-Value", "Progressive Design-Build"
    if f_avg >= 2.5:
        return "CM/GC", "Progressive Design-Build"
    if rating_lookup.get("A3") == "C" and rating_lookup.get("E3") == "C":
        return "Progressive Design-Build", "Design-Build/Best-Value"
    return "CM/GC", "Design-Build/Best-Value"


def _build_comparison(recommended: str, runner_up: str, composite: float, section_scores: dict) -> str:
    """Build a qualitative comparison for borderline cases."""
    lines = [
        f"**Borderline Analysis** (Composite Score: {composite:.2f})",
        "",
        f"The scores place this project near the boundary between **{recommended}** and **{runner_up}**.",
        "",
        "**Section Score Breakdown:**",
    ]
    section_names = {
        "A": "Project Scope & Characteristics",
        "B": "Schedule Issues",
        "C": "Opportunity for Innovation",
        "D": "Quality Enhancement",
        "E": "Cost Issues",
        "F": "Staffing Issues",
    }
    for s, name in section_names.items():
        score = section_scores.get(s, 2.0)
        lines.append(f"- {name}: {score:.2f}/3.00 (weight: {SECTION_WEIGHTS[s]:.0%})")

    lines.extend([
        "",
        f"**{recommended}** is recommended as the primary method, but the project team should also evaluate "
        f"**{runner_up}** given the proximity of scores. Consider the specific project constraints, district "
        f"experience with each method, and stakeholder preferences when making the final decision.",
    ])
    return "\n".join(lines)


# ==============================================================================
# EXCEL EXPORT
# ==============================================================================
def build_evaluation_excel(eval_data: dict, recommendation: dict, project_name: str) -> BytesIO:
    """Build a styled Excel workbook with evaluation results."""
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    even_fill = PatternFill("solid", fgColor="EBF3FB")
    border_side = Side(style="thin", color="000000")
    cell_border = Border(left=border_side, right=border_side, top=border_side, bottom=border_side)

    # --- Sheet 1: Evaluation Results ---
    ws1 = wb.create_sheet("Evaluation Results")
    # Title row
    ws1.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
    title_cell = ws1.cell(row=1, column=1, value=f"Delivery Method Evaluation - {project_name}")
    title_cell.font = Font(bold=True, size=13, color="1F4E79")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws1.row_dimensions[1].height = 26

    headers = ["Q#", "Question", "Rating", "Evidence", "Confidence", "Missing Info"]
    for ci, h in enumerate(headers, start=1):
        cell = ws1.cell(row=2, column=ci, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = cell_border
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Column widths
    ws1.column_dimensions["A"].width = 6
    ws1.column_dimensions["B"].width = 50
    ws1.column_dimensions["C"].width = 8
    ws1.column_dimensions["D"].width = 60
    ws1.column_dimensions["E"].width = 12
    ws1.column_dimensions["F"].width = 12

    ratings = eval_data.get("ratings", [])
    for ri, r in enumerate(ratings, start=3):
        fill = even_fill if ri % 2 == 0 else PatternFill()
        values = [
            r.get("question_id", ""),
            r.get("question_text", ""),
            r.get("selected_rating", ""),
            r.get("extracted_evidence", ""),
            round(r.get("confidence", 0), 2),
            "Yes" if r.get("missing_info") else "No",
        ]
        for ci, val in enumerate(values, start=1):
            cell = ws1.cell(row=ri, column=ci, value=val)
            cell.border = cell_border
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if fill.fill_type:
                cell.fill = fill
            # Color-code ratings
            if ci == 3:
                cell.alignment = Alignment(horizontal="center", vertical="top")
                if val == "A":
                    cell.font = Font(bold=True, color="166534")
                elif val == "B":
                    cell.font = Font(bold=True, color="854D0E")
                elif val == "C":
                    cell.font = Font(bold=True, color="991B1B")

    # --- Sheet 2: Recommendation ---
    ws2 = wb.create_sheet("Recommendation")
    ws2.merge_cells(start_row=1, start_column=1, end_row=1, end_column=4)
    title2 = ws2.cell(row=1, column=1, value="Delivery Method Recommendation")
    title2.font = Font(bold=True, size=13, color="1F4E79")
    title2.alignment = Alignment(horizontal="center")
    ws2.row_dimensions[1].height = 26

    # Recommendation summary
    ws2.cell(row=3, column=1, value="Recommended Method:").font = Font(bold=True)
    ws2.cell(row=3, column=2, value=recommendation.get("recommended_method", "")).font = Font(bold=True, size=12, color="1F4E79")
    ws2.cell(row=4, column=1, value="Runner-Up Method:").font = Font(bold=True)
    ws2.cell(row=4, column=2, value=recommendation.get("runner_up_method", ""))
    ws2.cell(row=5, column=1, value="Composite Score:").font = Font(bold=True)
    ws2.cell(row=5, column=2, value=f"{recommendation.get('composite_score', 0):.3f} / 3.000")
    ws2.cell(row=6, column=1, value="Borderline Case:").font = Font(bold=True)
    ws2.cell(row=6, column=2, value="Yes" if recommendation.get("is_borderline") else "No")

    # Section breakdown
    ws2.cell(row=8, column=1, value="Section Score Breakdown").font = Font(bold=True, size=11, color="1F4E79")
    sec_headers = ["Section", "Average Score", "Weight", "Weighted Score"]
    for ci, h in enumerate(sec_headers, start=1):
        cell = ws2.cell(row=9, column=ci, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = cell_border

    section_names = {
        "A": "Project Scope & Characteristics",
        "B": "Schedule Issues",
        "C": "Opportunity for Innovation",
        "D": "Quality Enhancement",
        "E": "Cost Issues",
        "F": "Staffing Issues",
    }
    section_scores = recommendation.get("section_scores", {})
    for ri, (sec, name) in enumerate(section_names.items(), start=10):
        avg = section_scores.get(sec, 2.0)
        weight = SECTION_WEIGHTS[sec]
        fill = even_fill if ri % 2 == 0 else PatternFill()
        for ci, val in enumerate([f"{sec}: {name}", f"{avg:.3f}", f"{weight:.0%}", f"{avg * weight:.3f}"], start=1):
            cell = ws2.cell(row=ri, column=ci, value=val)
            cell.border = cell_border
            if fill.fill_type:
                cell.fill = fill

    ws2.column_dimensions["A"].width = 35
    ws2.column_dimensions["B"].width = 18
    ws2.column_dimensions["C"].width = 12
    ws2.column_dimensions["D"].width = 18

    # --- Sheet 3: Data Completeness ---
    ws3 = wb.create_sheet("Data Completeness")
    ws3.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3)
    title3 = ws3.cell(row=1, column=1, value="Data Completeness Report")
    title3.font = Font(bold=True, size=13, color="1F4E79")
    title3.alignment = Alignment(horizontal="center")

    missing = eval_data.get("missing_questions", [])
    ws3.cell(row=3, column=1, value=f"Questions with Sufficient Evidence:").font = Font(bold=True)
    ws3.cell(row=3, column=2, value=f"{25 - len(missing)} / 25")
    ws3.cell(row=4, column=1, value=f"Questions with Missing Information:").font = Font(bold=True)
    ws3.cell(row=4, column=2, value=f"{len(missing)} / 25")

    if missing:
        ws3.cell(row=6, column=1, value="Missing Information Details").font = Font(bold=True, size=11, color="1F4E79")
        mh = ["Question ID", "Question", "AI Estimate"]
        for ci, h in enumerate(mh, start=1):
            cell = ws3.cell(row=7, column=ci, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.border = cell_border

        ratings_by_id = {r["question_id"]: r for r in ratings}
        for ri, qid in enumerate(missing, start=8):
            r = ratings_by_id.get(qid, {})
            vals = [qid, r.get("question_text", ""), r.get("selected_rating", "")]
            for ci, val in enumerate(vals, start=1):
                cell = ws3.cell(row=ri, column=ci, value=val)
                cell.border = cell_border

    ws3.column_dimensions["A"].width = 15
    ws3.column_dimensions["B"].width = 60
    ws3.column_dimensions["C"].width = 15

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
