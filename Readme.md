# Data-Grounded Financial Chatbot

A robust, data-grounded chatbot capable of answering questions about financial holdings and trades strictly from provided CSV data (`holdings.csv` and `trades.csv`). The system features a Jupyter Notebook for interactive exploration and a FastAPI backend with a web interface.

## 🚀 Features

*   **Strict Data Adherence**: Answers are derived *only* from the provided datasets.
*   **Robust Fallback**: Returns "Sorry can not find the answer" for invalid queries, missing data, or out-of-scope topics.
*   **Intent Classification**: Supports three core query types:
    *   **Direct Fact**: "Custodian of Heather"
    *   **Aggregation**: "Total number of trades for Platpot Fund"
    *   **Performance**: "Which funds performed better based on Profit & Loss?"
*   **Interfaces**:
    *   **Jupyter Notebook**: Full logic walkthrough and testing (`financial_chatbot.ipynb`).
    *   **Web Application**: Professional chat interface powered by FastAPI (`app.py`).

## 📂 Project Structure

```
.
├── app.py                   # FastAPI backend application
├── chatbot.py               # Core logic script (logic also embedded in app.py)
├── financial_chatbot.ipynb  # Interactive Jupyter Notebook
├── holdings.csv             # Source data for holdings
├── trades.csv               # Source data for trades
├── static/                  # Frontend assets
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md                # Project documentation
```

## 🛠️ Prerequisites

*   Python 3.8+
*   `pip` package manager

## 📦 Installation

1.  **Clone the repository** (or download the files).
2.  **Install dependencies**:
    ```bash
    pip install pandas fastapi uvicorn
    ```

## 🖥️ Usage

### Option 1: Web Interface (FastAPI)

1.  Run the server:
    ```bash
    uvicorn app:app --port 8000
    ```
    *(Note: Add `--reload` for development mode)*

2.  Open your browser and navigate to:
    ```
    http://localhost:8000
    ```

3.  Type questions into the chat window:
    *   *Example*: "Total number of trades for Platpot Fund"

### Option 2: Jupyter Notebook

1.  Open `financial_chatbot.ipynb` in Jupyter Lab, Jupyter Notebook, or VS Code.
2.  Run all cells to execute the logic and see the verification tests.

## 🔌 API Endpoints

*   `POST /api/chat`: Chat endpoint.
    *   **Payload**: `{"message": "Your question here"}`
    *   **Response**: `{"response": "Answer or Fallback message"}`

*   `GET /`: Serves the Web UI.

## 🛡️ Logic & Limitations

*   **Mock LLM**: The system uses a deterministic Rule-Based/Regex approach to simulate Intent Classification and Entity Extraction. This ensures reliability without requiring external API keys.
*   **Data Integrity**: The chatbot checks for the existence of columns and data before answering. If a fund name is not found or a column is missing, it triggers the fallback response.
