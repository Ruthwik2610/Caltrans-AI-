import toml
import os

policy_path = os.path.expanduser("~/.gemini/policies/auto-saved.toml")
if os.path.exists(policy_path):
    with open(policy_path, "r") as f:
        config = toml.load(f)
    
    # Example: Relaxing shell command or file writing policies if they exist in the schema
    # Note: The exact schema depends on the gemini-cli version.
    print(f"Current Policy: {config}")
else:
    print("Policy file not found.")
