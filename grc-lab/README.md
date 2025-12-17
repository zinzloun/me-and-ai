# 🛡️ Local GRC-LLM Lab

A private, high-performance **Retrieval-Augmented Generation (RAG)** laboratory designed for GRC (Governance, Risk, and Compliance) analysts.
This lab allows you to query framework documents (NIST CSF 2.0, SP 800-53, ISO Mappings) locally using your GPU.

## 🚀 Overview
The system indexes PDF documents from a local folder into a **FAISS** vector database. 
When a user asks a question, the system retrieves the most relevant technical "chunks" and uses **Llama 3.2 3B** to generate an audit-ready answer with source citations.

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

### Hardware
* **GPU:** NVIDIA GeForce RTX 4050 Laptop (6GB VRAM) or better.
* **Storage:** ~10GB for Docker images and LLM models.
* **OS:** Windows 10/11 with WSL2 or Linux.

### Software
* **[Ollama](https://ollama.com/):** Running natively on the host machine.
* **Docker & Docker Compose:** To orchestrate the API.
* **Python 3.10+** (Optional, for utility scripts like wiping the DB).

---

## ⚙️ Configuration

### 1. Ollama Setup (Host)
Ensure Ollama is accessible by the Docker containers:
1. Set the environment variable: `OLLAMA_HOST=0.0.0.0`
2. Pull the required models:
   ```powershell
   ollama pull llama3.2:3b
   ollama pull nomic-embed-text
   
## 🚀 Getting Started
1. Place NIST/ISO PDFs in the `./data` folder.
2. Start the lab:
   ```bash
   docker compose up --build -d

Open http://localhost:8000/docs to get started.
