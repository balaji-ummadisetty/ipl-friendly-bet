import streamlit as st
from database import get_user, add_user

def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = get_user(username)
        if user and user[2] == password:  # user[2] is password
            st.session_state['user'] = user
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")

def logout():
    if st.button("Logout"):
        st.session_state.pop('user', None)
        st.rerun()

def is_logged_in():
    return 'user' in st.session_state

def is_admin():
    return is_logged_in() and st.session_state['user'][3] == 'admin'

def is_member():
    return is_logged_in() and st.session_state['user'][3] == 'member'

def register_member(username, password):
    return add_user(username, password, 'member')