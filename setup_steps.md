### Python setup
1. Install Python 3.9+
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the environment:
    - Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

    - Linux/Mac:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

### Ollama setup
1. Install Ollama from https://ollama.com/download/
2. Pull required models:

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

3. Start Ollama:

```bash
ollama serve
```

### Optional models for advanced demos
Some module demos use additional model tags. Pull these only if needed:

```bash
ollama pull llama3.1:latest
ollama pull lfm2.5-thinking:latest
```