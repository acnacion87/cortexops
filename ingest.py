import os
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.docstore.document import Document

load_dotenv()
TICKETS_CSV_PATH = os.getenv("TICKETS_CSV_PATH")
DOCS_CSV_PATH = os.getenv("DOCS_CSV_PATH")

INDEX_PATH = os.getenv("INDEX_PATH")

# Load Dataset from Hugging Face
print(f'Loading synthetic dataset for customer support tickets: {TICKETS_CSV_PATH}')

documents = []
# Preprocess synthetic tickets dataset to LangChain Documents
def tickets_dataset_to_documents():
    tickets_dataset = load_dataset("csv", data_files = TICKETS_CSV_PATH, split="train")
    for item in tickets_dataset:
        id = (item.get("id") or "").strip()
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        resolution = (item.get("resolution") or "").strip()

        if not title or not description or not resolution:
            continue

        # Combine content for embedding
        content = f"Title: {title}\nDescription: {description}\nResolution: {resolution}"
        metadata = {
            "source": "ServiceNow",
            "id": id,
            "title": title
        }
        documents.append(Document(page_content=content, metadata=metadata))
    print(f"Prepared customer support tickets for indexing.")

# Preprocess synthetic documents dataset to LangChain Documents
def docs_dataset_to_documents():
    docs_dataset = load_dataset("csv", data_files = DOCS_CSV_PATH, split="train")
    for item in docs_dataset:
        url = (item.get("url") or "").strip()
        title = (item.get("title") or "").strip()
        overview = (item.get("overview") or "").strip()
        tools = (item.get("tools") or "").strip()
        investigation_steps = (item.get("investigation_steps") or "").strip()

        # Combine content for embedding
        content = f"Title: {title}\nOverview: {overview}\nTools: {tools}\nInvestigation Steps: {investigation_steps}"
        metadata = {
            "source": "Confluence",
            "url": url,
            "title": title
        }
        documents.append(Document(page_content=content, metadata=metadata))
    print(f"Prepared documentations for indexing.")

def build_faiss_index(indexPath):
    embed_model = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-base",
        model_kwargs = {'device': 'cpu'},
        encode_kwargs = {'normalize_embeddings': True},
        query_instruction="Represent the ServiceNow issue ticket:",
        embed_instruction="Represent the past incident ticket and resolution:")
    
    print("Creating FAISS Index...")
    vector_store = FAISS.from_documents(documents, embed_model)

    print(f"Saving FAISS index to: {indexPath}")
    vector_store.save_local(indexPath)

    print("Done! Document embeddings are ready for RAG.")


tickets_dataset_to_documents()
docs_dataset_to_documents()

build_faiss_index(INDEX_PATH)





