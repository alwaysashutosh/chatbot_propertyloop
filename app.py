import pandas as pd
import re
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict
import os

app = FastAPI()

HOLDINGS_PATH = 'holdings.csv'
TRADES_PATH = 'trades.csv'

h_df = None
t_df = None

def load_data():
    global h_df, t_df
    try:
        if not os.path.exists(HOLDINGS_PATH) or not os.path.exists(TRADES_PATH):
             print("DATA FILES MISSING")
             return

        holdings = pd.read_csv(HOLDINGS_PATH)
        trades = pd.read_csv(TRADES_PATH)
        
        holdings.columns = holdings.columns.str.strip()
        trades.columns = trades.columns.str.strip()
        
        for col in ['Quantity', 'Price', 'Principal', 'PL_YTD', 'Qty']:
            if col in holdings.columns:
                holdings[col] = pd.to_numeric(holdings[col], errors='coerce')
            if col in trades.columns:
                trades[col] = pd.to_numeric(trades[col], errors='coerce')
                
        h_df = holdings
        t_df = trades
        print("Data Loaded Successfully")
    except Exception as e:
        print(f"Error loading data: {e}")

load_data()

def classify_and_parse(question):
    q_lower = question.lower()
    
    intent_metadata = {
        "intent": "UNKNOWN",
        "filters": {},
        "table": "holdings",
        "agg": None,
        "sort_col": None
    }
    
    if any(k in q_lower for k in ["performed better", "profit", "loss", "p&l"]):
        intent_metadata["intent"] = "PERFORMANCE"
        intent_metadata["sort_col"] = "PL_YTD"
        intent_metadata["target_col"] = "PortfolioName"
        return intent_metadata
        
    if any(k in q_lower for k in ["total number", "count", "how many"]):
        intent_metadata["intent"] = "AGGREGATION"
        intent_metadata["agg"] = "count"
        
        if "trades" in q_lower:
            intent_metadata["table"] = "trades"
        else:
            intent_metadata["table"] = "holdings"
            
        match = re.search(r"for\s+(?:the\s+|a\s+)?([\w\s\-]+?)(?:$|\?|\sfund)", q_lower)
        if match:
            raw_ent = match.group(1).strip()
            if "given" not in raw_ent:
                intent_metadata["filters"]["PortfolioName"] = raw_ent
        return intent_metadata
        
    # Fact
    if "custodian" in q_lower:
        intent_metadata["intent"] = "FACT"
        intent_metadata["target_col"] = "CustodianName"
        
        match = re.search(r"of\s+(?:the\s+|a\s+)?([\w\s\-]+?)(?:$|\?)", q_lower)
        if match:
            raw_ent = match.group(1).strip()
            intent_metadata["filters"]["PortfolioName"] = raw_ent
        return intent_metadata
        
    return intent_metadata

def execute_query(metadata, h_df, t_df):
    if h_df is None or t_df is None:
        return "Sorry can not find the answer (Data not loaded)"

    df = t_df if metadata["table"] == "trades" else h_df
    result_df = df.copy()
    
    # Filters
    for col, val in metadata["filters"].items():
        if col not in result_df.columns:
            return "Sorry can not find the answer"
        mask = result_df[col].astype(str).str.contains(val, case=False, regex=False)
        result_df = result_df[mask]
        
    if result_df.empty:
        return "Sorry can not find the answer"
        
    intent = metadata.get("intent")
    
    try:
        if intent == "PERFORMANCE":
            if "PL_YTD" not in result_df.columns or "PortfolioName" not in result_df.columns:
                 return "Sorry can not find the answer"
            grouped = result_df.groupby("PortfolioName")["PL_YTD"].sum().reset_index()
            grouped = grouped.sort_values(by="PL_YTD", ascending=False)
            if grouped.empty: return "Sorry can not find the answer"
            return f"{grouped.iloc[0]['PortfolioName']}"
            
        elif intent == "AGGREGATION":
            return f"{len(result_df)}"
            
        elif intent == "FACT":
            target = metadata.get("target_col")
            if target and target in result_df.columns:
                answers = result_df[target].unique()
                return ", ".join(map(str, answers))
            else:
                return "Sorry can not find the answer"
    except:
        return "Sorry can not find the answer"
        
    return "Sorry can not find the answer"

# --- API Models ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str



@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Empty message")
    
    metadata = classify_and_parse(request.message)
    
    if metadata["intent"] == "UNKNOWN":
        return ChatResponse(response="Sorry can not find the answer")
        
    answer = execute_query(metadata, h_df, t_df)
    return ChatResponse(response=str(answer))


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    return FileResponse('static/index.html')


@app.get("/style.css")
async def read_css():
    return FileResponse('static/style.css')

@app.get("/script.js")
async def read_js():
    return FileResponse('static/script.js')

if __name__ == "__main__":
    import uvicorn
    if not os.path.exists("static/index.html"):
        print("WARNING: static/index.html not found!")
    
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
