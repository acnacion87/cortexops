import json
import re
import time
import logging

from openai import OpenAI
from dotenv import load_dotenv

OPENAI_MODEL = "gpt-3.5-turbo"
MAX_RETRIES = 3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('[OpenAI]')

load_dotenv()

client = OpenAI()

def clean_json_text(text):
    # Remove triple backticks and optional json language tag
    text = re.sub(r"```(?:json)?\s*", "", text)
    return text.replace("```", "").strip()

def query_openai_json(prompt, system_prompt=None, temperature=0.7, max_tokens=1024, model=None):
    model = model or OPENAI_MODEL

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            messages = [
                {"role": "user", "content": prompt}
            ]
            if (system_prompt):
                messages.insert(0, {"role": "system", "content": system_prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            clean = clean_json_text(content)
            return json.loads(clean)

        except json.JSONDecodeError as e:
            logger.warning("JSON parsing failed (attempt %d): %s", attempt, e)
            if attempt == MAX_RETRIES:
                raise
            logger.info("Retrying after 2 seconds...")
            time.sleep(2)
        except Exception as e:
            logger.error("OpenAI API failed: %s", e)
            raise