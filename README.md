# MANE Graduate Handbook Chatbot (OpenRouter + Google Cloud Integration)

This project is a Retrieval-Augmented Generation (RAG) based chatbot designed to answer questions about the RPI MANE Graduate Student Handbook.

This version uses OpenRouter for AI processing (free tier models available) and can optionally integrate with Google Cloud services for enhanced functionality.

## Features

- **Cloud AI Processing**: Uses OpenRouter to access free tier LLMs (no local installation required)
- **Vector Database**: ChromaDB for efficient document retrieval
- **Google Cloud Integration** (Optional):
  - Google Cloud Storage for document storage
  - Google Cloud Firestore for chat history persistence
  - Google Cloud Run for deployment
- **Privacy-First**: Your data stays local by default (embeddings are generated locally)

## How it Works

1.  **OpenRouter Setup**: This project uses [OpenRouter](https://openrouter.ai/) to access free tier LLMs (like Llama 3.3 8B) via API. No local installation required.
2.  **Ingestion**: The `ingest.py` script reads the handbook PDF, splits it into chunks, and uses a local sentence-transformer model to generate embeddings. These are stored in a local ChromaDB vector database.
3.  **Chat Interface**: The `app.py` script runs a Streamlit web application. When a user asks a question, the app searches the local vector database for relevant text chunks.
4.  **Answering**: The user's question and the retrieved text are sent to the LLM via OpenRouter API. The model is instructed to answer the question based *only* on the provided information from the handbook.
5.  **Cloud Integration** (Optional): Chat history can be stored in Firestore, and documents can be stored in Cloud Storage.

## Project Structure

```
mane_handbook_chatbot/
├── data/
│   └── MANE_GRADUATE_HANDBOOK.pdf  <-- Place the handbook PDF here
├── src/
│   ├── ingest.py           # Script to process the PDF and build the knowledge base
│   ├── chatbot.py          # Core RAG logic using local models
│   ├── app.py              # The Streamlit web application (local mode)
│   ├── app_cloud.py        # Enhanced app with Google Cloud integration
│   ├── cloud_storage.py    # Google Cloud Storage utilities
│   └── firestore_chat.py   # Google Cloud Firestore chat history
├── Dockerfile              # For Google Cloud Run deployment
├── deploy_to_cloud_run.sh  # Deployment script
├── env.example             # Example environment variables file
├── pyproject.toml          # Python dependencies (uv managed)
└── README.md               # This file
```

## Local Setup

**Note**: This project uses [uv](https://github.com/astral-sh/uv) for fast Python dependency management and virtual environments. uv is significantly faster than pip and handles virtual environments automatically.

**Step 1: Get OpenRouter API Key**

1.  Go to [https://openrouter.ai/](https://openrouter.ai/) and create an account.
2.  Navigate to your account settings and generate an API key.
3.  The free tier includes access to models like `meta-llama/llama-3.3-8b-instruct:free`.

**Step 2: Set Up the Python Project**

1.  **Install uv** (if not already installed):
    ```bash
    # On macOS/Linux:
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Or using pip:
    pip install uv
    ```

2.  **Install Python Dependencies with uv**:
    ```bash
    uv sync
    ```
    This will create a virtual environment and install all dependencies from `pyproject.toml`.

3.  **Set up Environment Variables**:
    -   Copy `env.example` to `.env`.
    -   Edit `.env` and add your OpenRouter API key:
        ```env
        OPENROUTER_API_KEY=your-api-key-here
        ```
    -   You can optionally change the model (default is `meta-llama/llama-3.3-8b-instruct:free`).

3.  **Add the Handbook**:
    -   Place the MANE Graduate Student Handbook PDF inside the `data` folder.
    -   Make sure the file is named `MANE_GRADUATE_HANDBOOK.pdf`.

4.  **Create the Knowledge Base**:
    ```bash
    uv run python src/ingest.py
    ```

5.  **Run the Chatbot Application**:
    ```bash
    uv run streamlit run src/app.py
    ```

## Google Cloud Integration

### Prerequisites

1. **Google Cloud Project**: Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable APIs**: Enable the following APIs:
   - Cloud Storage API
   - Cloud Firestore API
   - Cloud Run API
   - Cloud Build API
3. **Service Account**: Create a service account with appropriate permissions
4. **Authentication**: Download the service account key and set the environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
   ```

### Configuration

1. **Update Environment Variables**:
   ```bash
   cp env.example .env
   ```

   Edit `.env` and set:
   ```env
   USE_CLOUD_SERVICES=true
   USE_CLOUD_STORAGE=true
   GCS_BUCKET_NAME=your-bucket-name
   GOOGLE_CLOUD_PROJECT=your-project-id
   ```

2. **Create Cloud Storage Bucket**:
   ```bash
   gsutil mb gs://your-bucket-name
   ```

3. **Run with Cloud Integration**:
   ```bash
   streamlit run src/app_cloud.py
   ```

### Deployment to Google Cloud Run

1. **Install Google Cloud CLI**:
   ```bash
   # Follow instructions at https://cloud.google.com/sdk/docs/install
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Deploy**:
   ```bash
   chmod +x deploy_to_cloud_run.sh
   ./deploy_to_cloud_run.sh
   ```

### Cloud Features

- **Document Storage**: Upload and manage documents in Google Cloud Storage
- **Chat History**: Persistent chat sessions stored in Firestore
- **Session Management**: Create new chat sessions and view history
- **Scalable Deployment**: Deploy to Cloud Run for production use

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key (required) | - |
| `OPENROUTER_MODEL` | OpenRouter model to use | `meta-llama/llama-3.3-8b-instruct:free` |
| `OPENROUTER_BASE_URL` | OpenRouter API base URL | `https://openrouter.ai/api/v1` |
| `EMBEDDING_MODEL` | Embedding model for vector search | `all-MiniLM-L6-v2` |
| `USE_CLOUD_SERVICES` | Enable Google Cloud integration | `false` |
| `USE_CLOUD_STORAGE` | Use Cloud Storage for documents | `false` |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket name | - |
| `CLOUD_DOCUMENT_PATH` | Path to document in Cloud Storage | `documents/MANE_GRADUATE_HANDBOOK.pdf` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | - |

## Troubleshooting

### Local Issues
- **OpenRouter API key missing**: Make sure to set `OPENROUTER_API_KEY` in your `.env` file
- **Model not available**: Check OpenRouter for model availability; some free models may have rate limits
- **ChromaDB not found**: Run `python src/ingest.py` to create the vector database

### Cloud Issues
- **Authentication errors**: Check your service account key and permissions
- **Bucket not found**: Create the Cloud Storage bucket first
- **API not enabled**: Enable required Google Cloud APIs

## Security Notes

- The local version keeps all data on your machine
- Cloud integration requires proper IAM permissions
- Service account keys should be kept secure and not committed to version control
- Consider using Workload Identity for production deployments