# auth.py
import streamlit as st

CREDENTIALS = {
    "GFT_USER": {
        "password": "GFT2024!",
        "user_id": "GFT_001",
        "is_admin": False
    },
    "ADMIN": {
        "password": "admin2024!",
        "user_id": "ADMIN_001",
        "is_admin": True
    }
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["is_admin"] = False

    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            st.title("Login to Talent Discovery")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if (username in CREDENTIALS and 
                    CREDENTIALS[username]["password"] == password):
                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = CREDENTIALS[username]["user_id"]
                    st.session_state["is_admin"] = CREDENTIALS[username]["is_admin"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            return False
    return True