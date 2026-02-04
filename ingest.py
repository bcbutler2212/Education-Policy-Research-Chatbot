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

from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from chromadb.config import Settings


DOCS_PATH = "docs"
DB_PATH = "db"

def main():
    loader = DirectoryLoader(DOCS_PATH, glob="./*.pdf",loader_cls= PyPDFLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")
       

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100) # change chunk sizes here 
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
     
    # citations 
    for chunk in chunks:
        filename = os.path.basename(chunk.metadata.get("source", ""))
        chunk.metadata["citation"] = filename
    


    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(
        collection_name="new_collection",
        embedding_function=embeddings,
        persist_directory=DB_PATH,
        client_settings=Settings(anonymized_telemetry=False)
    )
    


    batch_size = 500 # 10000 previously 
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        batch = chunks[start:end]
        db.add_documents(batch)
        print(f"Upserted {min(end, len(chunks))}/{len(chunks)}")

    # Chroma persists automatically, but we can verify the collection
    print(f"Total documents in database: {db._collection.count()}")
    print("Saved to disk")









main()
