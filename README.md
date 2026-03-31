# Education Policy Research Chatbot

A RAG (Retrieval-Augmented Generation) chatbot designed to help researchers and policy creators analyze education policy documents.

## 🚀 Getting Started with Docker

Docker allows you to run this application in a consistent environment without manually installing all the dependencies (Python, Node.js, etc.) on your computer.

### 1. Install Docker

*   **Windows & Mac:** Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
*   **Linux:** Follow the [official installation guide](https://docs.docker.com/engine/install/) for your distribution. 

### 2. Prepare the Environment

1.  **Ollama (for Embeddings):** 
    This app uses Ollama for text embeddings. You must have Ollama installed and running on your host machine.
    *   Install from [ollama.com](https://ollama.com).
    *   **Crucial:** Start Ollama so it is accessible from Docker by running:
        ```bash
        OLLAMA_HOST=0.0.0.0 ollama serve
        ```
    *   Ensure the `nomic-embed-text` model is pulled:
        ```bash
        ollama pull nomic-embed-text
        ```

2.  **Configuration:**
    Create a `.env` file in the root directory with the following keys:
    ```env
    ANTHROPIC_API_KEY=your_key_here
    COSMOS_ENDPOINT=your_azure_cosmos_endpoint
    COSMOS_KEY=your_azure_cosmos_key
    COSMOS_DATABASE=your_db_name
    COSMOS_CONTAINER=your_container_name
    ```

### 3. Run the Application

Navigate to the project folder in your terminal and run:

```bash
docker-compose up --build
```

*   **Backend:** Accessible at `http://localhost:7860`
*   **Frontend:** Accessible at `http://localhost:5173`

To stop the application, press `Ctrl+C` in the terminal or run `docker-compose down`.

## 🛠 Project Structure

- `UI.py`: Flask backend providing the `/chat` and `/health` endpoints.
- `query.py`: Core RAG logic using LangChain, Claude (Anthropic), and Cosmos DB.
- `ingest.py`: Script to process PDFs from the `docs/` folder into the vector database.
- `frontend/`: Vite + React application for the user interface.

## 📝 Ingesting Documents

If the database is empty or you've added new PDFs to the `docs/` folder, run the ingestion script inside the container:

```bash
docker-compose exec app python ingest.py
```
