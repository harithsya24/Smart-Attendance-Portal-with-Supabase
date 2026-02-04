#student_main.py
import streamlit as st
from Attendence.student import show_student_panel
import pandas as pd 
from Attendence.clients import create_supabase_client
from datetime import datetime
import pytz

st.set_page_config(page_title="Student Dashboard", page_icon="🎓", layout="wide")

try:
    supabase = create_supabase_client()
except Exception as e:
    supabase = None
    st.error("Could not connect to the database.")
    st.stop()   
    
def current_est_time():
    est = pytz.timezone('America/New_York')
    return datetime.now(est)

st.markdown("""
            <h1 style='text-align: center; color: #2196F3;'>Smart Attendance Student Dashboard</h1>
            <hr style="border-top: 1px solid #bbb;"></br>
            """, unsafe_allow_html=True)    

tab1, tab2 = st.tabs(["Mark Attendance", "View My Attendance"])    

with tab1:
    show_student_panel()    
with tab2: 
    st.header("Check My Attendance Records")
    with st.form("view_attendance_form"):
        if supabase:
            try:
                class_list_response = supabase.table("classroom_settings").select("class_name").execute().data
                class_list = [entry['class_name'] for entry in class_list_response] if class_list_response else []
            except Exception:
                st.error("Could not fetch class list.")
                class_list = []
        else:
            class_list = []
            
        selected_class = st.selectbox("Select Class", class_list)
        roll_number = st.text_input("Enter Your Roll Number").strip()
        submit_button = st.form_submit_button("View My Attendance")
    
    if submit_button:
        if not roll_number:
            st.warning("Please enter your roll number.")
        else:
            if not supabase:
                st.error("Database connection is not available.")
            else:
                try:
                    records = (supabase.table("attendance").select("*").eq("class_name", selected_class).eq("roll_number", roll_number).execute().data)
                except Exception:
                    records = []
                
                if not records:
                    st.info("No attendance records found for the provided details.")
                else:
                    df = pd.DataFrame(records)
                    if 'status' not in df.columns:
                        df['status'] = 'P'
                    matrix = df.pivot_table(
                        index=['roll_number','name'], 
                        columns='date', 
                        values='status', 
                        aggfunc='first', 
                        fill_value='A'
                    ).reset_index()
                    matrix.columns.name = None
                    matrix = matrix.sort_values(by='roll_number')
                    st.dataframe(matrix,use_container_width='True')