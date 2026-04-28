import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

# --- DATABASE ENGINE ---
def get_db_connection():
    conn = sqlite3.connect('school_core.db', check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  full_name TEXT, role TEXT)''')
    # Notifications Table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications 
                 (id INTEGER PRIMARY KEY, target_role TEXT, message TEXT, 
                  created_at TEXT, created_by TEXT)''')
    
    # Create a default Admin if system is empty (Password: admin123)
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
                  ('admin', hashed_pw, 'System Administrator', 'Admin'))
    
    conn.commit()
    conn.close()

# --- AUTHENTICATION LOGIC ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    data = c.fetchone()
    conn.close()
    return data

# --- NOTIFICATION ENGINE ---
def send_notification(role, message, sender):
    conn = get_db_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO notifications (target_role, message, created_at, created_by) VALUES (?,?,?,?)",
              (role, message, timestamp, sender))
    conn.commit()
    conn.close()

def get_notifications(role):
    conn = get_db_connection()
    # Shows notifications for "All" or the user's specific role
    df = pd.read_sql_query("SELECT message, created_at, created_by FROM notifications WHERE target_role='All' OR target_role=?", 
                           conn, params=(role,))
    conn.close()
    return df

# --- MAIN INTERFACE ---
def main():
    st.set_page_config(page_title="EduMaster Core", layout="centered")
    init_db()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("🔐 School Portal Login")
        with st.form("login_form"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                res = login_user(user, pw)
                if res:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = res # (id, user, pass, name, role)
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
    else:
        user_name = st.session_state['user_info'][3]
        user_role = st.session_state['user_info'][4]
        
        st.sidebar.title(f"Welcome, {user_name}")
        st.sidebar.write(f"**Role:** {user_role}")
        
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

        # --- ROLE-BASED ACCESS CONTROL (RBAC) ---
        st.title(f"{user_role} Dashboard")
        
        # System-Wide Notifications Section
        st.subheader("📢 Announcements")
        notes = get_notifications(user_role)
        if not notes.empty:
            for i, row in notes.iterrows():
                st.info(f"**{row['created_at']}** | {row['message']} (via {row['created_by']})")
        else:
            st.write("No new notifications.")

        st.divider()

        # Dashboard Content based on Role
        if user_role == "Admin":
            admin_view()
        elif user_role == "Teacher":
            st.write("Welcome to the Teacher's Faculty Lounge. Grading tools loading...")
        elif user_role == "Student":
            st.write("Welcome to your Student Portal. Your assignments will appear here.")
        elif user_role == "Parent":
            st.write("Welcome, Guardian. Check your child's progress below.")

def admin_view():
    st.header("Admin Control Panel")
    tab1, tab2 = st.tabs(["User Management", "Send Broadcast"])
    
    with tab1:
        st.subheader("Register New User")
        with st.form("add_user"):
            new_user = st.text_input("Username")
            new_name = st.text_input("Full Name")
            new_pass = st.text_input("Temporary Password", type="password")
            new_role = st.selectbox("Role", ["Admin", "Teacher", "Student", "Parent"])
            if st.form_submit_button("Create User"):
                try:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
                              (new_user, hash_password(new_pass), new_name, new_role))
                    conn.commit()
                    st.success(f"Account for {new_name} created!")
                except:
                    st.error("Username already exists.")

    with tab2:
        st.subheader("Post System-Wide Notification")
        target = st.selectbox("Target Audience", ["All", "Admin", "Teacher", "Student", "Parent"])
        msg = st.text_area("Message Content")
        if st.button("Send Alert"):
            send_notification(target, msg, st.session_state['user_info'][1])
            st.success("Notification Sent!")

if __name__ == "__main__":
    main()