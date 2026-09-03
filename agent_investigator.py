# agent_investigator.py
import asyncio
import json
import requests
from google.antigravity import Agent, LocalAgentConfig

# 1. Fetch live investigation payload from local TRACE-X API
TRACEX_API_URL = "http://localhost:8000/api/v1/investigate?address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045"

def get_tracex_data():
    try:
        response = requests.get(TRACEX_API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[!] Error contacting TRACE-X backend: {e}")
        return None

async def main():
    print("Fetching live forensic data from TRACE-X backend...")
    tracex_payload = get_tracex_data()

    if not tracex_payload:
        print("[!] Aborting agent run: Could not retrieve TRACE-X payload.")
        return

    # 2. Formulate task prompt embedded with TRACE-X JSON context
    prompt = f"""
You are a senior Crypto Forensic Analyst working with the TRACE-X System.
Analyze the following multi-hop blockchain investigation JSON payload:

```json
{json.dumps(tracex_payload, indent=2)}