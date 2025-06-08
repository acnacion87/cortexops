import os
from dotenv import load_dotenv
from datasets import load_dataset
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain.docstore.document import Document

load_dotenv()
INCIDENTS_DATASET_HF_REPO_ID = os.getenv("INCIDENTS_DATASET_HF_REPO_ID")
CONFLUENCE_DATASET_HF_REPO_ID = os.getenv("CONFLUENCE_DATASET_HF_REPO_ID")
INDEX_PATH = os.getenv("INDEX_PATH")

# Load Dataset from Hugging Face
print(f'Loading synthetic dataset for customer support tickets: {INCIDENTS_DATASET_HF_REPO_ID}')

documents = []
# Preprocess synthetic tickets dataset to LangChain Documents
def tickets_dataset_to_documents():
    tickets_dataset = load_dataset(INCIDENTS_DATASET_HF_REPO_ID)
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
        documents.append(Document(page_content=content, metadata=metadata))
    print(f"Prepared customer support tickets for indexing.")

print(f'Loading synthetic dataset for documentations: {CONFLUENCE_DATASET_HF_REPO_ID}')
# Preprocess synthetic documents dataset to LangChain Documents
def docs_dataset_to_documents():
    docs_dataset = load_dataset(CONFLUENCE_DATASET_HF_REPO_ID)
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





