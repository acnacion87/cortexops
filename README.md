# CortexOps
⚠️ This is a proof of concept and is not production-ready. Use at your own risk.

This project is authored by Arjay Nacion and may be freely used or modified by Myridius, provided attribution is retained.

- [CortexOps](#cortexops)
  - [Description](#description)
  - [How it Works](#how-it-works)
  - [Tools](#tools)
  - [Architecture](#architecture)
  - [Monitoring and Evaluation](#monitoring-and-evaluation)
  - [Current Limitations](#current-limitations)
  - [Future Enhancements](#future-enhancements)

## Description
Smart incident resolution powered by AI, using synthetic data for demonstration purposes. The system provides IT support teams with rapid, contextually relevant resolution recommendations for new incident reports by leveraging AI-generated knowledge from past incidents and documentation.

## How it Works
1. **Synthetic Data Generation**: Using SDV (Synthetic Data Vault) to generate realistic synthetic incidents and documentation:
   - ServiceNow incidents with descriptions, categories, and resolutions
   - ServiceNow Knowledge Base articles with troubleshooting guides and best practices
   - Data represents common and edge-case scenarios in Merchant Onboarding

2. **Knowledge Base**: Vector embeddings stored in FAISS database for semantic search

3. **Incident Processing**: HTTP POST endpoint receives new incidents for analysis

4. **AI-Powered Analysis**: Agent-based system with OpenAI (gpt-4o-mini) for inference and feedback:
   - Validates query relevance to Merchant Onboarding System
   - Uses tools to search incidents and knowledge base
   - Generates resolution recommendations with conversation memory
   - Real-time streaming via Chainlit UI

## Tools
- OpenAI (gpt-4o-mini) - LLM for inference and feedback
- SDV - Synthetic data generation
- LangChain - LLM application framework
- Chainlit - Chatbot UI framework
- FAISS - Vector similarity search
- FastAPI - API framework
- Redis - Message broker
- TruLens - LLM application monitoring and evaluation

## Architecture

```mermaid
graph TB
    %% External Systems
    SDV[SDV<br/>Data Generation]
    
    %% Data Processing
    Ingest[Ingest Script<br/>Vector Embedding Creation]
    
    %% Storage
    FAISS[(FAISS Vector DB<br/>Incident/Doc Embeddings)]
    Redis[(Redis<br/>Message Broker)]
    
    %% User Interface
    Chainlit[Chainlit UI<br/>User Interface]
    
    %% AI Components
    Agent[Agent<br/>Query Validation & Tools]
    Tools[Tools<br/>Search & Validation]
    OpenAI[OpenAI<br/>gpt-4o-mini Model]
    TruLens[TruLens<br/>Monitoring & Evaluation]
    
    %% User
    User((User))
    
    %% Connections
    SDV -->|Generate Data| Ingest
    Ingest -->|Store Vectors| FAISS
    FAISS -->|Vector Search| Tools
    Chainlit -->|User Interaction| Agent
    Agent -->|Use Tools| Tools
    Agent -->|Validate Query| OpenAI
    Tools -->|Search Knowledge| FAISS
    OpenAI -->|Search Results| FAISS
    User -->|Submit/Analyze| Chainlit
    Chainlit -->|Poll| Redis
    Agent -->|Monitor| TruLens
    Tools -->|Monitor| TruLens
    OpenAI -->|Evaluate| TruLens
    
    %% Styling
    classDef external fill:#e6f3ff,stroke:#0066cc,stroke-width:2px,color:#000
    classDef process fill:#fff2e6,stroke:#cc6600,stroke-width:2px,color:#000
    classDef storage fill:#e6ffe6,stroke:#006600,stroke-width:2px,color:#000
    classDef ui fill:#ffe6e6,stroke:#cc0000,stroke-width:2px,color:#000
    classDef ai fill:#f2e6ff,stroke:#6600cc,stroke-width:2px,color:#000
    classDef user fill:#f5f5f5,stroke:#666666,stroke-width:2px,color:#000
    
    class SDV external
    class Ingest process
    class FAISS,Redis storage
    class Chainlit ui
    class Agent,Tools,OpenAI,TruLens ai
    class User user
```

## Monitoring and Evaluation
The system uses TruLens for comprehensive monitoring and evaluation of the RAG pipeline:
- **Feedback Collection**: Tracks user feedback on resolution recommendations
- **Performance Metrics**: Monitors latency, token usage, and response quality
- **Quality Assurance**: Evaluates retrieval relevance and generation accuracy
- **Custom Feedback Functions**: Implements domain-specific evaluation criteria for incident resolution quality

## Current Limitations
- Proof of concept using synthetic data
- Polling-based Redis implementation
- OpenAI API dependency
- Basic agent implementation with query validation

## Future Enhancements
- Redis Pub/Sub integration
- Production-grade security
- Cloud-based deployment
- Enhanced agentic capabilities