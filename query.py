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
from azure.cosmos import CosmosClient


from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from typing import Any
import asyncio
import textwrap



# add cosmos info below 
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER")

if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise ValueError("Cosmos DB credentials not set in environment variables.")

def get_cosmos_container():
    # Connects to Cosmos DB and returns container client.
    
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    return container

#DB_PATH = "db"


LLM_MODEL = "claude-sonnet-4-5-20250929"
EMBED_MODEL = "nomic-embed-text"

import os
import requests


class CosmosVectorRetriever(BaseRetriever):
    """
    - Embeds query using Ollama
    - Uses Cosmos VectorDistance search
    - Returns LangChain Documents
    """

    # Declare fields so Pydantic allows them
    container: any = Field(...)
    embed_model: any = Field(...)
    k: int = Field(default=8)

   # trying to get rid of warning 
    model_config = {
        "arbitrary_types_allowed": True
    }

    # this one works below 
    def __init__(self, container, embed_model, k: int = 4, **kwargs):
        # Pass fields to Pydantic BaseModel
        super().__init__(container=container, 
                         embed_model=embed_model,
                        k=k,
                        **kwargs)

    def _get_relevant_documents(self, query: str): # required by baseretriever 
        return self.get_relevant_documents(query)

    def get_relevant_documents(self, query: str):
        # Embed user query
        query_embedding = self.embed_model.embed_query(query)

        # Run Cosmos vector similarity search
        results = self.container.query_items(
            query="""
            SELECT TOP @k c.id, c.content, c.citation, c.source
            FROM c
            ORDER BY VectorDistance(c.embedding, @vector)
            """,
            parameters=[
                {"name": "@k", "value": self.k},
                {"name": "@vector", "value": query_embedding}
            ],
            enable_cross_partition_query=True
        )

        # Convert results to LangChain Documents
        documents = []
        for item in results:
            documents.append(
                Document(
                    page_content=item["content"],
                    metadata={
                        "citation": item.get("citation"),
                        "source": item.get("source", "")                    }
                )
            )
        return documents
    
async def aget_relevant_documents(self, query: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_relevant_documents, query)

class ClaudeLLM: # claude wrapper 
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
    container = get_cosmos_container() # get cosmos container 
    
    embedding_model = OllamaEmbeddings(model=EMBED_MODEL)

    # use cosmos retriever
    retriever = CosmosVectorRetriever(
        container=container,
        embed_model=embedding_model,
        k=5 # changed k value from 4 to 8
    )


    #anthropic model 
    llm = ClaudeLLM(
        model=LLM_MODEL,
        temperature=0.2,
        max_tokens=1024
    )

    '''
    **************************
    IMPORTANT NOTE FROM SOFIA:
    all edits should only be made below. The output of the chatbot is a little buggy and hard to follow. 

    SOme suggestions: 
    - The answer should be the main point, not sure that the bullets that follow are easy to interpret
    - ALso the citations given at the bottom are incorrect
    - We need to figure out how to cite correctly and point to the chunks that were used and where those are located
    - metaprompt is good but could use some edits 

    *************************
    '''
        # play with the metaprompt with new database and model !!!! 

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=(
          """You are a policy research assistant that answers questions using ONLY the provided CONTEXT_EXCERPTS.
          Your purpose is to help researchers and policy creators understand infromation contained in the excerpts.

            Your goals:
            - Give a clear, helpful answer grounded in the excerpts.
            - Synthesize across multiple excerpts when relevant.
            - Prefer precise wording from the excerpts when possible.
            - Be concise, accurate, and easy to read.


            Rules:
            - Do not introduce facts that are not supported by the excerpts.
            - Do not reference quotes not found in CONTEXT_EXCERPTS.
            - If the excerpts do not contain enough information, explicitly say so.
            - If excerpts conflict, briefly describe the conflict and reflect both sides.

            Handling missing information:
            If the excerpts do not contain enough information, respond with:

            "The provided excerpts do not contain sufficient information about: <topic>."

            Then suggest 1–3 specific additional queries, keywords, or document types that may help answer the question.

        


            Output format (always follow):


            Response
            No more than 6 sentences answering the question directly. 


            Key details
            - 2-4 short bullets that support or expand the response.
            - Use quotations from CONTEXT_EXCERPTS when useful, do not paraphrase these quotations
            - Each bullet should reference the relevant excerpt number and the filename of that excerpt if available.



            CONTEXT_EXCERPTS:
            {context}


            USER_QUESTION:
            {input}

            """
        ),
    )

    document_prompt = PromptTemplate(
        input_variables = ["page_content", "citation"], 
        template= "{page_content}\n"
        "[Source: {citation}]"
    )

    document_chain = create_stuff_documents_chain(llm, prompt, document_prompt=document_prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain) # not changed 

    import sys

    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    question = question.strip()

    result = rag_chain.invoke({"input": question})

    docs = result.get("context", []) # below prints sources 

    unique_files = set()
   
    # ** Print chunks for testing below **
    """ 
    print("\n--- Retrieved Chunks---") # citation and chunks
    for i, d in enumerate(docs, start=1):

        citation= d.metadata.get("citation")
        if citation:
            unique_files.add(citation)

        source_path = d.metadata.get("source", "")
        filename = os.path.basename(source_path)

        print(f"\nChunk {i}:")
        print(f"File: {filename}")
        print("Content:")
        #print(d.page_content)
        print(textwrap.fill(d.page_content, width=100))
        print("-" * 40)
    print("------------------------\n") """

    for i, d in enumerate(docs, start=1):

        citation= d.metadata.get("citation")
        if citation:
            unique_files.add(citation)

        source_path = d.metadata.get("source", "")
        filename = os.path.basename(source_path)
        
    print("\n--- Sources Used ---")
    for filename in sorted(unique_files):
        print(filename)
        print()
    print("--------------------\n")

    answer = result.get("answer") or result.get("result") or str(result)
    print("Answer:")
    #print(answer)
    for p in answer.split("\n"):
        print(textwrap.fill(p, width=100))
    print("\n")

if __name__ == "__main__":
    main()
