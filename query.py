try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ModuleNotFoundError:
    # Fallback to system sqlite3 if pysqlite3 is not available
    pass


from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


DB_PATH = "db"
LLM_MODEL = "mistral"
EMBED_MODEL = "nomic-embed-text"

def main():
    # Load DB with the same embedding model used during ingest
    db = Chroma(
        persist_directory=DB_PATH,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL),
        client_settings=Settings(anonymized_telemetry=False)
    )
    retriever = db.as_retriever()

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