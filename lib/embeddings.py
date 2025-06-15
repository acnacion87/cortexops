from typing import Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="hkunlp/instructor-base",
        model_kwargs = {"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True})

def get_retriever(INDEX_PATH, **kwargs: Any):
    embedding_model = get_embedding_model()

    db = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 6, "score_threshold": 0.9})