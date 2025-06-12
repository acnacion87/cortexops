import os
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from typing import List


# Preprocess synthetic tickets dataset to LangChain Documents
def tickets_dataset_to_documents():
    INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")

    print(f'Loading synthetic dataset for customer support tickets: {INCIDENTS_DATASET_HF_REPO_ID}')
    tickets_dataset = load_dataset(INCIDENTS_DATASET_HF_REPO_ID)

    docs = []
    for item in tickets_dataset["train"]:
        number = (item.get("number") or "").strip()
        short_desc = (item.get("short_description") or "").strip()
        description = (item.get("description") or "").strip()
        resolution = (item.get("resolution") or "").strip()

        if not short_desc or not description or not resolution:
            continue

        # Combine content for embedding
        content = f"Short Description: {short_desc}\nDescription: {description}\nResolution: {resolution}"
        metadata = {
            "number": number,
            "source": "ServiceNow",
            "short_description": short_desc
        }
        docs.append(Document(page_content=content, metadata=metadata))
    print(f"Prepared {len(docs)} incident tickets for indexing.")

    return docs

# Preprocess synthetic documentations dataset to LangChain Documents
def docs_dataset_to_documents():
    CONFLUENCE_DATASET_HF_REPO_ID = os.getenv("CONFLUENCE_DATASET_HF_REPO_ID")

    print(f'Loading synthetic dataset for documentations: {CONFLUENCE_DATASET_HF_REPO_ID}')
    docs_dataset = load_dataset(CONFLUENCE_DATASET_HF_REPO_ID)

    docs = []
    for item in docs_dataset["train"]:
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        overview = (item.get("overview") or "").strip()
        tools = "\n".join(map(str, item.get('tools')))
        investigation_steps = "\n".join(map(str, item.get('investigation_steps')))

        # Combine content for embedding
        content = f"Title: {title}\nOverview: {overview}\nTools: {tools}\nInvestigation Steps: {investigation_steps}"
        metadata = {
            "source": "Confluence",
            "url": url,
            "title": title
        }
        docs.append(Document(page_content=content, metadata=metadata))
    print(f"Prepared {len(docs)} documentations for indexing.")

    return docs

def build_faiss_index(documents: List[Document]):
    INDEX_PATH = os.getenv("INDEX_PATH")

    embed_instruction = (
        "Represent the Merchant Onboarding System incident report or technical "
        "knowledge base article for retrieval, aiming to find relevant resolution "
        "steps and troubleshooting steps:"
    )

    embed_model = HuggingFaceEmbeddings(
        model_name="hkunlp/instructor-base",
        model_kwargs = {'device': 'cpu'},
        encode_kwargs = {'normalize_embeddings': True}
    )
    
    instructed_docs = [Document(
        page_content=f"{embed_instruction}{doc.page_content}",
        metadata=doc.metadata) for doc in documents]
    
    print("Creating FAISS Index...")
    vector_store = FAISS.from_documents(instructed_docs, embed_model)

    print(f"Saving FAISS index to: {INDEX_PATH}")
    vector_store.save_local(INDEX_PATH)

    print("Done! Document embeddings are ready for RAG.")

if __name__ == "__main__":
    load_dotenv()

    documents = []
    documents.extend(tickets_dataset_to_documents())
    documents.extend(docs_dataset_to_documents())
    build_faiss_index(documents)




