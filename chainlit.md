# Welcome to CortexOps! 🚀🤖

Hi there! 👋 Welcome to CortexOps, a smart incident resolution system powered by AI. This system helps IT support teams quickly resolve incidents by leveraging AI-generated knowledge from past incidents and documentation.

## About CortexOps

CortexOps is a proof-of-concept AI assistant that:
- Analyzes new incident tickets in real-time
- Searches through past incidents and documentation
- Provides contextually relevant resolution recommendations
- Uses synthetic data for demonstration purposes

## Current Features

- 🔍 Real-time incident analysis
- 📚 Knowledge base search using FAISS vector database
- 🤖 AI-powered resolution recommendations using Ollama (phi3:mini)
- 📊 Performance monitoring with TruLens
- 💬 Interactive chat interface with Chainlit

## System Status

⚠️ **Note**: This is a proof of concept and is not production-ready. The system currently:
- Uses synthetic data for demonstration
- Runs on a local LLM deployment
- Implements basic RAG chain without agentic capabilities
- Uses polling-based Redis implementation

## Getting Started

1. Wait for a new incident to be raised
2. When an incident arrives, you'll see a notification
3. Click "🧠 Analyze" to get AI-powered resolution recommendations
4. Review the recommendations and suggested next steps

## Technical Details

- **Version**: 2.0.0
- **RAG Implementation**: FAISS vector store with instructor-base embeddings
- **Inference Model**: Ollama/phi3:mini
- **Feedback Model**: OpenAI/gpt-4-mini
- **UI Framework**: Chainlit
- **API Framework**: FastAPI
- **Vector Database**: FAISS
- **Message Broker**: Redis

Happy incident resolution! 🎯✨
