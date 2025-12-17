import os
import shutil
from fastapi import FastAPI
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

app = FastAPI()

# --- CONFIGURATION ---
DATA_PATH = "/data"
DB_FAISS_PATH = "/data/vectorstore"
OLLAMA_BASE_URL = "http://host.docker.internal:11434"

# Models optimized for RTX 4050 (6GB VRAM)
embeddings = OllamaEmbeddings(
    model="nomic-embed-text", 
    base_url=OLLAMA_BASE_URL
)

llm = ChatOllama(
    model="llama3.2:3b", 
    base_url=OLLAMA_BASE_URL,
    num_gpu=99,
    temperature=0,
    keep_alive="5m" # Stays in GPU for 5 mins after use
)

# --- CORE LOGIC ---

def create_or_load_vectorstore():
    """Initializes the vector database by reading PDFs or loading existing FAISS index."""
    if os.path.exists(DB_FAISS_PATH):
        print("Loading existing vectorstore...")
        return FAISS.load_local(
            DB_FAISS_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    
    print("Indexing documents... this might take a minute.")
    loader = DirectoryLoader(DATA_PATH, glob="./*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()
    
    # Larger chunks (1200) and overlap (300) to keep GRC concepts together
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200, 
        chunk_overlap=300
    )
    splits = text_splitter.split_documents(docs)
    
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
    vectorstore.save_local(DB_FAISS_PATH)
    return vectorstore

# Initialize Vectorstore and Retriever
vectorstore = create_or_load_vectorstore()
# k=7 allows the model to see more parts of the NIST framework at once
retriever = vectorstore.as_retriever(search_kwargs={"k": 7})

# --- RAG CHAIN DEFINITION ---

template = """You are a GRC Expert assistant. Use the following context from the uploaded documents to answer the question. 
If the information is not explicitly in the context, use the context as a guide and explain the relationship based on NIST principles.

Context:
{context}

Question: {question}

Helpful Answer in English:"""

prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# --- API ENDPOINTS ---

@app.get("/ask")
async def ask_grc(query: str):
    """Query the GRC documents and return the answer with sources."""
    # 1. Retrieve the source documents for citation
    source_docs = retriever.invoke(query)
    
    # 2. Generate the answer
    answer = rag_chain.invoke(query)
    
    # 3. Format sources (File Name + Page Number)
    sources = []
    for doc in source_docs:
        file_name = os.path.basename(doc.metadata.get('source', 'Unknown'))
        page_num = doc.metadata.get('page', 'N/A')
        # Increment page by 1 because PyPDFLoader starts at 0
        if isinstance(page_num, int):
            page_num += 1
        sources.append(f"{file_name} (Page {page_num})")
    
    return {
        "question": query, 
        "answer": answer,
        "sources": list(set(sources)) # Unique list
    }

@app.post("/reload")
async def reload_documents():
    """Wipes the database and re-indexes all documents in /data."""
    global vectorstore, retriever
    if os.path.exists(DB_FAISS_PATH):
        shutil.rmtree(DB_FAISS_PATH)
    
    vectorstore = create_or_load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 7})
    
    return {"status": "Database re-indexed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)