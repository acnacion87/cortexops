import os
import random

from dotenv import load_dotenv
from lib.files import save_to_csv, save_to_json
from lib.synthesize import generate_synthetic_data

load_dotenv()
TICKETS_CSV_PATH = os.getenv("TICKETS_CSV_PATH")
TICKETS_JSON_PATH = os.getenv("TICKETS_JSON_PATH")


PROMPT = """
You are an expert in a Merchant Onboarding Application used by Sales Agents to onboard merchants to avail
Bank of Mock payments services.

This application is a CRUD application where sales agents enter information about a merchant, the payment services equipments they need (e.g. POS terminals),
fees to paid, and other additional services to be availed in order to be onboarded to the Payment Processor's system. Another part of the system is the
Customer UI where merchants login to sign the merchant agreement (PDF). Once signed, the onboarding goes to PROCESSING stage.

Generate a synthetic IT support ticket as a JSON object with the following fields:
- title: a short summary of the issue. the short summary should be based on the description and not too generic
- description: a detailed explanation
- resolution: the resolution applied. 
- urgency: one of ["low", "medium", "high", "critical"]

Some typical issues encountered by Sales Agents are: unable to login, form validation errors, incorrect min-max rates for fees.
Some typical issues encountered by Merchants are: missing info on merchant agreement, merchant agreement not loading, unable to e-sign, unable to download
the unsigned version of the agreement (PDF).

Do not just focus on these typical issues. Play around with other possibilities but make sure these common issues are covered.

For the resolution, this should be in past tense because this tells how the issue was resolved (e.g. Called user to verify. Asked user to relogin).
The resolution should be a list of steps taken with minimum entry of 3 steps.

Return ONLY the raw JSON object.
"""

def generate_unique_incident_id(existing_ids):
    while True:
        new_id = f"INC{random.randint(0, 99999):05d}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id
        
if __name__ == "__main__":
    print("Generating synthetic incident tickets...")
    synthetic_data = generate_synthetic_data(PROMPT, 20)

    used_ids = set()
    for item in synthetic_data:
        item["id"] = generate_unique_incident_id(used_ids)

    save_to_csv(synthetic_data, TICKETS_CSV_PATH)
    save_to_json(synthetic_data, TICKETS_JSON_PATH)
