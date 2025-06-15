APP_VERSION = "2.0.0"

APP_METADATA = {
    "type": "RAG",
    "retriever": "faiss",
    "retrieval_strategy": "similarity_score_threshold",
    "embedding_model": "hkunlp/instructor-base",
    "index_style": "single-index",
    "rag_chain": "stuff_documents_chain",
    "prompt_style": "Zero-shot",
    "inference_model": "Ollama/phi3:mini",
    "feedback_model": "OpenAI/gpt-4o-mini"
}