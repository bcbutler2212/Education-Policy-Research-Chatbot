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

from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


DB_PATH = "db"
LLM_MODEL = "llama3.1"
EMBED_MODEL = "nomic-embed-text"

def main():
    # Load DB with the same embedding model used during ingest
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL),
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

    llm = ChatOllama(model=LLM_MODEL, temperature=0.2)

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=(
            "You are a helpful assistant. Use the provided context to answer the question.\n"
            "If the answer is not in the context, say you don't know.\n\n"
            "Context:\n{context}\n\nQuestion: {input}"
        ),
    )
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    import sys
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    result = rag_chain.invoke({"input": question})
    answer = result.get("answer") or result.get("result") or str(result)
    print(answer)

if __name__ == "__main__":
    main()
