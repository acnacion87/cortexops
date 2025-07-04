APP_VERSION = "2.0.0"

APP_INFERENCE_MODEL = "gpt-4o-mini"
APP_FEEDBACK_MODEL = "gpt-4.1-nano"
APP_METADATA = {
    "type": "Agentic",
    "retriever": "faiss",
    "retrieval_strategy": "similarity_score_threshold+mmr",
    "embedding_model": "hkunlp/instructor-base",
    "index_style": "per-tool",
    "prompt_style": "zero-shot",
    "inference_model": f"OpenAI/{APP_INFERENCE_MODEL}",
    "feedback_model": f"OpenAI/{APP_FEEDBACK_MODEL}"
}