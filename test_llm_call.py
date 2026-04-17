from databricks.sdk import WorkspaceClient
from openai import OpenAI
import os
from src.project_delivery_evaluator import _get_client

try:
    client = _get_client()
    print("Base URL:", client.base_url)
    
    response = client.chat.completions.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[{"role": "user", "content": "Respond with a clean JSON object containing {"hello": "world"}."}],
    )
    print("Success. Response:", response.choices[0].message.content)
except Exception as e:
    import traceback
    traceback.print_exc()
