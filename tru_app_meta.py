APP_VERSION = "2.0.0"

APP_INFERENCE_MODEL = "gpt-4o-mini"

APP_METADATA = {
    "type": "Agentic",
    "retriever": "faiss",
    "retrieval_strategy": "similarity_score_threshold+mmr",
    "embedding_model": "hkunlp/instructor-base",
    "index_style": "per-tool",
    "prompt_style": "few-shot",
    "inference_model": f"OpenAI/{APP_INFERENCE_MODEL}",
    "feedback_model": "OpenAI/gpt-4o-mini"
}