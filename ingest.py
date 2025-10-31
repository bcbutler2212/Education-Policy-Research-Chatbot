try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
    # Fallback to system sqlite3 if pysqlite3 is not available
    pass

import os
from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings


DOCS_PATH = "docs"
DB_PATH = "db"

def main():
    loader = DirectoryLoader(DOCS_PATH, glob="**/*.csv", loader_cls=CSVLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    db = Chroma(
        embedding_function=embeddings,
        persist_directory=DB_PATH,
        client_settings=Settings(anonymized_telemetry=False)
    )

    batch_size = 10000
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        batch = chunks[start:end]
        db.add_documents(batch)
        print(f"Upserted {min(end, len(chunks))}/{len(chunks)}")

    db.persist()
    print("Saved to disk")









main()