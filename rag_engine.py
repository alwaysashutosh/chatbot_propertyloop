from langchain_community.vectorstores import FAISS
# Using mock embeddings for simplicity
class MockEmbeddings:
    def embed_documents(self, texts):
        # Return simple hash-based embeddings for demonstration
        import hashlib
        import numpy as np
        embeddings = []
        for text in texts:
            # Create a simple hash-based embedding
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            # Create a 384-dimensional vector (similar to sentence transformers)
            embedding = [(hash_val >> i) & 1 for i in range(384)]
            embeddings.append(np.array(embedding, dtype=float))
        return embeddings
    
    def embed_query(self, text):
        # Embed a single query
        import hashlib
        import numpy as np
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        embedding = [(hash_val >> i) & 1 for i in range(384)]
        return np.array(embedding, dtype=float)
    
    def __call__(self, texts):
        # Make the class callable for backward compatibility
        if isinstance(texts, str):
            return self.embed_query(texts)
        else:
            return self.embed_documents(texts)
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self, holdings_path, trades_path):
        self.holdings_path = holdings_path
        self.trades_path = trades_path
        self.vector_store = None
        self.retriever = None
        
        # Initialize LLM (now using Groq)
        api_key = os.getenv("GROQ_API_KEY")
        self.use_mock = False
        if not api_key:
            print("WARNING: GROQ_API_KEY not found in environment. Using mock responses for demo.")
            self.use_mock = True
            # Skip vector store initialization for demo mode
            self.ingest_data_demo_mode()
        else:
            try:
                self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=api_key)
                # If we get here, the API key worked, so proceed with normal initialization
                self.ingest_data()
            except Exception as e:
                print(f"Error initializing Google Gemini: {e}")
                self.use_mock = True
                # On error, use demo mode instead
                self.ingest_data_demo_mode()

    def ingest_data(self):
        print("Ingesting data for RAG...")
        documents = []
        
        # Process Holdings
        try:
            if os.path.exists(self.holdings_path):
                holdings_df = pd.read_csv(self.holdings_path)
                for _, row in holdings_df.iterrows():
                    # Create a text representation of the row
                    content = f"Holding Record: Portfolio {row.get('PortfolioName', 'N/A')} holds {row.get('Quantity', 'N/A')} of Security {row.get('SecurityId', 'N/A')}. " \
                              f"Market Value Base: {row.get('MV_Base', 'N/A')}. Price: {row.get('Price', 'N/A')}."
                    
                    metadata = {
                        "source": "holdings",
                        "portfolio": row.get('PortfolioName', 'Unknown'),
                        "security": row.get('SecurityId', 'Unknown')
                    }
                    documents.append(Document(page_content=content, metadata=metadata))
        except Exception as e:
            print(f"Error ingesting holdings: {e}")

        # Process Trades
        try:
            if os.path.exists(self.trades_path):
                trades_df = pd.read_csv(self.trades_path)
                for _, row in trades_df.iterrows():
                    # Create a text representation of the row
                    content = f"Trade Record: {row.get('TradeTypeName', 'Trade')} of {row.get('Quantity', 'N/A')} {row.get('SecurityId', 'N/A')} " \
                              f"for Portfolio {row.get('PortfolioName', 'N/A')}. Price: {row.get('Price', 'N/A')}. Status: {row.get('Status', 'N/A')}."
                    
                    metadata = {
                        "source": "trades",
                        "portfolio": row.get('PortfolioName', 'Unknown'),
                        "security": row.get('SecurityId', 'Unknown')
                    }
                    documents.append(Document(page_content=content, metadata=metadata))
        except Exception as e:
            print(f"Error ingesting trades: {e}")

        if documents and not self.use_mock:
            # Use mock embeddings
            embeddings = MockEmbeddings()
            self.vector_store = FAISS.from_documents(documents, embeddings)
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            print(f"Ingested {len(documents)} documents.")
        elif documents and self.use_mock:
            # In demo mode, we don't actually create embeddings but store the documents
            self.demo_documents = documents
            self.retriever = None  # We'll handle retrieval differently in demo mode
            print(f"Loaded {len(documents)} documents in demo mode.")
        else:
            print("No documents ingested.")

    def ingest_data_demo_mode(self):
        print("Running in demo mode - skipping vector store initialization.")
        self.retriever = None

    def query_llm(self, user_query, additional_context=""):
        
        if hasattr(self, 'use_mock') and self.use_mock:
            # Return a helpful demo response
            return f"Demo Mode: This would normally analyze your query '{user_query}' against the financial data. To get real responses, please configure a valid Google API key in the .env file."
        
        if not self.retriever:
            return "RAG system not initialized properly (no data)."

        # Create the chain
        system_prompt = (
            "You are a financial assistant chatbot. Use the following pieces of retrieved context to answer "
            "the question. Sorry, but I can't assist with that. If you don't know the answer, say that Sorry, I don't know. "
            "Use three sentences maximum and keep the answer concise."
            "\n\n"
            "{context}"
            "\n\n"
            "Additional Context from Data Analysis:\n"
            "{additional_context}"
        )
        
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)
        
        try:
            response = rag_chain.invoke({"input": user_query, "additional_context": additional_context})
            return response["answer"]
        except Exception as e:
            return f"Error during RAG query: {e}"
