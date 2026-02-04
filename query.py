'''
import sys
import os

print("--- DEBUG INFO ---")
print(f"Current Working Dir: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print("System Path (in order):")
for p in sys.path:
    print(f"  - {p}")
print("------------------")
# ... your imports
'''
from __future__ import annotations

try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
    # Fallback to system sqlite3 if pysqlite3 is not available
    pass

# Disable chromadb telemetry
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_DISABLED"] = "True"

# from langchain_ollama import ChatOllama
# from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings

# added for claude
#from langchain_anthropic import ChatAnthropic
#from langchain_community.chat_models import ChatAnthropic
#from langchain_classic.embeddings import SentenceTransformerEmbeddings
#from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings

from langchain_core.prompts import PromptTemplate # charlie
from langchain_classic.chains import create_retrieval_chain # charlie
from langchain_classic.chains.combine_documents import create_stuff_documents_chain # charlie


# from langchain.prompts import PromptTemplate
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain


DB_PATH = "db"
# LLM_MODEL = "llama3.1"
# EMBED_MODEL = ""hkunlp/instructor-large"

LLM_MODEL = "claude-sonnet-4-5-20250929"
EMBED_MODEL = "nomic-embed-text"

# ---------------------------------------------------------
# CUSTOM CLAUDE 3 LLM WRAPPER (Python 3.12 compatible)
# ---------------------------------------------------------
import os
import requests




class ClaudeLLM:
    def __init__(self, model, temperature=0.2, max_tokens=1024):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Use your local environment variable automatically
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Missing ANTHROPIC_API_KEY environment variable. "
                "Set it locally before running the script."
            )

    def __call__(self, prompt, **kwargs):
        """Allows LangChain Classic to treat this like an LLM."""
        if hasattr(prompt, "to_string"):
            prompt = prompt.to_string()
        else:
            prompt = str(prompt)
        return self._generate(prompt)

    def _generate(self, prompt):
        url = "https://api.anthropic.com/v1/messages"

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Extract Claude's text response safely
        try:
            return data["content"][0]["text"]
        except Exception:
            return str(data)

def main():
    # Load DB with the same embedding model used during ingest
    db = Chroma(
        collection_name="new_collection",
        persist_directory=DB_PATH,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL), #changed 
        client_settings=Settings(anonymized_telemetry=False)
    )
    # Verify database has documents
    doc_count = db._collection.count()
    print(f"Database contains {doc_count} documents")
    
    if doc_count == 0:
        print("WARNING: Database is empty! Make sure you've run ingest.py first.")
        return

    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}  # Retrieve top 4 most similar documents
    )

    #llm = ChatOllama(model=LLM_MODEL, temperature=0.2) # old model 
    #anthropic model 
    llm = ClaudeLLM(
        model=LLM_MODEL,
        temperature=0.2,
        max_tokens=1024
    )

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=(
            "You are a helpful assistant. Use the provided context to answer the question.\n"
            "If the answer is not in the context, say you don't know.\n\n"
            "Context:\n{context}\n\nQuestion: {input}"
        ),
    )

    document_prompt = PromptTemplate(
        input_var = ["page_content", "citation"], 
        template= "{page_content}\n[Citation: {citation}]"
    )

    document_chain = create_stuff_documents_chain(llm, prompt, document_prompt=document_prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    import sys
   

    print("\nType your questions below. Type 'exit', 'quit', or q to stop.\n")
    while True:
        question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
        question = question.strip()
        if question.lower() in ("exit", "quit", "q"):
            print("goodbye!")
            break
        if not question: 
            continue

        result = rag_chain.invoke({"input": question})

        docs = result.get("context", []) # below prints sources 

        unique_files = set()
        for d in docs:
            citation= d.metadata.get("citation")
            if citation:
                unique_files.add(citation)

        print("\n--- Sources Used ---")
        for filename in sorted(unique_files):
            print(filename)
        print("--------------------\n")

        answer = result.get("answer") or result.get("result") or str(result)
        print("Answer:")
        print(answer)
        print("\n")

if __name__ == "__main__":
    main()
