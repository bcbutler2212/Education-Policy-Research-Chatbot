# test usert for db
from azure.cosmos import CosmosClient, PartitionKey
import uuid
import os

# add cosmos info below 
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE", "rag-db")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "chunks")

if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise ValueError("Cosmos DB credentials not set in environment variables.")


# test below 
from langchain_ollama import OllamaEmbeddings
import uuid

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vector = embeddings.embed_query("this is a test item")

# initializing cosmos below 
client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)


database = client.create_database_if_not_exists(id=DATABASE_NAME)


#databases = print(list(client.list_databases()))

#print("Connected successfully!")

container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/source"),
    offer_throughput=400
)

item = {
    "id": str(uuid.uuid4()),
    "content": "this is another test item before running injest",
    "embedding": vector,
    "source": "test_source",
    "citation": "test source",
    "page": 1
}

container.upsert_item(item) 

print("\nFetching items from Cosmos DB:\n")

query = "SELECT * FROM c"

items = container.query_items(
    query=query,
    enable_cross_partition_query=True
)

for item in items:
    print("ID:", item["id"])
    print("Content:", item["content"])
    print("Source:", item["source"])
    print("Page:", item["page"])
    print("-" * 40)