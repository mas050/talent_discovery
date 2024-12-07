# AI-Powered Talent Discovery Assistant

An advanced application for processing resumes and finding candidates using AI-powered semantic search, LLM reranking, and usage tracking. Built with Streamlit and Google's Generative AI.

## Features

### Resume Processing
- PDF text extraction with table support
- AI-powered text preprocessing and chunking
- Semantic embeddings generation
- Intelligent resume summarization
- Batch processing support
- Historical data integration

### Resume Query System
- Multi-query support
- Semantic search capabilities
- LLM-based candidate reranking
- Detailed match analysis
- Custom similarity scoring

### Admin Dashboard
- User activity monitoring
- Usage statistics tracking
- Cost analysis
- Token consumption metrics
- Export capabilities
- Date-filtered reporting

## Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - Google Generative AI (Gemini)
  - Text embeddings
  - Semantic search
- **Data Processing**:
  - PyMuPDF/PDFPlumber (PDF processing)
  - pandas
  - numpy
  - scipy
- **Database**: SQLite
- **Authentication**: Custom user management

## Project Structure

```
talent_discovery/
├── main.py           # Main Streamlit application
├── auth.py           # Authentication system
├── config.py         # Configuration settings
├── models.py         # Data models
├── processors/       # Core processing modules
│   ├── pdf.py       # PDF handling
│   └── llm.py       # LLM operations
└── utils/           # Utility modules
    ├── search.py    # Semantic search
    └── database.py  # Usage tracking
```

## Setup

1. Clone repository:
```bash
git clone https://github.com/mas050/talent_discovery.git
cd talent_discovery
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

3. Install dependencies:
```bash
pip install streamlit pandas numpy scipy PyPDF2 google-generativeai pdfplumber
```

4. Configure environment:
- Rename `config.py.example` to `config.py`
- Add your Gemini API key

## Usage

### Starting the Application
```bash
streamlit run main.py
```

### User Types

#### Regular User
- Username: GFT_USER
- Access to:
  - Resume processing
  - Resume querying

#### Admin User
- Username: ADMIN
- Additional access to:
  - Usage dashboard
  - User statistics
  - Cost tracking
  - Usage exports

### Features Usage

1. **Resume Processing**
   - Upload single or multiple PDFs
   - Optional historical data integration
   - Download processed results

2. **Resume Query**
   - Multiple search criteria support
   - View ranked candidates
   - Detailed match analysis

3. **Admin Dashboard** (Admin only)
   - View per-user statistics
   - Monitor token usage
   - Track costs
   - Export usage reports

## Data Management

### Usage Tracking
- Tracks all LLM operations
- Records token usage
- Calculates costs
- Stores user activities

### Database Schema
```sql
CREATE TABLE llm_usage (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    model TEXT NOT NULL,
    cost REAL NOT NULL
)
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## License

MAS050
