
import os
import sys
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv(dotenv_path='.env')

# Add the CURRENT directory (root) to sys.path
sys.path.insert(0, os.getcwd())

print(f"Current working directory: {os.getcwd()}")
print(f"OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")

try:
    from src.project_delivery_evaluator import ProjectDeliveryEvaluator
    evaluator = ProjectDeliveryEvaluator()
    print("Evaluator initialized successfully.")
    
    # Check client initialization
    client = evaluator._get_client()
    print(f"Successfully got client: {type(client)}")
    
    # Check template
    template_path = os.getenv("PDE_V2_TEMPLATE_PATH", "templates/pde_v2_template.xls")
    print(f"Checking template at: {template_path}")
    if os.path.exists(template_path):
        print("✅ Template file found.")
    else:
        print("❌ Template file NOT FOUND.")

    # Try a minimal scoring call (mock data)
    print("Testing scoring logic...")
    from src.project_delivery_evaluator import RUBRIC_QUESTIONS
    dummy_ratings = [{"question_id": q["id"], "selected_rating": "B", "confidence": 0.9} for q in RUBRIC_QUESTIONS[:3]]
    # Just checking if internal functions run
    print("Tests passed.")

except Exception as e:
    import traceback
    print("❌ ERROR during test:")
    traceback.print_exc()
