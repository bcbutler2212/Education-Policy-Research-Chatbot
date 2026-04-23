# Education Policy Research Chatbot

A RAG (Retrieval-Augmented Generation) chatbot designed to help researchers and policy creators analyze education policy documents.

## Prerequisites

Docker allows you to run this application in a consistent environment without manually installing all the dependencies (Python, Node.js, etc.) on your computer.

### 1. Install Docker

*   **Windows & Mac:** Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
*   **Linux:** Follow the [official installation guide](https://docs.docker.com/engine/install/) for your distribution. 

### 2. Install Azure CLI
* Login: run 'az login' in terminal 
* Ensure that you have the following: 
    - A resource group
    - An Azure Container Registry (ACR)


### Step 1: Build & Push Images to ACR
* Authenticate: 
    - 'az acr login --name ACR_NAME_HERE
* Build front and backend images, tag it, push to ACR (you will have to do this multiple times because the source URL needs to be changed once you make the container to call the right location)
    - docker-compose up --build
    - docker tag <local-image>:<tag> ACR_NAME_HERE.azurecr.io/<repository>:<tag>
    - docker push ACR_NAME_HERE.azurecr.io/<repository>:<tag>

### Step 2: Create the Container Apps Environment
This can be done on the Azure website or by running the following 

az containerapp env create \
  --name my-album-env \
  --resource-group <rg> \
  --logs-workspace-id <workspace-id> \
  --logs-workspace-key <workspace-key>

This environment provides networking, logging, and shared infrastructure for all three apps.

### Step 3: Make container apps
* I found the easiest way to do this was through the azure portal --> new resource --> container app
* Make sure that the subscription, resource group, and environment are all accurate
* Name the app
* For ollama container --> 
    - image source should be docker hub
    - image type private
    - Registry login server: docker.io
    - image and tag: ollama/ollama:latest
    - command override: ollama
    - Arguments override: serve
    - CPU and memory:  0.5 CPU cores, 1Gi memory
* For Backend container
    - image source: Azure container registry
    - Registry: ACR_NAME_HERE.azurecr.io
    - Location: East US
    - image: the image you want to use
    - version: the version you want to use 
    - environment variables: 
        - ANTHROPIC_API_KEY=your_key_here
        - COSMOS_ENDPOINT=your_azure_cosmos_endpoint
        - COSMOS_KEY=your_azure_cosmos_key
        - COSMOS_DATABASE=your_db_name
        - COSMOS_CONTAINER=your_container_name
        - OLLAMA_HOST= link provided when you make the ollama container 
* For frontend container
    - image source: Azure container registry
    - Registry: ACR_NAME_HERE.azurecr.io
    - Location: East US
    - image: the image you want to use
    - version: the version you want to use 
    - environment variables: 
        VITE_API_URL = link to backend container 

***The target ports should be as follows***
    - Ollama-server: 11434
    - Backend: 7860
    - Frontend: 5173

***The only container that needs to be open to public is the frontend***

Deploy!!!

### Step 4: pull embedding model
* navigate to the ollama container app
* Go to consola under monitoring
* run command: ollama pull nomic-embed-text

### Step 5: Increase minimum replicas
* navigate to scale under Application 
* change min replicas to 1

It is likely that you will not get it right first try. Make sure that all of the links and ports are correct in your code. Some of the locations of URLs are in dockerfiles, docker-compose, .env, query.py, and vite.config.js