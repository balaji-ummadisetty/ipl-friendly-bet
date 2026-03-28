import streamlit as st
from database import init_db, insert_matches, auto_close_predictions
from auth import login, logout, is_logged_in, is_admin, is_member
from admin import admin_dashboard
from member import member_dashboard

# Initialize DB and insert matches if not already
init_db()
insert_matches()
auto_close_predictions()  # auto-close any matches that have started

st.title("IPL Friendly Betting App")

if not is_logged_in():
    login()
else:
    logout()
    if is_admin():
        admin_dashboard()
    elif is_member():
        member_dashboard()
    else:
        st.error("Unknown role")