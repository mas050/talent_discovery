# main.py
import streamlit as st
from auth import check_login
from processors.pdf import PDFProcessor
from processors.llm import LLMProcessor
from utils.search import SemanticSearch
import pandas as pd

def main():
    if not check_login():
        return

    st.title("AI-Powered Talent Discovery Assistant")
    
    with st.sidebar:
        app_mode = st.radio("Navigation", ["Resume Processing", "Resume Query"])

    if app_mode == "Resume Processing":
        process_resumes()
    else:
        query_resumes()

def process_resumes():
    st.header("Resume Processing")
    uploaded_pdfs = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
    uploaded_csv = st.file_uploader("Upload historical CSV (optional)", type="csv")
    
    if uploaded_pdfs and st.button("Process Files"):
        pdf_processor = PDFProcessor()
        llm_processor = LLMProcessor()
        
        if uploaded_csv:
            historical_data = pd.read_csv(uploaded_csv)
        else:
            historical_data = pd.DataFrame(columns=["pdf_file_name", "candidate_name", "resume_section_content", "embedded_chunk"])
        
        for pdf_file in uploaded_pdfs:
            result = pdf_processor.process_file(pdf_file, llm_processor)
            if result is not None:
                historical_data = pd.concat([historical_data, result], ignore_index=True)
        
        st.success("Processing completed!")
        st.dataframe(historical_data)
        st.download_button(
            "Download Results",
            historical_data.to_csv(index=False),
            "processed_resumes.csv",
            "text/csv"
        )

def query_resumes():
    st.header("Resume Query")
    uploaded_file = st.file_uploader("Upload processed CSV", type="csv")
    
    if uploaded_file:
        search = SemanticSearch()
        if "queries" not in st.session_state:
            st.session_state["queries"] = []
            
        query_input = st.text_input("Enter a query criterion:")
        if st.button("+ Add Query") and query_input:
            st.session_state["queries"].append(query_input)
            
        if st.session_state["queries"]:
            st.subheader("Current Query Criteria")
            for i, query in enumerate(st.session_state["queries"]):
                st.write(f"{i+1}. {query}")
                
        if st.button("Search Candidates"):
            results = search.search_candidates(
                pd.read_csv(uploaded_file),
                st.session_state["queries"]
            )
            display_results(results)

if __name__ == "__main__":
    main()
