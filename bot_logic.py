import pandas as pd
import os

from rag_engine import RAGEngine
from intent_classifier import IntentClassifier, Intent

class DataChatbot:
    def __init__(self, holdings_path, trades_path):
        self.holdings_path = holdings_path
        self.trades_path = trades_path
        self.holdings_df = None
        self.trades_df = None
        
        # Load Pandas Data
        self.load_data()
        
        # Initialize AI Components
        print("Initializing RAG Engine... this may take a moment.")
        self.rag_engine = RAGEngine(holdings_path, trades_path)
        self.intent_classifier = IntentClassifier()
        print("Bot initialized.")

    def load_data(self):
        try:
            if os.path.exists(self.holdings_path):
                self.holdings_df = pd.read_csv(self.holdings_path)
            else:
                print(f"Error: {self.holdings_path} not found.")
            
            if os.path.exists(self.trades_path):
                self.trades_df = pd.read_csv(self.trades_path)
            else:
                print(f"Error: {self.trades_path} not found.")
                
        except Exception as e:
            print(f"Error loading data: {e}")

    def process_query(self, query):
        # 1. Classify Intent
        intent = self.intent_classifier.classify(query)
        print(f"Query: {query} | Detected Intent: {intent}")

        # 2. Route based on Intent
        if intent == Intent.DATA_LOOKUP or intent == Intent.AGGREGATION:
            # Try deterministic logic first
            response = self.handle_deterministic_query(query)
            if response: 
                return response
            # Fallback to RAG if deterministic logic fails to extract entities
            return self.rag_engine.query_llm(query)
            
        elif intent == Intent.COMPARISON or intent == Intent.EXPLANATION:
            # Use RAG
            return self.rag_engine.query_llm(query)
            
        elif intent == Intent.OUT_OF_SCOPE:
            return "I'm sorry, I can only answer questions related to your financial holdings and trades."
            
        else:
            return self.rag_engine.query_llm(query)

    def handle_deterministic_query(self, query):
        query_lower = query.lower()
        
        # Improved regex/keyword matching for legacy support
        if "total number of holdings" in query_lower or "number of holdings" in query_lower:
            return self.get_holdings_count(query)
        elif "total number of trades" in query_lower or "number of trades" in query_lower:
            return self.get_trades_count(query)
        elif "performed better" in query_lower and "profit and loss" in query_lower:
            # This is actually better served by RAG for "explanation" but if it's just a list
            # we can keep the pandas logic or return the raw data string for RAG to format.
            return self.get_fund_performance_summary()
            
        return None

    def get_holdings_count(self, query):
        if self.holdings_df is None:
            return "Holdings data not available."
        
        portfolios = self.holdings_df['PortfolioName'].unique()
        found_portfolio = self.extract_portfolio_from_query(query, portfolios)
        
        if found_portfolio:
            count = self.holdings_df[self.holdings_df['PortfolioName'] == found_portfolio].shape[0]
            return f"The total number of holdings for {found_portfolio} is {count}."
        return None

    def get_trades_count(self, query):
        if self.trades_df is None:
            return "Trades data not available."
            
        portfolios = self.trades_df['PortfolioName'].unique()
        found_portfolio = self.extract_portfolio_from_query(query, portfolios)
        
        if found_portfolio:
            count = self.trades_df[self.trades_df['PortfolioName'] == found_portfolio].shape[0]
            return f"The total number of trades for {found_portfolio} is {count}."
        return None

    def extract_portfolio_from_query(self, query, portfolios):
        # 1. Exact match search
        for p in portfolios:
            if p.lower() in query.lower():
                return p
        
        # 2. "for" keyword extraction
        if "for" in query.lower():
            potential_name = query.lower().split("for")[-1].strip()
            potential_name = potential_name.replace("?", "").replace(".", "")
            
            for p in portfolios:
                if potential_name in p.lower():
                    return p
        return None

    def get_fund_performance_summary(self):
        if self.holdings_df is None:
            return "Holdings data not available."
        
        if 'PL_YTD' not in self.holdings_df.columns:
             return "Profit and Loss data (PL_YTD) not found in holdings."

        try:
            self.holdings_df['PL_YTD'] = pd.to_numeric(self.holdings_df['PL_YTD'], errors='coerce')
            performance = self.holdings_df.groupby('PortfolioName')['PL_YTD'].sum().sort_values(ascending=False)
            
            top_funds = performance.head(5)
            response = "Top funds by YTD Profit/Loss:\n"
            for fund, pl in top_funds.items():
                response += f"- {fund}: {pl:,.2f}\n"
            return response
        except Exception as e:
            return f"Error calculating performance: {e}"
