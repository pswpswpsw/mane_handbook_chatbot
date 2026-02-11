import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

# --- Configuration ---
DB_PATH = "chroma_db"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",'all-MiniLM-L6-v2')
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-8b-instruct:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

class Chatbot:
    def __init__(self):
        """Initializes the chatbot by setting up the RAG chain."""
        self.chain = self._setup_chain()

    def _setup_chain(self):
        """Configures and returns the retrieval chain."""
        # 1. Load the local vector database
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

        # 2. Set up the LLM through OpenRouter
        if not OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. Please set it in your .env file. "
                "Get your API key from https://openrouter.ai/"
            )
        
        llm = ChatOpenAI(
            model=OPENROUTER_MODEL,
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base=OPENROUTER_BASE_URL,
            temperature=0.3,
            max_tokens=1024
        )

        # 3. Create a prompt template
        # This is the most important part. It instructs the LLM to answer *only* based on the context.
        system_prompt = (
            "You are a factual, helpful assistant for the RPI MANE department, focused on answering questions about the graduate program.\n"
            "By strict instructions, you must answer based ONLY on the provided context below.\n"
            "If the answer is not in the context, say 'I'm sorry, I cannot find the answer to that in the graduate student handbook.'\n"
            "Do not fabricate or infer information.\n"
            "\n"
            "Context:\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        # 4. Create the chain
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        return rag_chain

    def get_response(self, query):
        """
        Gets a response from the chatbot for a given query.
        Returns the answer and the source documents.
        """
        if not self.chain:
            return "Chatbot is not initialized.", []
        
        try:
            response = self.chain.invoke({"input": query})
            return response.get("answer"), response.get("context", [])
        except Exception as e:
            return f"An error occurred: {e}", []

# Example usage (for testing)
if __name__ == "__main__":
    bot = Chatbot()
    
    # Example query
    test_query = "What are the requirements for the PhD qualifying exam?"
    print(f"Testing with query: '{test_query}'")
    
    answer, sources = bot.get_response(test_query)
    
    print("\n--- Answer ---")
    print(answer)
    
    print("\n--- Sources ---")
    if sources:
        for i, doc in enumerate(sources):
            print(f"Source {i+1}:")
            # print(f"  Content: {doc.page_content[:200]}...") # Uncomment to see content
            print(f"  Source: {doc.metadata.get('source', 'N/A')}")
    else:
        print("No sources found.")