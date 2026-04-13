

import requests




# PROMPT STYLES - Try these to see how prompts shape outputs:

# Simple question
# prompt = "Explain the concept of AI agents in one sentence."

# Structured request
# prompt = "Summarize the benefits of unit tests in 3 bullet points."

# Translation task
# prompt = "Translate to Spanish: 'Where is the train station?'"

# Classification task
# prompt = "Classify the sentiment (positive/neutral/negative): 'The service was slow but the food was great.'"

# Creative generation
# prompt = "Write a short (3-line) poem about rain."

# Information extraction
# prompt = "Extract keywords from this text: 'Agents combine reasoning and tools to solve tasks.'"

# JSON output (format constraint)
# prompt = "Given input JSON {\"a\": 3, \"b\": 4}, output only the sum as a number."

# Strict JSON generation
# prompt = "You are a strict JSON generator. Output only JSON with keys: title, summary. Topic: LangChain."

url = "http://localhost:11434/api/generate"

# Prompt examples: uncomment ONE at a time to try different prompt styles.
prompt = "What is the capital of France?"

payload = {
    "model": "llama3",  # Default model
    "prompt": prompt,
    "stream": False
}
response = requests.post(url, json=payload)

print(response.json().get("response", ""))


