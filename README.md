# MANE Graduate Handbook Chatbot (100% Free & Local)

This project is a Retrieval-Augmented Generation (RAG) based chatbot designed to answer questions about the RPI MANE Graduate Student Handbook.

This version uses 100% free, open-source models that run locally on your machine. Your data remains private, and there are no API costs.

## How it Works

1.  **Ollama Setup**: This project uses [Ollama](https://ollama.com/) to run a powerful open-source Large Language Model (like Llama 3) locally.
2.  **Ingestion**: The `ingest.py` script reads the handbook PDF, splits it into chunks, and uses a local sentence-transformer model to generate embeddings. These are stored in a local ChromaDB vector database.
3.  **Chat Interface**: The `app.py` script runs a Streamlit web application. When a user asks a question, the app searches the local vector database for relevant text chunks.
4.  **Answering**: The user's question and the retrieved text are sent to the local LLM running via Ollama. The model is instructed to answer the question based *only* on the provided information from the handbook.

## Project Structure

```
mane_handbook_chatbot/
├── data/
│   └── MANE_GRADUATE_HANDBOOK.pdf  <-- Place the handbook PDF here
├── src/
│   ├── ingest.py       # Script to process the PDF and build the knowledge base
│   ├── chatbot.py      # Core RAG logic using local models
│   └── app.py          # The Streamlit web application
├── .env              # Your local environment variables (copy from .env.example)
├── .env.example      # Example environment variables file
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## How to Run

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
    -   Rename `.env.example` to `.env`.
    -   The file specifies which Ollama model to use. The default is `llama3`, which you just downloaded. You can change this if you prefer another model.

3.  **Add the Handbook**:
    -   Place the MANE Graduate Student Handbook PDF inside the `data` folder.
    -   Make sure the file is named `MANE_GRADUATE_HANDBOOK.pdf`.

4.  **Create the Knowledge Base**:
    -   Run the ingestion script. This will use your local CPU to create the embeddings. It only needs to be done once, or whenever the handbook is updated.
    ```bash
    python src/ingest.py
    ```

5.  **Run the Chatbot Application**:
    ```bash
    streamlit run src/app.py
    ```

This will open a new tab in your browser with the chatbot interface. The chatbot will now be running completely on your local machine, for free.