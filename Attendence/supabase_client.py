# Attendence/supabase_client.py
from .clients import create_supabase_client, create_github_client

supabase= None
try:
    supabase = create_supabase_client()
except Exception:
    supabase = None