

from openai import OpenAI

# Initialize client pointing to local Ollama with OpenAI-compatible endpoint
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama'  # Required for OpenAI SDK, but can be any string for local Ollama
)

# Send a simple chat request to the LLM
response = client.chat.completions.create(
    model="llama3.2",  # Default model
    messages=[{
        "role": "user",
        "content": "In one paragraph, explain what an AI agent is to a new developer."
    }]
)

# Extract and print the response
print(response.choices[0].message.content)




