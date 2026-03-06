#!/usr/bin/env bash
# ==============================================================
# Start the CUCP MCP Server with ngrok tunnel
# Usage:
#   ./start_mcp.sh                  # SSE on port 8000, no ngrok
#   ./start_mcp.sh --ngrok          # SSE on port 8000 + ngrok
#   ./start_mcp.sh --port 9000 --ngrok --ngrok-token YOUR_TOKEN
# ==============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================="
echo "  CUCP Re-Evaluations — MCP Server Launcher"
echo "============================================="

python -m src.mcp_server "$@"
