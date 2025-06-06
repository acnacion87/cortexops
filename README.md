# CortexOps
⚠️ This is a proof of concept and is not production-ready. Use at your own risk.

This project is authored by Arjay Nacion and may be freely used or modified by Myridius, provided attribution is retained.

## Description
Smart incident resolution powered by AI

Designed to significantly accelerate and enhance the process of resolving IT incidents. By leveraging existing organizational knowledge from past incidents and documentation, combined with advanced AI reasoning, the system provides IT support teams with rapid, contextually relevant resolution recommendations upon receiving new incident reports.

## How it Works:
The system operates through a combination of scheduled data ingestion and real-time incident processing:

1. **Knowledge Base Creation**: A scheduled Ingest service reads data from ServiceNow (past incidents) and Confluence (documentation). This information is processed and transformed into a searchable format, stored as vector embeddings in a FAISS database, creating a comprehensive knowledge base.
2. **Real-time Incident Notification**: When a new incident is created in ServiceNow, a webhook triggers a FastAPI service. This service immediately publishes a notification about the new incident to a Redis Pub/Sub channel.
3. **User Alerting**: The Chainlit user interface, subscribed to Redis, receives the new incident notification in real-time. It alerts the user to the new incident and provides an option (an "Analyze" button) to initiate the resolution analysis.
4. **AI-Powered Analysis (RAG Chain)**: When the user requests analysis, the RAG Chain component is activated. It queries the FAISS vector database to retrieve the most similar past incidents and relevant documentation chunks. This retrieved context is then provided to a Large Language Model (LLM), hosted by Ollama (using Llama3.2:3b), along with the details of the new incident. The LLM processes this information to generate a recommended resolution.
5. **Resolution Delivery**: The generated resolution is returned by the RAG Chain and displayed to the user within the Chainlit UI.

## Tools
1. Ollama - for running LLMs locally
2. Anaconda - Data Science and AI Distribution Platform
3. LangChain - framework for developing applications powered by large language models (LLMs).
4. Chainlit - an open-source Python library designed to streamline the creation of chatbot applications ready for production.
5. FAISS - stands for Facebook AI Similarity Search, is a library developed by Facebook AI Research. It provides efficient tools for performing similarity search and clustering on large datasets of dense vectors.
6. FastAPI - a modern, high-performance web framework for building APIs with Python.
7. Redis - an open-source, in-memory data structure server, meaning it's primarily used as a database, cache, or message broker. 

## Architecture

```
+----------------+     +----------------+
|    ServiceNow  |     |   Confluence   |
| (Incident Sys) |     | (Documentation)|
+----------------+     +----------------+
        |                      |
        | (Read Incidents)     | (Read Docs)
        v                      v
+----------------------------+
|       Ingest Service       |
| (Scheduled Indexing)       |
+----------------------------+
        |
        | (Index & Store Vectors)
        v
+----------------------------+
|       FAISS Vector DB      |
| (Incident/Doc Embeddings)  |
+----------------------------+


+----------------+     +----------------+
|    ServiceNow  |     |    FastAPI     |
| (New Incident) |<--->|   (Webhook     |
|                |     |   Receiver)    |
+----------------+     +----------------+
        |                      |
        | (Webhook -           | (Publish New
        |  New Incident)       |  Incident)
        v                      v
+----------------------------+
|      Redis Pub/Sub         |
| (Incoming Incident Queue)  |
+----------------------------+
        |
        | (Subscribe & Receive)
        v
+----------------------------+
|        Chainlit UI         |
|    (User Interface)        |
+----------------------------+
        |
        | (User Interaction /
        |  Trigger Analysis)
        v
+----------------------------+
|         RAG Chain          |
|  (Retrieval & Generation)  |
+----------------------------+
        |          ^
        | (Vector  | (Search
        |  Search) |  Results)
        v          |
+----------------+     +----------------+
| FAISS Vector DB|<--->| Ollama (Llama) |
| (Incident/Doc  |     |   (Inference)  |
| Embeddings)    |     +----------------+
+----------------+          ^
        ^                   | (Query /
        |                   |  Resolution)
        +-------------------+

```

**Explanation of Components and Flow:**

1.  **ServiceNow & Confluence:** These are external source systems containing the raw data (incidents and documentation).
2.  **Ingest Service:** This service periodically reads data from ServiceNow and Confluence. It processes this data (e.g., cleaning, chunking) and creates vector embeddings, which are then stored in the FAISS database. This is the offline/scheduled part of the system, building the knowledge base for RAG.
3.  **FAISS Vector DB:** A specialized database optimized for storing and searching vector embeddings. It serves as the knowledge base for the RAG Chain, holding the indexed data from ServiceNow (past incidents) and Confluence (documentation).
4.  **FastAPI Service:** This service acts as the real-time entry point for new incidents. It receives webhooks directly from ServiceNow whenever a new incident is created. Upon receiving a webhook, it processes the notification and publishes a message about the new incident to Redis.
5.  **Redis Pub/Sub:** Redis is used as a message broker. The FastAPI service *publishes* notifications for new incidents to a specific channel. The Chainlit UI *subscribes* to this channel to be instantly notified when a new incident arrives. It also acts as temporary storage for the incoming incident details until Chainlit picks it up.
6.  **Chainlit UI:** The user interface of the system. It maintains a persistent connection (via subscription) to Redis. When it receives a new incident notification, it updates the user interface to inform the user and presents an "Analyze" action. When the user clicks "Analyze", Chainlit orchestrates the resolution process by calling the RAG Chain.
7.  **RAG Chain:** This is the core logic orchestrating the retrieval and generation process.
    *   It takes the new incident details as input.
    *   It queries the **FAISS Vector DB** to find similar past incidents and relevant documentation chunks based on their vector similarity.
    *   It combines the retrieved information (the context) with the new incident details and a prompt for the LLM.
    *   It sends this combined prompt to the **Ollama** service.
8.  **Ollama (Llama3.2:3b):** This service hosts the large language model (Llama3.2:3b). It receives the prompt and context from the RAG Chain and generates a recommended resolution or analysis based on the provided information.
9.  **User:** The end-user interacting with the Chainlit UI to receive notifications and trigger the analysis process.