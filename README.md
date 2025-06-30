# MANE Graduate Handbook Chatbot (Local + Google Cloud Integration)

This project is a Retrieval-Augmented Generation (RAG) based chatbot designed to answer questions about the RPI MANE Graduate Student Handbook.

This version uses Ollama for local AI processing and can optionally integrate with Google Cloud services for enhanced functionality.

## Features

- **Local AI Processing**: Uses Ollama to run open-source LLMs locally
- **Vector Database**: ChromaDB for efficient document retrieval
- **Google Cloud Integration** (Optional):
  - Google Cloud Storage for document storage
  - Google Cloud Firestore for chat history persistence
  - Google Cloud Run for deployment
- **Privacy-First**: Your data stays local by default

## How it Works

1.  **Ollama Setup**: This project uses [Ollama](https://ollama.com/) to run a powerful open-source Large Language Model (like Llama 3) locally.
2.  **Ingestion**: The `ingest.py` script reads the handbook PDF, splits it into chunks, and uses a local sentence-transformer model to generate embeddings. These are stored in a local ChromaDB vector database.
3.  **Chat Interface**: The `app.py` script runs a Streamlit web application. When a user asks a question, the app searches the local vector database for relevant text chunks.
4.  **Answering**: The user's question and the retrieved text are sent to the local LLM running via Ollama. The model is instructed to answer the question based *only* on the provided information from the handbook.
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
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Local Setup

**Step 1: Install and Set Up Ollama**

This is a one-time setup.

1.  Go to [https://ollama.com/](https://ollama.com/) and download the application for your operating system (Windows, macOS, or Linux).
2.  Install Ollama.
3.  Once installed, open your terminal or command prompt and pull a model. We recommend Llama 3, which is powerful and efficient.
    ```bash
    ollama pull llama3
    ```
    This will download the model to your machine. You can verify it's running by typing `ollama list`.

**Step 2: Set Up the Python Project**

1.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up Environment Variables**:
    -   Copy `env.example` to `.env`.
    -   The file specifies which Ollama model to use. The default is `llama3`, which you just downloaded.

3.  **Add the Handbook**:
    -   Place the MANE Graduate Student Handbook PDF inside the `data` folder.
    -   Make sure the file is named `MANE_GRADUATE_HANDBOOK.pdf`.

4.  **Create the Knowledge Base**:
    ```bash
    python src/ingest.py
    ```

5.  **Run the Chatbot Application**:
    ```bash
    streamlit run src/app.py
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
| `OLLAMA_MODEL` | Ollama model to use | `llama3-chatqa` |
| `EMBEDDING_MODEL` | Embedding model for vector search | `all-MiniLM-L6-v2` |
| `USE_CLOUD_SERVICES` | Enable Google Cloud integration | `false` |
| `USE_CLOUD_STORAGE` | Use Cloud Storage for documents | `false` |
| `GCS_BUCKET_NAME` | Google Cloud Storage bucket name | - |
| `CLOUD_DOCUMENT_PATH` | Path to document in Cloud Storage | `documents/MANE_GRADUATE_HANDBOOK.pdf` |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | - |

## Troubleshooting

### Local Issues
- **Ollama not found**: Make sure Ollama is installed and running
- **Model not found**: Run `ollama pull llama3` to download the model
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