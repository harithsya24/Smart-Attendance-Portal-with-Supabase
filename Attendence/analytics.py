# Attendence/analytics.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from .clients import create_supabase_client
from .logger import get_logger

logger = get_logger(__name__)

def show_analytics_panel():
    st.title("Attendance Analytics")
    
    try:
        supabase = create_supabase_client()
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        st.error("Could not connect to the database.")
        return
    
    try: 
        class_list_response = supabase.table("classroom_settings").select("class_name").execute()
        class_list = [item['class_name'] for item in class_list_response.data] if class_list_response.data else []
    except Exception:
        logger.error("Failed to fetch class list from Supabase.")
        st.error("Could not fetch class list.")
        return
    
    if not class_list:
        st.info("No classes found.")
        return

    selected_class = st.selectbox("Select Class", class_list, key="analytics_class")

    if st.button("Close Class", key="close_class_btn"):
        supabase.table("classroom_settings") \
            .update({"is_open": False}) \
            .eq("class_name", selected_class) \
            .execute()
        st.success(f"{selected_class} closed.")
        st.rerun()

    
    selected_class = st.selectbox("Select Class", class_list, key="analytics_class_select")

    
    try:
        data = supabase.table("attendance").select("*").eq("class_name", selected_class).execute()
    except Exception:
        logger.error("Failed to fetch attendance data from Supabase.")
        st.error("Could not fetch attendance data.")
        return
    
    if not data or not data.data:
        st.warning("No attendance data found for the selected class.")
        return
    
    df = pd.DataFrame(data.data)
    if 'status' not in df.columns:
        df['status'] = 'P'
    pivot_df = df.pivot_table(index=['roll_number','name'], columns='date', values='status', aggfunc='first', fill_value='A')
    pivot_df.columns.name = None
    
    st.dataframe(pivot_df,use_container_width='stretch')
    
    date_cols = pivot_df.columns[2:]
    pivot_df['Present_Count'] = pivot_df[date_cols].apply(lambda row: sum(val == 'P' for val in row if val == 'P'), axis=1)
    pivot_df['Attendance %'] = (pivot_df['Present_Count'] / len(date_cols) * 100).round(2)
    
    st.subheader("Attendance Count(Top 30)")
    top_df = pivot_df[['name','Present_Count']].nlargest(30, 'Present_Count').set_index('name')
    st.bar_chart(top_df)
    
    st.subheader("Top 3 Students:")
    st.table(pivot_df.sort_values("Attendance %", ascending=False).head(3)[['name', 'Attendance %']].set_index('name'))
    
    st.subheader("Bottom 3 Students:")
    st.table(pivot_df.sort_values("Attendance %").head(3)[['name', 'Present_Count', 'Attendance %']].set_index('name'))
    
    st.subheader("Filter by Attendance Range")
    min_val, max_val = float(pivot_df['Attendance %'].min()), float(pivot_df['Attendance %'].max())
    selected_range = st.slider("Select Attendance Percentage Range",0.0, 100.0, value=(min_val, max_val),step=1.0)
    
    filtered_df = pivot_df[(pivot_df['Attendance %'] >= selected_range[0]) & (pivot_df['Attendance %'] <= selected_range[1])]
    st.markdown(f"Showing {len(filtered_df)} students with attendance between {selected_range[0]}% and {selected_range[1]}%")
    st.dataframe(filtered_df[['name', 'Present_Count', 'Attendance %']].set_index('name'), use_container_width='stretch') 
    
    try:
        flattened = pivot_df[date_cols].values.flatten()
        present = sum(val == 'P' for val in flattened)
        absent = sum(val == 'A' for val in flattened)
        
        fig, ax = plt.subplots()
        ax.pie([present, absent], labels=['Present', 'Absent'], autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FF5722'])
        ax.axis('equal')
        st.pyplot(fig)
    except Exception:
        logger.error("Failed to generate attendance pie chart.")
        st.error("Could not generate attendance pie chart.")    
        
    