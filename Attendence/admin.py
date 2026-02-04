# Attendance/admin.py
import streamlit as st
import pandas as pd
from github import GithubException

from .clients import create_supabase_client, create_github_client
from .utils import current_est_date
from .config import get_env
from .logger import get_logger

logger = get_logger(__name__)

# ---------- SETUP ----------
def setup_clients():
    supabase = create_supabase_client()
    gh, repo = create_github_client()
    admin_user = get_env("ADMIN_USERNAME")
    admin_password = get_env("ADMIN_PASSWORD")
    return supabase, gh, repo, admin_user, admin_password

# ---------- AUTH ----------
def admin_login(admin_user, admin_password):
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if st.session_state["admin_logged_in"]:
        return

    with st.sidebar.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == admin_user and password == admin_password:
                st.session_state["admin_logged_in"] = True
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ---------- SIDEBAR ----------
def sidebar_controls(supabase):
    try:
        with st.sidebar:
            st.markdown("## Create Class")
            class_input = st.text_input("New Class Name")

            if st.button("Add Class", key="add_class_btn") and class_input.strip():
                exists = (
                    supabase.table("classroom_settings")
                    .select("*")
                    .eq("class_name", class_input)
                    .execute()
                    .data
                )

                if exists:
                    st.warning("Class already exists.")
                else:
                    supabase.table("classroom_settings").insert(
                        {
                            "class_name": class_input,
                            "code": "1234",
                            "daily_limit": 10,
                            "is_open": False,
                        }
                    ).execute()
                    st.success(f"Class '{class_input}' added.")
                    st.experimental_rerun()

            if st.button("Logout", key="logout_btn"):
                st.session_state["admin_logged_in"] = False
                st.experimental_rerun()

            st.markdown("## Delete Class")
            delete_target = st.text_input("Class Name to Delete", key="delete_input")
            confirm = st.text_input("Type 'DELETE' to confirm", key="confirm_delete_input")

            if st.button("Delete Class", key="delete_class_btn") and delete_target.strip():
                if confirm == "DELETE":
                    for table in ["attendance", "roll_map", "classroom_settings"]:
                        supabase.table(table).delete().eq(
                            "class_name", delete_target
                        ).execute()
                    st.success(f"Class '{delete_target}' deleted.")
                    st.experimental_rerun()
                else:
                    st.warning("Type 'DELETE' to confirm deletion.")

    except Exception as e:
        logger.exception("Sidebar error")
        st.error("An error occurred.")

# ---------- CLASS CONTROLS ----------
def class_controls(supabase):
    try:
        classes = supabase.table("classroom_settings").select("*").execute().data
    except Exception:
        logger.exception("Fetch classes failed")
        st.error("Could not fetch classes.")
        st.stop()

    if not classes:
        st.info("No classes available.")
        st.stop()

    selected_class = st.selectbox(
        "Select Class",
        [c["class_name"] for c in classes],
        key="select_class"
    )

    config = next((c for c in classes if c["class_name"] == selected_class), None)
    if not config:
        st.error("Class config missing.")
        st.stop()

    st.markdown(f"**Code:** `{config['code']}`")
    st.markdown(f"**Daily Limit:** {config['daily_limit']}")

    is_open = config.get("is_open", False)
    other_open = [c["class_name"] for c in classes if c.get("is_open") and c["class_name"] != selected_class]

    st.subheader("Attendance Controls")
    st.info(f"Status: {'Open' if is_open else 'Closed'}")

    col1, col2 = st.columns(2)

    # Open Attendance
    with col1:
        if st.button("Open Attendance", key="open_attendance_btn"):
            if other_open:
                st.warning(f"Cannot open. Already open: {', '.join(other_open)}")
            else:
                # Optional: close all other classes automatically
                supabase.table("classroom_settings").update({"is_open": False}).neq("class_name", selected_class).execute()
                supabase.table("classroom_settings").update({"is_open": True}).eq("class_name", selected_class).execute()
                st.success(f"Attendance for '{selected_class}' is now OPEN.")
                st.experimental_rerun()

    # Close Attendance
    with col2:
        if st.button("Close Attendance", key="close_attendance_btn"):
            supabase.table("classroom_settings").update({"is_open": False}).eq("class_name", selected_class).execute()
            st.success(f"Attendance for '{selected_class}' is now CLOSED.")
            st.experimental_rerun()

    # Update Settings
    with st.expander("Update Settings"):
        new_code = st.text_input("New Code", value=config["code"], key="new_code_input")
        new_limit = st.number_input("Daily Limit", min_value=1, value=config["daily_limit"], key="new_limit_input")

        if st.button("Save Settings", key="save_settings_btn"):
            supabase.table("classroom_settings").update({"code": new_code, "daily_limit": new_limit}).eq("class_name", selected_class).execute()
            st.success("Class settings updated.")
            st.experimental_rerun()

    return selected_class

# ---------- MATRIX ----------
def show_matrix_and_push(supabase, repo, selected_class):
    try:
        records = supabase.table("attendance").select("*").eq("class_name", selected_class).execute().data
    except Exception:
        logger.exception("Attendance fetch failed")
        st.error("Could not fetch records.")
        return

    if not records:
        st.info("No attendance data.")
        return

    df = pd.DataFrame(records)
    df["status"] = "P"

    pivot_df = df.pivot_table(
        index=["roll_number", "name"],
        columns="date",
        values="status",
        aggfunc="first",
        fill_value="A",
    )

    st.dataframe(pivot_df, width="stretch")

    st.download_button(
        "Download Attendance CSV",
        pivot_df.to_csv().encode(),
        f"{selected_class}_attendance.csv",
        "text/csv",
    )

    if not st.button("Push to GitHub", key="push_github_btn"):
        return

    if repo is None:
        st.error("GitHub not configured.")
        return

    filename = f"records/attendance_{selected_class}_{current_est_date():%Y%m%d}.csv"
    content = pivot_df.to_csv().encode()
    message = f"Update attendance for {selected_class}"
    branch = "main"

    try:
        existing = repo.get_contents(filename, ref=branch)
        repo.update_file(filename, message, content, existing.sha, branch=branch)
        st.success("Updated GitHub file.")
    except GithubException as e:
        if e.status == 404:
            repo.create_file(filename, message, content, branch=branch)
            st.success("Created new GitHub file.")
        else:
            logger.error(e)
            st.error("GitHub error.")
    except Exception:
        logger.exception("GitHub push failed")
        st.error("Push failed.")

# ---------- MAIN ----------
def show_admin_panel():
    st.set_page_config(page_title="Attendance Admin", layout="wide")
    st.title("Attendance Administration Panel")

    try:
        supabase, gh, repo, admin_user, admin_password = setup_clients()
    except Exception:
        st.error("Client setup failed.")
        return

    admin_login(admin_user, admin_password)
    sidebar_controls(supabase)

    selected_class = class_controls(supabase)
    if selected_class:
        show_matrix_and_push(supabase, repo, selected_class)
