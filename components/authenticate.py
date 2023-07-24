import os
import streamlit as st
import pandas as pd


# ------------------------------------
# Read constants from environment file
# ------------------------------------
USERS_CSV_PATH="./content/user.csv"

# ------------------------------------
# Initialise Streamlit state variables
# ------------------------------------
def initialise_st_state_vars():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

# ----------------------------------
# Check user credentials
# ----------------------------------
def check_user_credentials(username, password):
    users_df = pd.read_csv(USERS_CSV_PATH)
    user_row = users_df[(users_df['username'] == username) & (users_df['password'] == password)]

    if not user_row.empty:
        st.session_state["authenticated"] = True
        st.experimental_rerun()
        return True
    else:
        return False

# -----------------------------
# Login form
# -----------------------------
def login_form():
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Log In"):
        if check_user_credentials(username, password):
            st.success("Logged in successfully.")
        else:
            st.error("Invalid username or password.")

# -----------------------------
# Logout button
# -----------------------------
def logout_button():
    if st.sidebar.button("Log Out"):
        st.session_state["authenticated"] = False
        st.session_state["user_groups"] = []
        st.success("Logged out successfully.")
