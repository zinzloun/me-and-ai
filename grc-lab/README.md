# 🤖 Local GRC-LLM Lab

A private, high-performance **Retrieval-Augmented Generation (RAG)** laboratory designed for GRC (Governance, Risk, and Compliance) analysts.
This lab allows you to query framework documents (NIST CSF 2.0, SP 800-53, ISO Mappings) locally using your GPU.

## 🛡️ Overview
The system indexes PDF documents from a local folder into a **FAISS** vector database. 
When a user asks a question, the system retrieves the most relevant technical "chunks" and uses **Llama 3.2 3B** to generate an audit-ready answer with source citations.
At the monent the only available endpoint is API.

## Project Structure
```text
grc-lab/
├── app/
│   ├── main.py          # FastAPI Backend with RAG Logic
├── data/
│   ├── *.pdf            # NIST/ISO framework documents
│   └── vectorstore/     # FAISS database (auto-generated)
├── docker-compose.yaml  # Docker orchestration
└── README.md            # Documentation
```
---

## 📋 Requirements
This lab has been created on Windows 11 with WSL2, so I assume that Docker Desktop is also used

### Hardware
* **GPU:** NVIDIA GeForce RTX 4050 Laptop (6GB VRAM) or better.
* **Storage:** ~10GB for Docker images and LLM models.
* **OS:** Windows 10/11 with WSL2 or Linux.

### Software
* **[Ollama](https://ollama.com/):** Running natively on the my host machine.
* **Docker & Docker Compose:** To orchestrate the API and FAISS.
---

## ⚙️ Configuration

### 1. Ollama Setup (Host)
Ensure Ollama is accessible by the Docker containers:
1. Set the environment variable:
```
set OLLAMA_HOST=0.0.0.0
```
1. Start the server
```
ollama serve
```
3. Open another prompt and pull the required models (takes log time but you need just do it once):
```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
ollama pull phi3:mini
```
4. Check Ollama is running: http://localhost:11434
## 🚀 Getting Started
1.Clone or download this repo
2. Eventually place other relevant PDFs in the `./data` folder (at the moment only PDF file are supported)
3. Start Docker
4. Start the lab:
```
docker compose up --build -d
```
4. Start grc-api container
```
docker start grc-api
```
Wait 5 minutes to allow building indexes, then open http://localhost:8000/docs to get started.

## Appendix: useful commands
### Ollama
```
#list model
ollama list

#list process
ollama ps
```

# LLM Red Teaming Lab: NIST & ISO 27001 RAG Security

This repository contains an automated Red Teaming laboratory designed to evaluate the security posture of an AI Chatbot specialized in **NIST CSF** and **ISO 27001** compliance. 

The lab simulates adversarial attacks to identify vulnerabilities in a Retrieval-Augmented Generation (RAG) system, focusing on data privacy and technical robustness.

## 🏗️ Architecture

- **Target Model:** Llama 3.2 (3B) - Serving as a RAG-based Compliance Expert.
- **Judge/Attacker Model:** Phi-3 Mini - Used as the "Adversarial Simulator" and "Security Evaluator".
- **Environment:**
	- **Networking** WSL Hyper-V
	- **Host:** Windows 11 with Ollama - GPU Accelerated - RTX 4050 (IP: `172.31.192.1`).
    - **Attack VM:** Kali Linux running on **WSL2** (IP: `172.31.199.52`).
- **Framework:** [DeepTeam](https://github.com/confident-ai/deepteam) for LLM Red Teaming.



## 🛡️ Vulnerabilities Tested

The assessment covers 13 types of vulnerabilities across 4 core domains:
1. **Prompt Leakage:** Attempts to extract system instructions or internal guardrails.
2. **PII Leakage:** Probing the RAG database for sensitive personal identifiable information (e.g., employee records).
3. **Misinformation:** Checking if the model hallucinates or provides unsupported claims about ISO/NIST standards.
4. **Robustness:** Testing the model's resistance to conversation hijacking and input overreliance.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Ollama (running on host machine at `172.31.199.52:11434`)
- Chatbot API (running on port `8000`)

### Installation & Virtual Environment Setup
Clone the repository and set up the Python virtual environment:

```bash
# Create the virtual environment
python3 -m venv venvDT

# Activate the environment
source venvDT/bin/activate

# Install dependencies
pip install --upgrade pip
pip install requests deepteam deepeval

```
### Run the test script
```bash
cd venvDT
wget 
