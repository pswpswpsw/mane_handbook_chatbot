import streamlit as st
import os
from dotenv import load_dotenv
from chatbot import Chatbot
from firestore_chat import FirestoreChatManager
from cloud_storage import CloudStorageManager

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="MANE Handbook Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("MANE Graduate Handbook Chatbot 🤖")
st.caption("Powered by Ollama with Google Cloud integration")

# --- Configuration ---
USE_CLOUD_SERVICES = os.getenv("USE_CLOUD_SERVICES", "false").lower() == "true"

# --- State Management ---
# Initialize the chatbot and store it in the session state
if "chatbot" not in st.session_state:
    # Check if the database exists before initializing
    if not os.path.exists("chroma_db"):
        st.error(
            "The knowledge base (ChromaDB) has not been created yet. "
            "Please run `python src/ingest.py` from your terminal first."
        )
        st.stop()
    
    with st.spinner("Initializing chatbot... This may take a moment."):
        st.session_state.chatbot = Chatbot()

# Initialize cloud services if enabled
if USE_CLOUD_SERVICES and "firestore_manager" not in st.session_state:
    try:
        st.session_state.firestore_manager = FirestoreChatManager()
        st.session_state.storage_manager = CloudStorageManager()
    except Exception as e:
        st.warning(f"Cloud services not available: {e}")
        USE_CLOUD_SERVICES = False

# Initialize chat session
if "session_id" not in st.session_state:
    if USE_CLOUD_SERVICES:
        st.session_state.session_id = st.session_state.firestore_manager.create_chat_session()
    else:
        st.session_state.session_id = "local_session"

# Initialize chat history
if "messages" not in st.session_state:
    if USE_CLOUD_SERVICES:
        # Load from Firestore
        st.session_state.messages = []
        history = st.session_state.firestore_manager.get_chat_history(st.session_state.session_id)
        for msg in history:
            st.session_state.messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    else:
        st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.header("About")
    st.info(
        "This chatbot helps you find answers to questions about the "
        "MANE Graduate Student Handbook.\n\n"
        "It uses a local AI model (via Ollama) and a vector database "
        "to ensure answers come directly from the handbook content."
    )
    
    if USE_CLOUD_SERVICES:
        st.success("✅ Cloud services enabled")
        st.info("Chat history is being saved to Google Cloud Firestore")
    else:
        st.info("ℹ️ Running in local mode")
    
    st.header("How to Use")
    st.markdown(
        """
        1.  Type your question in the chat box below.
        2.  The chatbot will search the handbook for relevant information.
        3.  An answer will be generated based *only* on the handbook's content.
        """
    )
    
    # Cloud storage management
    if USE_CLOUD_SERVICES:
        st.header("Cloud Storage")
        if st.button("Upload Handbook to Cloud"):
            try:
                local_path = "data/MANE_GRADUATE_HANDBOOK.pdf"
                if os.path.exists(local_path):
                    cloud_path = "documents/MANE_GRADUATE_HANDBOOK.pdf"
                    st.session_state.storage_manager.upload_file(local_path, cloud_path)
                    st.success(f"Handbook uploaded to cloud storage!")
                else:
                    st.error("Handbook file not found locally")
            except Exception as e:
                st.error(f"Upload failed: {e}")
        
        if st.button("List Cloud Documents"):
            try:
                files = st.session_state.storage_manager.list_files("documents/")
                if files:
                    st.write("Documents in cloud storage:")
                    for file in files:
                        st.write(f"- {file}")
                else:
                    st.write("No documents found in cloud storage")
            except Exception as e:
                st.error(f"Failed to list files: {e}")

# --- Chat Interface ---
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about the MANE handbook"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Save to cloud if enabled
    if USE_CLOUD_SERVICES:
        st.session_state.firestore_manager.add_message(
            st.session_state.session_id, "user", prompt
        )

    # Get bot response
    with st.spinner("Searching the handbook and generating an answer..."):
        response, sources = st.session_state.chatbot.get_response(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
            
            # Display sources in an expander
            if sources:
                with st.expander("View Sources"):
                    for i, doc in enumerate(sources):
                        st.write(f"**Source {i+1}**")
                        st.write(f"From: *{doc.metadata.get('source', 'N/A')}*")
                        st.info(f"{doc.page_content}")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Save to cloud if enabled
    if USE_CLOUD_SERVICES:
        sources_data = []
        if sources:
            for doc in sources:
                sources_data.append({
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get('source', 'N/A')
                })
        st.session_state.firestore_manager.add_message(
            st.session_state.session_id, "assistant", response, sources_data
        )

# --- Session Management ---
if USE_CLOUD_SERVICES and st.sidebar.button("New Chat Session"):
    st.session_state.session_id = st.session_state.firestore_manager.create_chat_session()
    st.session_state.messages = []
    st.rerun()

if USE_CLOUD_SERVICES and st.sidebar.button("View Chat History"):
    sessions = st.session_state.firestore_manager.get_user_sessions("anonymous")
    if sessions:
        st.sidebar.write("Recent chat sessions:")
        for session in sessions[:5]:  # Show last 5 sessions
            st.sidebar.write(f"- {session['created_at'].strftime('%Y-%m-%d %H:%M')} ({session['message_count']} messages)")
    else:
        st.sidebar.write("No chat history found") 