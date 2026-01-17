# PropertyLoop Assignment - Financial RAG Chatbot

A Retrieval-Augmented Generation (RAG) based financial chatbot that enables natural language querying of portfolio holdings and trading data.

## 📋 Project Overview

This project implements an intelligent chatbot system that allows users to interact with financial portfolio data through conversational AI. Built with Python, Flask, and the Groq API, it combines traditional data processing with modern LLM capabilities.

## 🏗️ Architecture

### Core Components

1. **Data Layer**
   - `holdings.csv` - Portfolio position data (~174KB)
   - `trades.csv` - Transaction history data (~143KB)
   - Processed using pandas for structured data manipulation

2. **RAG Engine** (`rag_engine.py`)
   - Vector storage using FAISS for efficient similarity search
   - Custom mock embeddings (384-dimension hash-based vectors)
   - Groq API integration with `llama-3.1-8b-instant` model
   - Document ingestion and retrieval pipeline

3. **Intent Classifier** (`intent_classifier.py`)
   - Categorizes queries into 5 types:
     - DATA_LOOKUP (simple data retrieval)
     - AGGREGATION (summaries and calculations)
     - COMPARISON (performance comparisons)
     - EXPLANATION (analytical questions)
     - OUT_OF_SCOPE (non-financial queries)

4. **Business Logic** (`bot_logic.py`)
   - Hybrid processing approach
   - Deterministic logic for simple queries
   - RAG processing for complex analysis
   - Graceful fallback mechanisms

5. **Web Interface** (`app.py`)
   - Flask REST API backend
   - Static HTML/CSS/JS frontend
   - Real-time chat functionality

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key

### Installation

1. **Clone and Navigate**
```bash
cd "c:\Users\ashut\OneDrive\Desktop\ashutosh\PropertyLoop Assignment\chatbot"
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
Create/edit `.env` file:
```env
GROQ_API_KEY=gsk_your_api_key_here
```

4. **Run the Application**
```bash
python app.py
```

5. **Access the Interface**
Open browser to `http://127.0.0.1:5000`

## 💡 Usage Examples

### Sample Queries

**Portfolio Analysis:**
```
"Total number of holdings for Garfield"
"Which funds performed better based on Profit and Loss"
"What portfolio has trades but no holdings"
```

**Performance Insights:**
```
"Show me the top 5 performing funds"
"Compare portfolio returns year-to-date"
"What are the worst performing assets?"
```

### API Usage

```bash
curl -X POST "http://127.0.0.1:5000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Total number of holdings for Garfield"}'
```

## 🔧 Technical Details

### Current Implementation

**LLM Model:** `llama-3.1-8b-instant` (Groq)
**Embedding Strategy:** Custom hash-based mock embeddings
**Vector Store:** FAISS
**Framework:** LangChain
**Web Framework:** Flask

### Migration History

The project successfully migrated from Google Gemini to Groq API, overcoming:
- Model deprecation issues
- Dependency conflicts
- Version compatibility challenges
- Embedding library limitations

## 📁 Project Structure

```
PropertyLoop Assignment/
├── chatbot/
│   ├── rag_engine.py          # RAG implementation
│   ├── bot_logic.py           # Business logic
│   ├── intent_classifier.py   # Query classification
│   ├── app.py                 # Flask application
│   ├── requirements.txt       # Dependencies
│   ├── .env                   # Environment variables
│   └── static/                # Frontend files
│       ├── index.html
│       ├── script.js
│       └── style.css
├── holdings.csv               # Portfolio data
├── trades.csv                 # Transaction data
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Model Settings
Currently uses `llama-3.1-8b-instant` with:
- Temperature: 0 (deterministic responses)
- Context window: 131,072 tokens
- Max completion tokens: 131,072

## 🛠️ Development

### Adding New Features

1. **New Query Types**: Extend `Intent` enum in `intent_classifier.py`
2. **Custom Processing**: Add methods to `DataChatbot` class in `bot_logic.py`
3. **UI Enhancements**: Modify files in `static/` directory

### Testing
```bash
python test_chatbot.py
```

## 📊 Performance Metrics

- **Documents Ingested**: ~1,671 records from CSV files
- **Response Time**: Sub-second for simple queries
- **Accuracy**: High for deterministic lookups, contextual for complex analysis
- **Scalability**: Handles growing dataset sizes efficiently

## 🔒 Security Considerations

- API keys stored in `.env` file (gitignored)
- Input validation on all user queries
- Secure Flask configuration for production deployment
- Rate limiting considerations for API usage

## 🚨 Troubleshooting

### Common Issues

1. **"Model decommissioned" errors**
   - Solution: Update to current Groq models in code
   
2. **Dependency conflicts**
   - Solution: Use exact package versions from requirements.txt
   
3. **Embedding errors**
   - Solution: System uses mock embeddings as fallback

### Debug Mode
Enable debug logging by setting `debug=True` in `app.py`

## 📈 Future Enhancements

- [ ] Integration with live market data APIs
- [ ] Advanced visualization dashboards
- [ ] Multi-user authentication system
- [ ] Enhanced portfolio analytics
- [ ] Mobile-responsive interface
- [ ] Export functionality for reports

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📄 License

This project is for educational/demo purposes.

## 🙏 Acknowledgments

- Groq for providing the LLM API
- LangChain for RAG framework components
- FAISS for vector storage capabilities

## 📞 Support

For issues or questions, please open an issue in the repository.

---
*Built with ❤️ using Python, Flask, and Groq API*
