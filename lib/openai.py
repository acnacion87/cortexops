import json
import re
import time

from openai import OpenAI
from dotenv import load_dotenv

OPENAI_MODEL = "gpt-3.5-turbo"
MAX_RETRIES = 3

load_dotenv()

client = OpenAI()

def clean_json_text(text):
    # Remove triple backticks and optional json language tag
    text = re.sub(r"```(?:json)?\s*", "", text)
    return text.replace("```", "").strip()

def query_openai_json(prompt, temperature=0.7, max_tokens=1024, model=None):
    model = model or OPENAI_MODEL

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            clean = clean_json_text(content)
            return json.loads(clean)

        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parsing failed (attempt {attempt}): {e}")
            if attempt == MAX_RETRIES:
                raise
            print("[INFO] Retrying after 2 seconds...")
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] OpenAI API failed: {e}")
            raise