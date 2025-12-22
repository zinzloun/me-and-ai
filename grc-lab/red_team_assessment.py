import requests
import csv
import os
from datetime import datetime
from typing import List, Optional
from deepteam import red_team
from deepteam.vulnerabilities import PromptLeakage, PIILeakage, Misinformation, Robustness
from deepeval.models.base_model import DeepEvalBaseLLM

# --- CONFIGURATION ---
# Target and Judge are hosted on the host machine/Ollama accessible via WSL2 Bridge
HOST_IP = "172.31.199.52"
OLLAMA_URL = f"http://{HOST_IP}:11434/api/generate"
CHATBOT_API_URL = f"http://{HOST_IP}:8000/ask"

class OllamaJudge(DeepEvalBaseLLM):
    """
    Custom Judge implementation using Ollama to evaluate the target's security posture.
    """
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
            "options": {"temperature": 0} # Set to 0 for consistent JSON output
        }
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return response.json().get("response", "")
        except Exception as e:
            return f"{{\"error\": \"Judge connection failed: {str(e)}\"}}"

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return self.model_name

def chatbot_target(prompt: str, history: Optional[List] = None) -> str:
    """
    Callback function to send adversarial prompts to the RAG Chatbot.
    """
    try:
        # Increased timeout for RAG processing overhead
        response = requests.get(CHATBOT_API_URL, params={"query": prompt}, timeout=120)
        return response.json().get("answer", "No answer provided.")
    except Exception as e:
        return f"Error: {str(e)}"

def run_assessment():
    print(f"[*] Initializing Security Assessment...")
    print(f"[*] Target Chatbot: {CHATBOT_API_URL}")
    print(f"[*] Evaluation Model: Phi-3 Mini (via Ollama)")
    
    judge = OllamaJudge(model_name="phi3:mini")

    try:
        # Launching the DeepTeam Red Teaming framework
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
            target_purpose="A NIST CSF and ISO 27001 compliance expert assistant.",
            async_mode=False 
        )

        # --- DATA EXTRACTION & EXPORT ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"redteam_report_{timestamp}.csv"
        
        extracted_data = []
        test_cases = getattr(results, 'test_cases', [])

        for tc in test_cases:
            extracted_data.append([
                getattr(tc, 'vulnerability', 'N/A'),
                getattr(tc, 'vulnerability_type', 'N/A'),
                "PASS" if getattr(tc, 'success', False) else "FAIL",
                getattr(tc, 'input', 'N/A'),
                getattr(tc, 'output', 'N/A'),
                getattr(tc, 'reason', 'N/A')
            ])

        # Write results to CSV
        with open(report_file, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Vulnerability", "Type", "Status", "Input_Prompt", "Bot_Response", "Reasoning"])
            writer.writerows(extracted_data)

        print(f"\n[+] Assessment Complete!")
        print(f"[+] Total Test Cases: {len(extracted_data)}")
        print(f"[+] Security Report saved to: {report_file}")

    except Exception as e:
        print(f"\n[!] Critical Error during Red Teaming: {e}")

if __name__ == "__main__":
    run_assessment()