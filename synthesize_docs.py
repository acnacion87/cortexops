import os
import pandas as pd
import time

from dotenv import load_dotenv
from lib.files import save_to_csv, save_to_json
from lib.ollama import query_ollama_json

load_dotenv()
TICKETS_CSV_PATH = os.getenv("TICKETS_CSV_PATH")
DOCS_CSV_PATH = os.getenv("DOCS_CSV_PATH")
DOCS_JSON_PATH = os.getenv("DOCS_JSON_PATH")

# Generate the prompt to be used with the model
def make_prompt(title, description, resolution):
    return f"""
You are an expert IT documentation writer. Based on the following incident details,
write an internal Confluence-style documentation detailing steps to resolve the issue or similar issue.
The incidents that will be given are from Service Now.

Context:
Incident Title: {title}
Description: {description}
Resolution: {resolution}

Generate a synthetic documentation as a JSON object with the following fields:
 - url - randomly generated URL/link for this documentation.
 - title - should not match exactly the incident title. Be creative here and make a title that mimics real-world documentations.
 - overview - overview of what the documentation is for.
 - tools - list tools to use to investigate issue (e.g. Splunk, Jira, etc.)
 - investigation_steps - list of steps to investigate the issue

Return ONLY the raw JSON object.
"""
def generate_doc(ticket, max_retries=3):
    title = ticket.get("title", "Untitled")
    description = ticket.get("description", "")
    resolution = ticket.get("urgency", "")

    prompt = make_prompt(title, description, resolution)

    for _ in range(max_retries):
            try:
                doc = query_ollama_json(prompt)
                if doc:  # Ensure parsing returned usable data
                    return doc
                else:
                    print(f"Unable to generate documentation for: {title}. Retrying")
            except Exception as e:
                print(f"Failed to generate doc for ticket {ticket.get('id', '?')}: {e}")

def generate_docs_from_tickets():
    df = pd.read_csv(TICKETS_CSV_PATH)
    print(f"Loaded {len(df)} incidents from {TICKETS_CSV_PATH}")

    data = []
    for idx, row in df.iterrows():
        doc = generate_doc(row)
        if doc:
            data.append(doc)
            print(f"Generated {len(data)}/{len(df)}")
        
        time.sleep(1)

    if data:
        save_to_csv(data, DOCS_CSV_PATH)
        save_to_json(data, DOCS_JSON_PATH)

if __name__ == "__main__":
    print("Generating synthetic Confluence-style documentation from synthetic incident tickets...")
    generate_docs_from_tickets()
