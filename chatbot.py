import pandas as pd
import re
from datetime import datetime

HOLDINGS_PATH = 'holdings.csv'
TRADES_PATH = 'trades.csv'

def load_data():
    try:
        holdings = pd.read_csv(HOLDINGS_PATH)
        trades = pd.read_csv(TRADES_PATH)
        
        holdings.columns = holdings.columns.str.strip()
        trades.columns = trades.columns.str.strip()
        
        cols_to_numeric = ['Quantity', 'Price', 'Principal', 'PL_YTD', 'Qty']
        for df in [holdings, trades]:
            for col in df.columns:
                if col in cols_to_numeric:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return holdings, trades
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def parse_question(question):
    q_lower = question.lower()
    
    result = {
        "intent": "UNKNOWN",
        "filters": {},
        "target_col": None,
        "aggregation": None,
        "sort_by": None,
        "table": None 
    }
    
    if "performed better" in q_lower or "profit & loss" in q_lower or "p&l" in q_lower:
        result["intent"] = "PERFORMANCE"
        result["table"] = "holdings"
        result["sort_by"] = "PL_YTD"
        result["target_col"] = "PortfolioName" 
        result["aggregation"] = "sum" 
        return result

    if "total number" in q_lower or "how many" in q_lower or "count" in q_lower:
        result["intent"] = "AGGREGATION"
        result["aggregation"] = "count"
        
        fund_match = re.search(r"for\s+(?:a|the)?\s*([a-zA-Z0-9\s]+?)(?:$|\?|fund)", q_lower)
        if fund_match:
            raw_fund = fund_match.group(1).strip()
            if "given fund" not in raw_fund:
                 result["filters"]["PortfolioName"] = raw_fund
        
        if "trades" in q_lower:
            result["table"] = "trades"
        elif "holdings" in q_lower:
            result["table"] = "holdings"
            
        return result

    if "custodian" in q_lower:
        result["intent"] = "FACT"
        result["target_col"] = "CustodianName"
        result["table"] = "holdings" 
        
        fund_match = re.search(r"of\s+(?:a|the)?\s*([a-zA-Z0-9\s]+?)(?:$|\?)", q_lower)
        if fund_match:
             raw_fund = fund_match.group(1).strip()
             result["filters"]["PortfolioName"] = raw_fund
        return result
        
    return result

def filter_dataframe(df, filters):
    if df is None: return None
    temp_df = df.copy()
    for col, val in filters.items():
        if col in temp_df.columns:
            mask = temp_df[col].astype(str).str.contains(val, case=False, regex=False)
            temp_df = temp_df[mask]
        else:
            return pd.DataFrame() 
    return temp_df

def answer_question(question, holdings_df, trades_df):
    parsed = parse_question(question)
    
    if parsed["intent"] == "UNKNOWN":
        return "Sorry can not find the answer"
    
    if parsed["table"] == "holdings":
        df = holdings_df
    elif parsed["table"] == "trades":
        df = trades_df
    else:
        df = holdings_df 

    filtered_df = filter_dataframe(df, parsed["filters"])
    
    if filtered_df is None or filtered_df.empty:
        return "Sorry can not find the answer"

    try:
        if parsed["intent"] == "PERFORMANCE":
            if "PL_YTD" not in filtered_df.columns:
                 return "Sorry can not find the answer"
            
            agg_df = filtered_df.groupby("PortfolioName")["PL_YTD"].sum().reset_index()
            agg_df = agg_df.sort_values(by="PL_YTD", ascending=False)
            
            if agg_df.empty:
                return "Sorry can not find the answer"
                
            best_fund = agg_df.iloc[0]["PortfolioName"]
            return f"The fund that performed better based on yearly Profit & Loss is {best_fund}."

        elif parsed["intent"] == "AGGREGATION":
            count = len(filtered_df)
            entity = parsed.get("table", "records")
            return f"Total number of {entity} is {count}."

        elif parsed["intent"] == "FACT":
            target_col = parsed["target_col"]
            if target_col not in filtered_df.columns:
                return "Sorry can not find the answer"
            
            values = filtered_df[target_col].unique()
            if len(values) == 0:
                return "Sorry can not find the answer"
            
            return f"{', '.join(map(str, values))}"
            
    except Exception as e:
        return "Sorry can not find the answer"

    return "Sorry can not find the answer"

if __name__ == "__main__":
    h_df, t_df = load_data()
    
    test_questions = [
        "Total number of trades for Platpot Fund",
        "Total number of holdings for Garfield", 
        "Which funds performed better depending on the yearly Profit & Loss of that fund",
        "Custodian of Heather",
        "Number of trades for UnknownFund", 
        "What is the capital of France?" 
    ]
    
    print("--- Test Run ---")
    for q in test_questions:
        print(f"Q: {q}")
        ans = answer_question(q, h_df, t_df)
        print(f"A: {ans}\n")
