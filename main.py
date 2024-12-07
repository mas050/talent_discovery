# main.py
import streamlit as st
from auth import check_login
from processors.pdf import PDFProcessor
from processors.llm import LLMProcessor
from utils.search import SemanticSearch
import pandas as pd
from utils.database import UsageTracker
from datetime import datetime, timedelta

def main():
    if not check_login():
        return

    with st.sidebar:
        navigation_options = ["Resume Processing", "Resume Query"]
        if st.session_state.get("is_admin", False):
            navigation_options.append("Admin Dashboard")
        
        app_mode = st.radio("Navigation", navigation_options)

    if app_mode == "Resume Processing":
        process_resumes()
    elif app_mode == "Resume Query":
        query_resumes()
    elif app_mode == "Admin Dashboard" and st.session_state.get("is_admin", False):
        show_admin_dashboard()
    else:
        st.error("Unauthorized access")

def show_usage_stats():
    if st.session_state.get("logged_in") and st.session_state.get("user_id"):
        tracker = UsageTracker()
        user_id = st.session_state["user_id"]
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("Usage Statistics")
        total_cost = tracker.get_total_cost(user_id)
        st.sidebar.metric("Total Cost ($)", f"{total_cost:.4f}")
        
        if st.sidebar.button("View Detailed Usage"):
            st.subheader("Usage Details")
            usage = tracker.get_user_usage(user_id)
            if usage:
                df = pd.DataFrame(usage, columns=[
                    'id', 'user_id', 'timestamp', 'operation_type',
                    'prompt_tokens', 'completion_tokens', 'model', 'cost'
                ])
                st.dataframe(df)
            else:
                st.info("No usage data available")

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    tracker = UsageTracker()
    users = tracker.get_all_users()
    
    if not users:
        st.warning("No usage data recorded in the database")
        total_records = tracker.conn.execute('SELECT COUNT(*) FROM llm_usage').fetchone()[0]
        st.write(f"Total records in database: {total_records}")
        return
        
    # Add "All Users" option to the list
    user_options = ["All Users"] + users
    selected_user = st.selectbox("Select User", user_options)
    
    default_start = datetime.now().date() - timedelta(days=30)
    default_end = datetime.now().date()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From date", default_start)
    with col2:
        end_date = st.date_input("To date", default_end)

    # Modify query based on selection
    if selected_user == "All Users":
        usage_data = tracker.get_all_usage(start_date, end_date)
    else:
        usage_data = tracker.get_user_usage(selected_user, start_date, end_date)
    
    if not usage_data:
        st.info("No usage data found for selected period")
        return

    df = pd.DataFrame(usage_data, columns=[
        'id', 'user_id', 'timestamp', 'operation_type', 
        'prompt_tokens', 'completion_tokens', 'model', 'cost'
    ])
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", f"${df['cost'].sum():.4f}")
    with col2:
        st.metric("Total Operations", len(df))
    with col3:
        st.metric("Total Tokens", df['prompt_tokens'].sum() + df['completion_tokens'].sum())

    # Usage breakdown tabs
     # Usage breakdown tabs
    tab1, tab2, tab3 = st.tabs(["Operation Summary", "Daily Trend", "Detailed Logs"])
    
    with tab1:
        st.subheader("Usage by Operation Type")
        op_summary = df.groupby('operation_type').agg({
            'cost': 'sum',
            'prompt_tokens': 'sum',
            'completion_tokens': 'sum'
        }).reset_index()
        st.dataframe(op_summary)

    with tab2:
        st.subheader("Daily Usage Trend")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily_usage = df.groupby('date')['cost'].sum().reset_index()
        # Replace line_chart with a regular dataframe view
        st.write("Daily Cost Breakdown:")
        st.dataframe(
            daily_usage.sort_values('date', ascending=False),
            column_config={
                "date": "Date",
                "cost": st.column_config.NumberColumn(
                    "Cost",
                    format="$%.4f"
                )
            }
        )

    with tab3:
        st.subheader("Detailed Usage Logs")
        st.dataframe(df.sort_values('timestamp', ascending=False))

    # Export functionality
    if st.button("Export Usage Data"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"usage_report_{selected_user}_{start_date}_{end_date}.csv",
            "text/csv"
        )

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

def display_results(results):
    if results:
        st.subheader("High Potential Candidates")
        st.dataframe(results["candidates"])
        
        st.subheader("Analysis")
        st.text_area("LLM Analysis", results["analysis"], height=300)

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
