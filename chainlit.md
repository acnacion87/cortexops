# Welcome to CortexOps! 🚀🤖

Welcome to CortexOps, an AI-powered incident resolution system! This application helps IT support teams by providing rapid, contextually relevant resolution recommendations for new incident reports.

## How It Works 🔧

1. When a new incident ticket is raised, you'll be notified and given the option to analyze or ignore it.
2. If you choose to analyze, our AI system will:
   - Search through past incidents and documentation
   - Generate relevant resolution recommendations
   - Stream the response in real-time

## Features ✨

- **Smart Analysis**: Uses RAG (Retrieval Augmented Generation) to find similar past incidents and relevant documentation
- **Real-time Streaming**: Watch the AI's thought process as it analyzes incidents
- **Interactive UI**: Choose to analyze or ignore new incidents as they come in
- **Quality Monitoring**: Evaluates response quality and relevance using TruLens

## Note 📝

This is a proof of concept using synthetic data for demonstration purposes. The system currently uses:
- Ollama (phi3:mini) for local inference
- FAISS for vector similarity search
- Redis as a message broker

## Getting Help 🔗

- **Documentation**: For technical details, check out our [GitHub Repository](https://github.com/arjaynacion/agentic-rag-support)
- **Issues**: Found a bug? Have a suggestion? [Open an issue](https://github.com/arjaynacion/agentic-rag-support/issues)

Let's make incident resolution smarter and faster! 💪

## Welcome screen

To modify the welcome screen, edit the `chainlit.md` file at the root of your project. If you do not want a welcome screen, just leave this file empty.
