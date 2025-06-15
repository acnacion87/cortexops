from typing import Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="hkunlp/instructor-base",
        model_kwargs = {"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True})

def get_retriever(index_path: str, **kwargs: Any) -> VectorStoreRetriever:
    embedding_model = get_embedding_model()

    db = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)
    return db.as_retriever(**kwargs)