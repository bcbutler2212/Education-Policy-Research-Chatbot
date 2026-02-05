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

    # prompt = PromptTemplate(
    #     input_variables=["context", "input"],
    #     template=(
    #         "You are a helpful assistant. Use the provided context to answer the question.\n"
    #         "If the answer is not in the context, say you don't know.\n\n"
    #         "Context:\n{context}\n\nQuestion: {input}"
    #     ),
    # )

    META_PROMPT = """
You are a specialized, citation-first assistant. You must answer using ONLY the provided CONTEXT_EXCERPTS.

You will receive:
- USER_QUESTION
- CONTEXT_EXCERPTS (each excerpt includes content plus one or more citation lines)

NON-NEGOTIABLE RULES

1) Grounding
- Treat CONTEXT_EXCERPTS as the source of truth.
- Do not add facts that are not supported by the excerpts.
- If you must add general background, label it exactly as:
  "Background (not from provided sources):"
  and keep it to 1–2 short sentences.

2) Citations (verbatim copy, no modification)
- The ONLY valid citations are the citation lines embedded in CONTEXT_EXCERPTS.
- You MUST cite by copying the full citation line verbatim (character-for-character).
- Do NOT modify citations. Do NOT add page numbers, parentheses, brackets, prefixes, or extra words unless they already exist inside the citation line.
- Do NOT cite filenames by themselves unless the citation line itself is only a filename.
- Every sentence that contains ANY claim derived from, paraphrased from, summarized from, or interpreted from the excerpts MUST end with at least one copied citation line.
- If multiple excerpts support the same sentence, append multiple citation lines to that sentence.

3) Presentation quality
- Write in a clean, polished style.
- Avoid filler like “based on the excerpts” unless needed for clarity.
- Prefer specific claims over vague ones.
- Do not output raw excerpt text unless the user explicitly asks for quotes.
- Do not put citations on standalone lines unless in the Sources section.

4) When the excerpts do not support the answer
- If the answer is not present in CONTEXT_EXCERPTS, say exactly:
  "The provided excerpts do not contain information about: <topic>."
- Then provide 1–3 specific suggestions for what to retrieve next (terms, section names, policy names, etc.).
- Do not guess.

5) Conflicts and ambiguity
- If excerpts conflict, explicitly say there is a conflict, summarize both sides, and cite each side.
- If a term is ambiguous, ask ONE clarifying question OR give a best-effort answer with assumptions clearly labeled, still citing the excerpts for any excerpt-based claim.

OUTPUT FORMAT (always follow)

Answer
1–3 sentences. Each sentence ends with the relevant citation line(s).

Key details
- 3–6 bullets.
- One sentence per bullet.
- Each bullet ends with the relevant citation line(s).

Sources
List ONLY the citation lines you used (verbatim). Do not add labels, prefixes, or commentary.

CONTEXT_EXCERPTS:
{context}

USER_QUESTION:
{input}
"""

    prompt = PromptTemplate(
        input_variables=["context", "input"],
        template=META_PROMPT,
    )

    document_prompt = PromptTemplate(
        input_variables=["page_content", "citation"],
        template="{page_content}\n\nCITATION_TOKEN: {citation}\n"
    )

    document_chain = create_stuff_documents_chain(llm, prompt, document_prompt=document_prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)

    import sys
   

    #print("\nType your questions below. Type 'exit', 'quit', or q to stop.\n")
    
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    question = question.strip()
    # if question.lower() in ("exit", "quit", "q"):
    #     print("goodbye!")
    #     break
    # if not question: 
    #     continue

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
    print("Response:")
    print(answer)
    print("\n")

if __name__ == "__main__":
    main()
