# auth.py
import streamlit as st

CREDENTIALS = {
    "GFT_USER": "GFT2024!"
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            st.title("Login to Talent Discovery")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted and username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.rerun()  # Add this line to refresh the page
            return False
    return True