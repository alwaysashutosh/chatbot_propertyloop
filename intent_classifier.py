from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from enum import Enum

class Intent(Enum):
    DATA_LOOKUP = "DATA_LOOKUP"
    AGGREGATION = "AGGREGATION"
    COMPARISON = "COMPARISON"
    EXPLANATION = "EXPLANATION"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

class IntentClassifier:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=api_key)
        self.chain = self._create_chain()

    def _create_chain(self):
        system_prompt = (
            "You are a helpful assistant for a financial chatbot. Your task is to classify the user's intent "
            "into one of the following categories:\n"
            "- DATA_LOOKUP: simple lookups, counts, finding values, filtering data (e.g., 'count holdings for X', 'show trades for Y').\n"
            "- AGGREGATION: summing values, averages, min/max finding.\n"
            "- COMPARISON: comparing two funds, portfolios, or securities.\n"
            "- EXPLANATION: asking 'why', 'how', or for general explanations of the data.\n"
            "- OUT_OF_SCOPE: questions unrelated to financial data, holdings, or trades.\n\n"
            "Return ONLY the category name. Do not add any punctuation or extra text."
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{query}"),
            ]
        )
        
        return prompt | self.llm | StrOutputParser()

    def classify(self, query):
        try:
            result = self.chain.invoke({"query": query})
            intent_str = result.strip().upper()
            
            # Safe fallbacks if LLM returns something weird, though prompt instructs strictness
            if "DATA_LOOKUP" in intent_str: return Intent.DATA_LOOKUP
            if "AGGREGATION" in intent_str: return Intent.AGGREGATION
            if "COMPARISON" in intent_str: return Intent.COMPARISON
            if "EXPLANATION" in intent_str: return Intent.EXPLANATION
            
            # Default to OUT_OF_SCOPE if we can't map it, or if it explicitly says so
            if "OUT_OF_SCOPE" in intent_str: return Intent.OUT_OF_SCOPE
            
            return Intent.OUT_OF_SCOPE
            
        except Exception as e:
            print(f"Error classifying intent: {e}")
            # Fallback for reliability: assume data lookup if failed, or handle gracefully
            return Intent.DATA_LOOKUP
