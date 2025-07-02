# app.py
import streamlit as st

st.set_page_config(page_title="Mobile App", layout="centered")

st.markdown("<h1 style='text-align: center;'>📱 Simple Mobile App</h1>", unsafe_allow_html=True)

name = st.text_input("Enter your name")
btn = st.button("Greet Me")

if btn and name:
    st.success(f"Hello, {name}! Welcome to your mobile app 🚀")
