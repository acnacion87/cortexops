# DRAFT 1
Presented June 06, 2025

Draft 1 focuses on building the main components of the system and generating synthetic data for Service Now incidents and Confluence documentations.

As we don't have access to live Service Now and Confluence instance containing large data, in order to come up with a POC, we will generate synthetic data to test against with.

## Components for Draft 1
1. Synthetic Data Ingestion and Indexing to FAISS Vector Database
2. FastAPI endpoint to handle webhook call and publish to Redis
3. Chainlit UI containing the basic functionality of reading new incident from Redis - polling for now but will be updated to pub-sub on **DRAFT 2**. Informing user when a incident is raised and provide option to Analyze. Executes the fixed RAG Chain to generate recommended resolution.
4. Fixed RAG Chain where past incidents and related documents are searched provided with the prompt to LLM
5. Ollama (using Llama3.2:3b) for local testing using a lightweight model.

## Updates after June 06 presentation
1. Regenerated synthetic incidents and documentations using OpenAI gpt-3.5-turbo model.
2. Pushed synthetic incidents and documentations datasets to HuggingFace Hub
3. Rebuilt FAISS index using the new datasets
4. Refactored prompts.
5. Implemented callback handler to log events during RAG Chain processing.
6. Fixed query provided to the chain during invocation to match the same query used with instructor embedding

# DRAFT 2
Planned for June 25, 2025

Draft 2 will focuse on building making the solution more agentic to improve reasoning and decision-making.


## Components Improvement
1. Synthetic Data Ingestion and Indexing to FAISS Vector Database - Maybe replaced with Chroma for rich metadata filtering. Generate more synthetic data, currently using prompt-based Ollama API queries but maybe replaced with Distilabel pipelines.
2. FastAPI endpoint to handle webhook call and publish to Redis - replace implementation to publish to a Redis channel instead of just adding new incident to a list
3. Chainlit UI - Replace the polling mechanism with a subscription to a Redis Channel
4. Fixed RAG Chain - replace fixed RAG chain with LangChain's AgentExecutor to use an agent that can decide whether to search incidents or docs or both, whether to escalate or retry, whether to respond immediately or ask the user a follow-up.
5. Ollama (using Llama3.2:3b) for local testing using a lightweight model.

# Potential Improvements for DRAFT2 or DRAFT 3
1. Memory or Context Awareness - track past steps, chain reasoning across actions, store questions and responses
2. Multi-Step Reasoning
3. Dynamic Planning - Chooses to search docs only if incident data is weak
4. Feedback or Self-Critique Loop (e.g. Let the model double check it's answer)
5. Multi-hop retrieval - Agent fetches info in multiple steps to support resolution
6. Context Accumuluation - Agent tracks partial evidence and builds a final answer
7. Replace local-based Ollama with Cloud-based models (e.g. OpenAI GPT4, Calude3 Sonnet etc.)