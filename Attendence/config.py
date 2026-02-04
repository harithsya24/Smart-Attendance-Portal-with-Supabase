# Attendence/config.py
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_env(var_name, default=None):
    try:
        if hasattr(st, "secrets") and var_name in st.secrets:
            return st.secrets[var_name]
    except  Exception:
        pass
    
    return os.getenv(var_name, default)