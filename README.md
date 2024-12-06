# AI-Powered Talent Discovery Assistant

A Streamlit application for processing resumes and finding candidates using AI-powered semantic search and LLM reranking.

## Features

- PDF resume processing
- AI-powered resume chunking
- Semantic search capabilities
- LLM-based candidate reranking
- Multi-query support
- Secure authentication

## Tech Stack

- Python 3.8+
- Streamlit
- Google Generative AI (Gemini)
- PyPDF2
- pandas
- scipy
- numpy

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
pip install streamlit pandas numpy scipy PyPDF2 google-generativeai
```

4. Configure API key:
- Rename `config.py.example` to `config.py`
- Add your Gemini API key

## Usage

1. Start application:
```bash
streamlit run main.py
```

2. Login credentials:
- Username: GFT_USER
- Password: GFT2024!

3. Features:
- Upload and process PDFs
- Add multiple search queries
- View ranked candidates
- Export results to CSV

## Project Structure

```
talent_discovery/
├── main.py           # Main Streamlit app
├── auth.py           # Authentication
├── config.py         # Configuration
├── processors/       # Core processing
│   ├── pdf.py       # PDF handling
│   └── llm.py       # LLM operations
└── utils/           # Utilities
    └── search.py    # Semantic search
```

## License

MAS050

## Contact

For questions or support, please open an issue on GitHub.
