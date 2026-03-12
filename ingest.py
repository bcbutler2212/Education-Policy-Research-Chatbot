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

from azure.cosmos import CosmosClient, PartitionKey
import uuid

# add cosmos info below 
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "rag-db")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "chunks")

if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise ValueError("Cosmos DB credentials not set in environment variables.")

# initializing cosmos below 
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

database = client.create_database_if_not_exists(id=DATABASE_NAME)

container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/source"),
    offer_throughput=400
)


def strip_header_lines(text: str, page_number: str): 
    if page_number != '1':
        lines = text.split("\n")
        cleaned = []
        removed = 0

        for line in lines:
            if removed < 2 and line.strip() != "":
                removed += 1
                continue
            cleaned.append(line)

        return "\n".join(cleaned)


    lower_text = text.lower()
    intro_index = lower_text.find("introduction")

    # If "introduction" isn't found, return the text unchanged
    if intro_index == -1:
        return text

    # Keep everything starting from the word "Introduction"
    return text[intro_index:]



DOCS_PATH = "docs"


def main():
    loader = DirectoryLoader(DOCS_PATH, glob="./*.pdf",loader_cls= PyPDFLoader)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    for doc in documents:
        page_number = doc.metadata.get("page_label", None)

        doc.page_content = strip_header_lines(
            doc.page_content,
            page_number=page_number
        )
        
   


    custom_separators = [
        ". ",
        "? ",
        "! ",
    ]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=120,
        separators=custom_separators,
        keep_separator=False
        )
    
    
    chunks = text_splitter.split_documents(documents)
    

    print(f"Split into {len(chunks)} chunks")

    # citations 
    for chunk in chunks:
        filename = os.path.basename(chunk.metadata.get("source", ""))
        chunk.metadata["citation"] = filename
    
   

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    
    # new db here ***
    # db = Chroma(
    #     collection_name="new_collection",
    #     embedding_function=embeddings,
    #     persist_directory=DB_PATH,
    #     client_settings=Settings(anonymized_telemetry=False)
    # )
    batch_size = 128 # 10000 previously 

    # cosmos db below 


    


   
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        batch = chunks[start:end]
        # Change me below *** perhaps ??? look at documentation 
        #db.add_documents(batch)
        for chunk in batch:
            embedding = embeddings.embed_query(chunk.page_content)

            # this format needed for cosmos db 
            item = {
            "id": str(uuid.uuid4()), # unsure if I should change ids to include metadata info for citations 
            "content": chunk.page_content,
            "embedding": embedding,
            "source": chunk.metadata.get("source"),
            "citation": chunk.metadata.get("citation"),
            "page": chunk.metadata.get("page_label")
                }
            container.upsert_item(item) #overwrites

        print(f"Upserted {min(end, len(chunks))}/{len(chunks)}")
    
  

    # for i, chunk in enumerate(chunks[:10]):
    #     print(f"\n--- Chunk {i+1} ---")
    #     print(chunk.page_content)
    #     print("-------------------")





main()
