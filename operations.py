import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# --- DATABASE EXTENSION ---
def init_ops_db():
    conn = sqlite3.connect('school_core.db', check_same_thread=False)
    c = conn.cursor()
    
    # 1. Student Profiles
    c.execute('''CREATE TABLE IF NOT EXISTS student_profiles 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, dob TEXT, 
                  enrollment_date TEXT, class_name TEXT, contact TEXT)''')
    
    # 2. Academic: Timetable & Grades
    c.execute('''CREATE TABLE IF NOT EXISTS grades 
                 (id INTEGER PRIMARY KEY, student_id INTEGER, subject TEXT, 
                  score INTEGER, term TEXT)''')
    
    # 3. Library System
    c.execute('''CREATE TABLE IF NOT EXISTS books 
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, status TEXT DEFAULT 'Available')''')
    c.execute('''CREATE TABLE IF NOT EXISTS library_logs 
                 (id INTEGER PRIMARY KEY, book_id INTEGER, student_id INTEGER, 
                  issue_date TEXT, return_date TEXT, fine REAL DEFAULT 0.0)''')
    
    conn.commit()
    conn.close()

# --- MODULE 1: STUDENT MANAGEMENT ---
def student_management():
    st.header("👤 Student Management")
    menu = ["Enrollment", "Profile Records", "Digital ID Card"]
    choice = st.tabs(menu)

    with choice[0]:
        st.subheader("New Enrollment")
        # Assuming user is already created in 'users' table
        user_id = st.number_input("Enter User ID from Core", min_value=1)
        dob = st.date_input("Date of Birth", min_value=date(2005, 1, 1))
        class_name = st.selectbox("Assign Class", ["Grade 10-A", "Grade 11-B", "Grade 12-C"])
        contact = st.text_input("Parent/Guardian Contact")
        
        if st.button("Complete Profile"):
            conn = sqlite3.connect('school_core.db')
            c = conn.cursor()
            c.execute("INSERT INTO student_profiles (user_id, dob, enrollment_date, class_name, contact) VALUES (?,?,?,?,?)",
                      (user_id, str(dob), str(date.today()), class_name, contact))
            conn.commit()
            st.success("Student profile records updated!")

    with choice[1]:
        st.subheader("Search Records")
        conn = sqlite3.connect('school_core.db')
        df = pd.read_sql_query("SELECT * FROM student_profiles", conn)
        st.dataframe(df, use_container_width=True)

    with choice[2]:
        st.subheader("ID Card Generator")
        s_id = st.number_input("Enter Student ID for ID Card", step=1)
        if st.button("Preview ID Card"):
            # Mock-up of a digital ID card
            st.markdown(f"""
            <div style="border: 2px solid #0e1117; border-radius: 10px; padding: 20px; width: 300px; background-color: #f0f2f6; color: black;">
                <h3 style="text-align: center;">EDUMASTER 2026</h3>
                <hr>
                <p><b>ID:</b> {s_id}</p>
                <p><b>Status:</b> Active Student</p>
                <p><b>Valid Until:</b> Dec 2026</p>
            </div>
            """, unsafe_allow_html=True)

# --- MODULE 2: ACADEMIC MANAGEMENT ---
def academic_management():
    st.header("📚 Academic & Curriculum")
    tab1, tab2, tab3 = st.tabs(["Timetabling", "Grade Book", "Exam Schedule"])
    
    with tab1:
        st.write("Current Week Timetable")
        schedule = {
            "Time": ["08:00", "09:30", "11:00"],
            "Monday": ["Math", "Physics", "English"],
            "Tuesday": ["History", "Chemistry", "Math"]
        }
        st.table(pd.DataFrame(schedule))

    with tab2:
        st.subheader("Input Grades")
        s_id = st.number_input("Student ID", key="grade_sid")
        subject = st.selectbox("Subject", ["Mathematics", "Science", "History"])
        score = st.slider("Score", 0, 100)
        if st.button("Save Grade"):
            st.success(f"Grade {score} recorded for Student {s_id}")

# --- MODULE 3: LIBRARY SYSTEM ---
def library_system():
    st.header("📖 Library Management")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Book Inventory")
        # Quick Add
        new_book = st.text_input("Book Title")
        author = st.text_input("Author")
        if st.button("Add to Catalog"):
            conn = sqlite3.connect('school_core.db')
            c = conn.cursor()
            c.execute("INSERT INTO books (title, author) VALUES (?,?)", (new_book, author))
            conn.commit()
            st.info("Book cataloged.")

    with col2:
        st.subheader("Issue/Return")
        book_id = st.number_input("Book ID", step=1)
        student_id = st.number_input("Student ID", step=1, key="lib_sid")
        if st.button("Issue Book"):
            st.warning(f"Book {book_id} issued to Student {student_id}. Due in 14 days.")

# --- INTEGRATION WITH CORE ---
# In your main app, you would simply call these based on the user's role.