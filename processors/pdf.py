# processors/pdf.py
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import camelot
import pdfplumber

class PDFProcessor:

    def extract_text(self, pdf_file):
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            row = [str(cell) if cell else "" for cell in row]
                            text += " | ".join(row) + "\n"
                    
                    # Extract regular text 
                    text += (page.extract_text() or "") + "\n"

                return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None

    def process_file(self, pdf_file, llm_processor):
        user_id = st.session_state.get("user_id")
        print(f"Current user_id: {user_id}")  # Debug print
        if not user_id:
            st.error("User not logged in")
            return None
            
        text = self.extract_text(pdf_file)
        if not text:
            return None
            
        condensed_text = llm_processor.preprocess_resume(text, user_id)
        sections = llm_processor.chunk_resume(condensed_text, user_id)
        if not sections:
            return None
            
        embeddings = [llm_processor.get_embedding(chunk) for chunk in sections['chunks']]
        
        return pd.DataFrame({
            "pdf_file_name": [pdf_file.name] * len(sections['chunks']),
            "candidate_name": [sections['name']] * len(sections['chunks']),
            "resume_section_content": sections['chunks'],
            "embedded_chunk": embeddings
        })
