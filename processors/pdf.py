# processors/pdf.py
from PyPDF2 import PdfReader
import pandas as pd
import streamlit as st

class PDFProcessor:
    def extract_text(self, pdf_file):
        try:
            reader = PdfReader(pdf_file)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return None

    def process_file(self, pdf_file, llm_processor):
        text = self.extract_text(pdf_file)
        if not text:
            return None
            
        sections = llm_processor.chunk_resume(text)
        if not sections:
            return None
            
        embeddings = [llm_processor.get_embedding(chunk) for chunk in sections['chunks']]
        
        return pd.DataFrame({
            "pdf_file_name": [pdf_file.name] * len(sections['chunks']),
            "candidate_name": [sections['name']] * len(sections['chunks']),
            "resume_section_content": sections['chunks'],
            "embedded_chunk": embeddings
        })
