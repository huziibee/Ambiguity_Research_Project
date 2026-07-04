import os
import json
import hashlib
import time
from typing import Any, Dict, Optional
import litellm
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables from .env file if present
load_dotenv()

from src.schema import ManagerInput, ManagerOutput
from src.baselines.ollama_llm import OUTPUT_SCHEMA, _prompt, _parse_output

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache", "llm_responses")

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _completion_with_backoff(**kwargs):
    """
    Wrap litellm completion calls in exponential backoff retries to handle rate limiting.
    """
    return litellm.completion(**kwargs)

def llm_predict(input_data: ManagerInput) -> Optional[ManagerOutput]:
    backend = os.environ.get("DIRECT_LLM_BACKEND", "").lower().strip()
    
    # Auto-detect backend if not explicitly set
    if not backend:
        if "LITELLM_MODEL" in os.environ or any(k in os.environ for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]):
            backend = "litellm"
        elif "LOCAL_LLM_MODEL" in os.environ or os.environ.get("DIRECT_LLM_BACKEND") == "ollama":
            backend = "ollama"
        else:
            return None

    if backend == "ollama":
        from src.baselines.ollama_llm import ollama_predict
        return ollama_predict(input_data)

    if backend == "litellm":
        model = os.environ.get("LITELLM_MODEL") or os.environ.get("LOCAL_LLM_MODEL")
        if not model:
            if "GEMINI_API_KEY" in os.environ or "GOOGLE_API_KEY" in os.environ:
                model = "gemini/gemini-3.1-flash-lite"
            elif "OPENAI_API_KEY" in os.environ:
                model = "gpt-4o-mini"
            elif "ANTHROPIC_API_KEY" in os.environ:
                model = "claude-3-5-haiku-20241022"
            else:
                model = "gemini/gemini-3.1-flash-lite"

        prompt = _prompt(input_data)
        
        # Check cache
        use_cache = os.environ.get("DISABLE_LLM_CACHE", "").lower().strip() != "true"
        cache_key = hashlib.sha256(f"{model}:{prompt}".encode("utf-8")).hexdigest()
        cache_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        if use_cache:
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                    return _parse_output(cached_data, input_data)
                except Exception as e:
                    print(f"[CACHE ERROR] Failed to load cache: {e}")
        
        # Rate limit friendly sleep
        time.sleep(2.0)
        
        try:
            # Call litellm completion wrapped with tenacity exponential backoff
            response = _completion_with_backoff(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You must output a JSON object adhering exactly to the requested schema. Do not output anything other than the JSON object."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_object",
                    "response_schema": OUTPUT_SCHEMA
                },
                temperature=0.0
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                return None
            
            parsed_json = json.loads(raw_content.strip())
            
            # Write to cache if successful
            if use_cache:
                os.makedirs(CACHE_DIR, exist_ok=True)
                try:
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"[CACHE ERROR] Failed to write cache: {e}")
                    
            return _parse_output(parsed_json, input_data)
        except Exception as e:
            print(f"[LITELLM ERROR] Model {model} failed after retries: {e}")
            raise e

    return None
