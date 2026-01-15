import streamlit as st

from utils.nav import top_nav

top_nav()

st.set_page_config("App Suite", page_icon="🧰")

st.title("App Suite")
st.write("Choose a tool from the left sidebar.")

st.markdown("""
    ### Tools
    - Background Remover   
    - Extension Formatter
""")
