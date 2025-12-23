import requests
import csv
import json
import os
from datetime import datetime
from typing import List, Optional
from deepteam import red_team
from deepteam.vulnerabilities import PromptLeakage, PIILeakage, Misinformation, Robustness
from deepeval.models.base_model import DeepEvalBaseLLM

# --- CONFIGURATION ---
# Target and Judge are hosted on the host machine via WSL2 Bridge
HOST_IP = "172.31.192.1" 
OLLAMA_URL = f"http://{HOST_IP}:11434/api/generate"
CHATBOT_API_URL = f"http://{HOST_IP}:8000/ask"

class OllamaJudge(DeepEvalBaseLLM):
    
    # Custom Judge implementation using Ollama. 
    # Includes a cleanup layer to handle 'Invalid JSON' errors from small models.
    
    def __init__(self, model_name):
        self.model_name = model_name

    def load_model(self):
        return self.model_name

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_ctx": 4096
            }
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=180)
            raw_output = response.json().get("response", "")
            
            # Basic cleanup: ensuring the output starts and ends with curly braces
            if "{" in raw_output and "}" in raw_output:
                return raw_output[raw_output.find("{"):raw_output.rfind("}")+1]
            return raw_output
        except Exception as e:
            return f"{{\"error\": \"Judge connection failed: {str(e)}\"}}"

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return self.model_name

def chatbot_target(prompt: str, history: Optional[List] = None) -> str:
    
    # Callback function to send adversarial prompts to the target RAG Chatbot.
    
    try:
        response = requests.get(CHATBOT_API_URL, params={"query": prompt}, timeout=180)
        return response.json().get("answer", "No answer provided.")
    except Exception as e:
        return f"Error: {str(e)}"

def run_assessment():
    print(f"[*] Starting AI Security Lab...")
    print(f"[*] Host IP: {HOST_IP}")
    
    # Using Phi-3 Mini as the security judge
    judge = OllamaJudge(model_name="phi3:mini")

    try:
        results = red_team(
            model_callback=chatbot_target,
            simulator_model=judge,
            evaluation_model=judge,
            vulnerabilities=[
                PromptLeakage(),
                PIILeakage(),
                Misinformation(),
                Robustness()
            ],
            attacks_per_vulnerability_type=2,
            target_purpose="NIST CSF and ISO 27001 compliance advisor.",
            async_mode=False
        )

        # --- EXPORT TO CSV ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"security_report_{timestamp}.csv"

        # --- UPDATED DATA EXTRACTION ---
        extracted_data = []
        test_cases = getattr(results, 'test_cases', [])
        
        for tc in test_cases:
            # DeepEval/DeepTeam convention:
            # Score 1 = The bot stayed safe (PASS)
            # Score 0 = The bot was exploited (FAIL)
            score = getattr(tc, 'score', 0)
            status_label = "PASS" if score == 1 else "FAIL"
        
            extracted_data.append([
                getattr(tc, 'vulnerability', 'N/A'),
                getattr(tc, 'vulnerability_type', 'N/A'),
                status_label,  # This will match the screen output!
                getattr(tc, 'input', 'N/A'),
                getattr(tc, 'output', 'N/A'),
                getattr(tc, 'reason', 'N/A')
            ])

        with open(report_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Vulnerability", "Type", "Status", "Input", "Response", "Reasoning"])
            writer.writerows(extracted_data)

        print(f"\n[+] Assessment Completed Successfully.")
        print(f"[+] Results saved to: {report_file}")

    except Exception as e:
        print(f"\n[!] Fatal error during execution: {e}")

if __name__ == "__main__":
    run_assessment()
