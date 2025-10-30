__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


from langchain_ollama import ChatOllama
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


DB_PATH = "db"
LLM_MODEL = "mistral"

def main():
    db = Chroma(persist_directory=DB_PATH, embedding_function=OllamaEmbeddings(model=LLM_MODEL))
    retriever = db.as_retriever()
    return ChatOllama(model=LLM_MODEL, temperature=0.7, llm=retriever)

    prompt = PromptTemplate(
        template="""
        You are a helpful assistant that can answer questions about the following text:
        {text}
        """
    )
    document_chain = create_stuff_documents_chain(llm, prompt)