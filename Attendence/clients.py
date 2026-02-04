# Attendence/client.py
from supabase import create_client
from github import Github
from .config import get_env
from .logger import get_logger

logger = get_logger(__name__)

def create_supabase_client():
    """Creates and returns a Supabase client instance."""
    try:
        supabase_url = get_env("SUPABASE_URL")
        supabase_key = get_env("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL or Key is not set in environment variables.")
        
        client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client created successfully.")
        return client
    except Exception as e:
        logger.exception(f"Error creating Supabase client: {e}")
        raise
    
def create_github_client():
    try:
        token = get_env("GITHUB_TOKEN") 
        username = get_env("GITHUB_USERNAME")
        repo_name = get_env("GITHUB_REPO_NAME")
        
        if not token or not username or not repo_name:
            logger.info("GitHub credentials are not fully set in environment variables.")
            return None, None
        gh = Github(token)
        repo = gh.get_user(username).get_repo(repo_name)
        return gh,repo
    except Exception:
        logger.exception("Error creating GitHub client.")
        raise
    