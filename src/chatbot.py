import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA

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
        """Configures and returns the RetrievalQA chain."""
        # 1. Load the local vector database
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)

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
        template = """
        You are a factual, helpful assistant for the RPI MANE department, focused on answering questions about the graduate program. Follow these strict instructions:
        
1. Question Classification
If the question is about the graduate program:

Use only the provided graduate student handbook as your source.

If the answer is found in the handbook: respond with a clear, concise answer based strictly on that content.

If the answer is not in the handbook: reply with:

"I'm sorry, I cannot find the answer to that in the graduate student handbook."
You may then optionally add a general response based on verified, factual knowledge about the RPI MANE department — but do not speculate or assume.

If the question is not about the graduate program:

You may still respond based on known, factual information about the RPI MANE department.

Clearly state:

"This information is not from the graduate student handbook."

2. Style & Integrity
Be concise and answer the question directly.

Do not fabricate or infer information. If a fact is not supported by the handbook or verifiable knowledge, say so.

Always prioritize factual accuracy over completeness or helpfulness.



        CONTEXT:
        {context}

        QUESTION:
        {question}

        ANSWER:
        """
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])

        # 4. Create the RetrievalQA chain
        # This chain ties together the retriever (vector database) and the LLM.
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        return qa_chain

    def get_response(self, query):
        """
        Gets a response from the chatbot for a given query.
        Returns the answer and the source documents.
        """
        if not self.chain:
            return "Chatbot is not initialized.", []
        
        try:
            response = self.chain.invoke({"query": query})
            return response.get("result"), response.get("source_documents", [])
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