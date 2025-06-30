FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create directory for ChromaDB
RUN mkdir -p chroma_db

# Expose port
EXPOSE 8501

# Start Ollama and the application
CMD ["sh", "-c", "ollama serve & sleep 10 && streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0"] 