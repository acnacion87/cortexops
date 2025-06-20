from typing import Any
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever

EMBED_INCIDENT_INSTRUCTION = "Represent the Merchant Onboarding System incident report for retrieval, aiming to find relevant resolution steps and troubleshooting steps"
EMBED_KB_INSTRUCTION = "Represent the ServiceNow Knowledge Base article for retrieval, aiming to find relevant resolution steps and troubleshooting steps"

def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="hkunlp/instructor-base",
        model_kwargs = {"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True})

def get_retriever(index_path: str, **kwargs: Any) -> VectorStoreRetriever:
    embedding_model = get_embedding_model()

    db = FAISS.load_local(index_path, embedding_model, allow_dangerous_deserialization=True)
    return db.as_retriever(**kwargs)