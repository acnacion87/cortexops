import os
from langchain.tools import tool
from lib.embeddings import EMBED_INCIDENT_INSTRUCTION, EMBED_KB_INSTRUCTION, get_retriever
from lib.openai import query_openai_json

from trulens.apps.langchain import WithFeedbackFilterDocuments
from trulens.core import Feedback
from trulens.providers.openai import OpenAI

from tru_app_meta import APP_FEEDBACK_MODEL

provider = OpenAI(model_engine=APP_FEEDBACK_MODEL)
f_context_relevance_score = Feedback(
    provider.context_relevance, name="Context Relevance"
)

QUERY_VALIDATION_SYSTEM_PROMPT = """You are a query validator for the Merchant Onboarding System. Your task is to determine if a given query is valid and relevant to the system's context.

The Merchant Onboarding System is a CRUD application where:
- Sales Agents input merchant data, choose equipment, and configure fees/services
- Merchants log in via a separate UI to review and e-sign a Merchant Agreement (PDF)
- The onboarding process proceeds to the PROCESSING stage once the agreement is signed

A valid query should:
1. Be related to technical issues, troubleshooting, or system functionality
2. Be clear and specific enough to be actionable
3. Be within the scope of the Merchant Onboarding System
4. Not be a general question or unrelated to the system

Return a JSON object with:
{
    "is_valid": boolean,
    "reason": "string explaining why the query is valid or invalid"
}"""

QUERY_VALIDATION_USER_PROMPT = """Validate if the following query is valid for the Merchant Onboarding System:

Query: {query}

Consider:
- Is it related to the system's functionality?
- Is it a technical issue or troubleshooting question?
- Is it clear and specific enough?
- Is it within the system's scope?

Return only a JSON object with is_valid and reason fields."""

@tool("is_query_valid", description="Use this FIRST to check if the query is valid in the context of the Merchant Onboarding System.")
def is_query_valid(query: str):
    """
    Validate if a query is relevant to the Merchant Onboarding System using OpenAI.
    
    Args:
        query: The query to validate
    Returns:
        bool: True if the query is valid, False otherwise
    """
    try:
        result = query_openai_json(
            prompt=QUERY_VALIDATION_USER_PROMPT.format(query=query),
            system_prompt=QUERY_VALIDATION_SYSTEM_PROMPT,
            temperature=0.0  # Use 0 temperature for consistent validation
        )
        return result.get("is_valid", False)
    except Exception as e:
        print(f"Error validating query: {e}")
        return False

@tool("search_incidents", description="Use this only if query is validto search for related incidents.")
def search_incidents(query: str):
    """
    Search for related incidents in the knowledge base using semantic search.
    
    Args:
        query: The search query to find related incidents
    Returns:
        List of documents containing incident information
    """
    index_path = os.getenv("INCIDENTS_INDEX_PATH")
    if not index_path:
        raise ValueError("INCIDENTS_INDEX_PATH environment variable is not set")
    
    retriever = get_retriever(index_path = index_path, search_type="similarity_score_threshold",
        search_kwargs={"k": 6, "score_threshold": 0.7})
    
    filtered_retriever = WithFeedbackFilterDocuments.of_retriever(
        retriever=retriever, feedback=f_context_relevance_score, threshold=0.75
    )

    query_instruction = (
        "Represent the new Merchant Onboarding System incident report "
        "to find the most relevant resolution steps and troubleshooting steps")
    
    docs = filtered_retriever.invoke(f"{query_instruction}:{query}")
    if (len(docs) == 0):
        return None
    
    return "\n\n".join([doc.page_content.replace(f"{EMBED_INCIDENT_INSTRUCTION}:", "") for doc in docs])

@tool("search_knowledge_base", description="Use this only if query is valid to search for related knowledge base articles.")
def search_kb(query: str):
    """
    Search for related knowledge base articles in the knowledge base using semantic search.
    
    Args:
        query: The search query to find related knowledge base articles
    Returns:
        List of documents containing knowledge base articles
    """
    index_path = os.getenv("KNOWLEDGE_BASE_INDEX_PATH")
    if not index_path:
        raise ValueError("KNOWLEDGE_BASE_INDEX_PATH environment variable is not set")
    
    retriever = get_retriever(index_path = index_path, search_type="mmr",
        search_kwargs={"k": 6, "lambda_mult": 0.7})
    
    filtered_retriever = WithFeedbackFilterDocuments.of_retriever(
        retriever=retriever, feedback=f_context_relevance_score, threshold=0.75
    )
    query_instruction = (
        "Represent the new Merchant Onboarding System incident report to find the most relevant"
        "knowledge base article containing resolution steps and troubleshooting steps")
    
    docs = filtered_retriever.invoke(f"{query_instruction}:{query}")
    if (len(docs) == 0):
        return None
    
    return "\n\n".join([doc.page_content.replace(f"{EMBED_KB_INSTRUCTION}:", "") for doc in docs])
