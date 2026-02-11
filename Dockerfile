FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/
COPY data/ ./data/
COPY env.example .

# Create directory for ChromaDB
RUN mkdir -p chroma_db

# Install Python dependencies using uv
RUN uv sync --no-dev

# Expose port
EXPOSE 8501

# Run the application
CMD ["sh", "-c", "uv run streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0"] 