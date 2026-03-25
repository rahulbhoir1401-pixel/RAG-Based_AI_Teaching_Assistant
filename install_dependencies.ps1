Write-Host "Installing FFmpeg..."
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements --silent

Write-Host "Installing Python Requirements..."
python -m pip install setuptools wheel
python -m pip install -r backend/requirements.txt
python -m pip install git+https://github.com/openai/whisper.git

Write-Host "Pulling Ollama Models (this may take a while depending on your internet connection)..."
ollama pull llama3.2
ollama pull bge-m3

Write-Host "All system dependencies installed successfully!"
