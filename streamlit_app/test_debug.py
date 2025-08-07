import streamlit as st

st.set_page_config(page_title="Test", layout="wide")
st.title("🎭 Vakta AI - Debug Test")
st.write("✅ If you can see this, Streamlit is working!")

if st.button("Test Button"):
    st.success("✅ Working!")
