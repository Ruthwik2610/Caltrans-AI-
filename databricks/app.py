import os
import sys

import streamlit as st

# ==============================================================================
# ENVIRONMENT SETUP FOR DATABRICKS
# ==============================================================================
# The Databricks app now uses a local `src/` folder containing ONLY project delivery logic.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# The databricks_openai library automatically handles OAuth and endpoints natively via the WorkspaceClient.

# --- Model Config ---
DATABRICKS_MODEL_ENDPOINT = str(os.getenv("DATABRICKS_MODEL_ENDPOINT", "databricks-meta-llama-3-3-70b-instruct"))

# ==============================================================================
# IMPORTS FROM CORE APPLICATION
# ==============================================================================
# Import our proven evaluation logic directly from the traditional app source
from src.project_delivery_evaluator import (
    build_evaluation_excel,
    compute_delivery_recommendation,
    extract_multi_doc_context,
    extract_text_from_docx,
    load_delivery_method_kb,
    run_delivery_evaluation,
    run_validation_analysis,
    score_all_methods,
)

# ==============================================================================
# DATABRICKS STREAMLIT UI
# ==============================================================================
st.set_page_config(
    page_title="Project Delivery Evaluator",
    page_icon="🏗️",
    layout="wide"
)

st.title("Project Delivery Evaluator")
st.markdown("### Caltrans Project Delivery Method Evaluator")
st.write(f"Powered by Databricks Llama 3.3 70B (`{DATABRICKS_MODEL_ENDPOINT}`)")

# We focus purely on the Project Delivery Use Case
st.info("Upload your **Alternative Delivery Nomination Fact Sheet** and any supporting project documents to begin.")

delivery_files = st.file_uploader(
    "Upload Alternative Delivery Documents (DOCX or PDF)", 
    type=["docx", "pdf"], 
    accept_multiple_files=True,
    help="Upload the Nomination Fact Sheet plus any appendices (e.g., Risk Register, Schedule)."
)

# Start Analysis button
if st.button("🚀 Run Project Analysis", disabled=not delivery_files):
    with st.spinner("🔍 Reviewing documents and evaluating all 25 rubric questions..."):
        # 1. Extraction & Pre-check
        try:
            narrative_text = extract_multi_doc_context(delivery_files)
            
            if not narrative_text or len(narrative_text.strip()) < 50:
                st.error("❌ Document extraction failed or returned too little text. Please ensure the documents are readable and not empty.")
                st.stop()
            
            st.session_state.pde_narrative = narrative_text
            
            # Extract existing ratings if any
            existing_ratings = {}
            for f in delivery_files:
                if f.name.endswith(".docx"):
                    f.seek(0)
                    _, extracted_ratings = extract_text_from_docx(f)
                    if extracted_ratings:
                        existing_ratings.update(extracted_ratings)
            st.session_state.pde_existing_ratings = existing_ratings
            
            # 2. Knowledge Base
            kb_text = load_delivery_method_kb()
            
            # 3. Evaluation
            eval_result = run_delivery_evaluation(
                narrative_text,
                kb_text,
                existing_ratings if existing_ratings else None,
                model_name=DATABRICKS_MODEL_ENDPOINT
            )
            
            if "error" in eval_result:
                st.error(eval_result["error"])
            else:
                st.session_state.pde_eval_result = eval_result
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")

# Display Results
if "pde_eval_result" in st.session_state:
    st.divider()
    eval_data = st.session_state.pde_eval_result
    ratings = eval_data.get("ratings", [])
    
    # Get filenames for report
    file_names = sorted([f.name for f in delivery_files]) if delivery_files else ["project"]
    project_name = file_names[0].rsplit(".", 1)[0]
    
    recommendation = compute_delivery_recommendation(ratings)
    multi_method_data = score_all_methods(ratings)
    
    validation_data = None
    if st.session_state.get("pde_existing_ratings"):
        validation_data = run_validation_analysis(
            ratings,
            st.session_state.pde_existing_ratings,
        )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🏆 Recommendation")
        st.info(f"**{recommendation['recommended_method']}**", icon="🎯")
        st.metric("Composite Score", f"{recommendation['composite_score']:.2f}")

    with col2:
        st.markdown("### 📝 Analysis Summary")
        st.write(eval_data.get("summary", "No summary provided."))

    # Download Report
    excel_buf = build_evaluation_excel(
        eval_data=eval_data,
        recommendation=recommendation,
        project_name=project_name,
        multi_method_data=multi_method_data,
        validation_data=validation_data,
    )
    st.download_button(
        label="Download Complete Excel Report",
        data=excel_buf,
        file_name=f"Evaluation_{project_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )
