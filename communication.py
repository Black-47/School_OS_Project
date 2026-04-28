import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# --- DATABASE EXTENSION ---
def init_comm_db():
    conn = sqlite3.connect('school_core.db', check_same_thread=False)
    c = conn.cursor()
    # 1. Digital Notice Board
    c.execute('''CREATE TABLE IF NOT EXISTS notice_board 
                 (id INTEGER PRIMARY KEY, title TEXT, content TEXT, 
                  date_posted TEXT, priority TEXT)''')
    conn.commit()
    conn.close()

# --- MODULE 1: COMMUNICATION HUB ---
def communication_hub():
    st.header("📢 Communication Hub")
    tab1, tab2, tab3 = st.tabs(["Digital Notice Board", "Alert System", "Parent Portal"])

    with tab1:
        st.subheader("Post New Announcement")
        with st.form("notice_form"):
            title = st.text_input("Notice Title")
            content = st.text_area("Detailed Content")
            priority = st.select_slider("Priority Level", options=["Low", "Medium", "High"])
            if st.form_submit_button("Post to Board"):
                conn = sqlite3.connect('school_core.db')
                c = conn.cursor()
                c.execute("INSERT INTO notice_board (title, content, date_posted, priority) VALUES (?,?,?,?)",
                          (title, content, str(datetime.now().date()), priority))
                conn.commit()
                st.success("Announcement Live!")

    with tab2:
        st.subheader("🚀 Rapid Alert System (SMS/Email)")
        st.write("Send urgent broadcasts to specific groups.")
        target_group = st.multiselect("Select Recipients", ["All Parents", "All Teachers", "Grade 10 Only"])
        alert_msg = st.text_input("Short Alert Message (Max 160 chars)")
        if st.button("Simulate Broadcast"):
            # In a production environment, this would trigger an API like Twilio or SendGrid
            st.toast(f"Sending alert to {len(target_group)} groups...")
            st.success(f"Alert successfully queued for delivery.")

    with tab3:
        st.subheader("👨‍👩‍👧 Parent Portal Preview")
        st.info("This is what a parent sees when they log in.")
        # Simulating a parent checking their child's latest notice
        conn = sqlite3.connect('school_core.db')
        notices = pd.read_sql_query("SELECT * FROM notice_board ORDER BY id DESC LIMIT 2", conn)
        for _, note in notices.iterrows():
            with st.expander(f"📌 {note['title']} ({note['date_posted']})"):
                st.write(note['content'])
                st.caption(f"Priority: {note['priority']}")

# --- MODULE 2: REPORTS & ANALYTICS ---
def insights_dashboard():
    st.header("📊 System Insights & KPIs")
    
    # --- KPI MOCK DATA ---
    # In a real app, these would be calculated from the 'grades' and 'attendance' tables
    pass_rate = 84.5
    attendance_avg = 92.0
    revenue_target = 75.0 # 75% of fees collected
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg. Pass Rate", f"{pass_rate}%", delta="2.1%")
    col2.metric("Daily Attendance", f"{attendance_avg}%", delta="-0.5%")
    col3.metric("Fee Collection", f"{revenue_target}%", delta="10%")

    st.divider()

    # --- VISUAL TRENDS ---
    st.subheader("Attendance Trends (Last 7 Days)")
    chart_data = pd.DataFrame(
        np.random.randn(7, 2) / [10, 20] + [0.95, 0.90],
        columns=['Grade 10', 'Grade 11']
    )
    st.line_chart(chart_data)

    # --- DATA EXPORT FEATURE ---
    st.subheader("📄 Exportable Data")
    conn = sqlite3.connect('school_core.db')
    
    report_type = st.selectbox("Select Report to Generate", ["Student Records", "Financial Ledger", "Attendance History"])
    
    if report_type == "Student Records":
        query = "SELECT * FROM student_profiles"
    elif report_type == "Financial Ledger":
        query = "SELECT * FROM fees"
    else:
        query = "SELECT * FROM notice_board" # Placeholder
        
    df_to_export = pd.read_sql_query(query, conn)
    st.dataframe(df_to_export.head(5), use_container_width=True)
    
    # The 'Magic' Export Button
    csv = df_to_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Report as CSV",
        data=csv,
        file_name=f"school_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )