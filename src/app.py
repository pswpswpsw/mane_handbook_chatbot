import streamlit as st
import os

# Fix for ChromaDB on Streamlit Cloud (requires pysqlite3-binary)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from chatbot import Chatbot

# --- Page Configuration ---
st.set_page_config(
    page_title="MANE Handbook Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("MANE Graduate Handbook Chatbot 🤖")
st.caption("Powered by local, open-source models. Your data stays on your machine.")

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

# Initialize chat history
if "messages" not in st.session_state:
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
    st.header("How to Use")
    st.markdown(
        """
        1.  Type your question in the chat box below.
        2.  The chatbot will search the handbook for relevant information.
        3.  An answer will be generated based *only* on the handbook's content.
        """
    )

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
