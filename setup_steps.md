### Python Setup Steps
1. Install the python3 (recommended version 3.11.3)
2. Follow venv based approach to avoid breaking your other python application
    a. Go to cmd
    b. Create a folder named agentic-ai-workshop
    c. Go to that folder
    d. Run command : python -m venv test_env
    e. Activate the venv : test_env\Scripts\activate
    f. Download the requirements.txt and copy to agentic-ai-workshop folder
    g. Run command : python install -r requirements.txt


### LLM Setup Steps
1. Install ollama (LLM Provider) from https://ollama.com/download/ (Make sure you have at least 8 GB of RAM and 10 GB of free disk space for the model)
2. Run command : ollama pull llama3.1:latest
3. Run command : ollama run nomic-embed-text:latest
4. Run command : ollama list
5. Run command : ollama serve


Once you are done we are good to start tomorrow. Eager to meet you all tomorrow !!!

!!! Happy Learning !!!