import streamlit as st
import sqlite3

# --- IMPORTING OUR MODULES ---
# (Note: In a real setup, these would be separate .py files)
# For this demo, ensure the functions from previous steps are available.

def main():
    st.set_page_config(
        page_title="FRB Academy | 2026", 
        page_icon="🏫", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 1. Initialize all databases
    # (Calls the init functions we wrote in previous modules)
    # init_db(), init_ops_db(), init_admin_db(), init_comm_db(), init_facilities_db()

    # 2. Authentication Check
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        show_login_screen()
    else:
        show_unified_dashboard()

def show_login_screen():
    st.title("🏫 FRB Academy")
    st.subheader("Login to access your workspace")
    
    with st.form("main_login"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Enter System"):
            # Using the core login logic we built in Module 1
            # res = login_user(user, pw)
            # if res:
            #     st.session_state['logged_in'] = True
            #     st.session_state['user_info'] = res
            #     st.rerun()
            
            # DEFAULT BYPASS FOR SETUP TESTING:
            if user == "admin" and pw == "admin123":
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = (1, 'admin', '...', 'Black', 'Admin')
                st.rerun()
            else:
                st.error("Access Denied")

def show_unified_dashboard():
    user_name = st.session_state['user_info'][3]
    user_role = st.session_state['user_info'][4]

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2940/2940651.png", width=100)
    st.sidebar.title(f"Hello, {user_name}")
    st.sidebar.info(f"Access Level: **{user_role}**")
    
    st.sidebar.divider()
    
    # Navigation logic based on role
    if user_role == "Admin":
        menu = ["🏠 Dashboard", "👥 Students", "📚 Academics", "💰 Finance & HR", "🚌 Facilities", "📢 Communication"]
    elif user_role == "Teacher":
        menu = ["🏠 Dashboard", "📚 Academics", "📢 Communication"]
    else:
        menu = ["🏠 Dashboard", "👨‍🎓 My Portal", "📢 Communication"]

    choice = st.sidebar.radio("Main Menu", menu)

    if st.sidebar.button("🔒 Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

    # --- ROUTING LOGIC ---
    if "🏠 Dashboard" in choice:
        st.title("System Overview")
        # show_kpi_metrics() from Module 4
        
    elif "👥 Students" in choice:
        # student_management() from Module 2
        st.write("Student Module Loaded...")

    elif "📚 Academics" in choice:
        # academic_management() from Module 2
        st.write("Academic Module Loaded...")

    elif "💰 Finance & HR" in choice:
        # hr_management() & finance_management() from Module 3
        st.write("Financial Module Loaded...")

    elif "🚌 Facilities" in choice:
        # transport_management() & hostel_management() from Module 5
        st.write("Facilities Module Loaded...")

    elif "📢 Communication" in choice:
        # communication_hub() from Module 4
        st.write("Communication Module Loaded...")

if __name__ == "__main__":
    main()
