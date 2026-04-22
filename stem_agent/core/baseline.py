from openai import OpenAI
client = OpenAI()
BASE_MODEL = "gpt-4o"
GENERIC_SYSTEM = "You are a helpful AI assistant. Answer questions clearly and accurately."

def run_baseline(query: str) -> str:
    r = client.chat.completions.create(
        model=BASE_MODEL, max_tokens=2000,
        messages=[{"role":"system","content":GENERIC_SYSTEM},{"role":"user","content":query}]
    )
    return r.choices[0].message.content
