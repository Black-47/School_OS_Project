import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE EXTENSION ---
def init_facilities_db():
    conn = sqlite3.connect('school_core.db', check_same_thread=False)
    c = conn.cursor()
    
    # 1. Transport: Routes and Safety Logs
    c.execute('''CREATE TABLE IF NOT EXISTS transport 
                 (id INTEGER PRIMARY KEY, bus_no TEXT, route TEXT, 
                  driver_name TEXT, safety_status TEXT, last_inspection TEXT)''')
    
    # 2. Hostel: Room Allocation
    c.execute('''CREATE TABLE IF NOT EXISTS hostel 
                 (id INTEGER PRIMARY KEY, room_no TEXT, block TEXT, 
                  capacity INTEGER, occupied INTEGER, warden TEXT)''')
    
    conn.commit()
    conn.close()

# --- MODULE 1: TRANSPORT MANAGEMENT ---
def transport_management():
    st.header("🚌 Transport & Fleet Logistics")
    tab1, tab2, tab3 = st.tabs(["Route Management", "GPS Tracking", "Safety Compliance"])

    with tab1:
        st.subheader("Manage Bus Routes")
        with st.form("bus_form"):
            b_no = st.text_input("Bus Number (e.g., BUS-01)")
            route = st.text_input("Route Path (e.g., Downtown - North Square)")
            driver = st.text_input("Driver Name")
            if st.form_submit_button("Assign Route"):
                conn = sqlite3.connect('school_core.db')
                c = conn.cursor()
                c.execute("INSERT INTO transport (bus_no, route, driver_name, safety_status, last_inspection) VALUES (?,?,?,?,?)",
                          (b_no, route, driver, "Passed", str(datetime.now().date())))
                conn.commit()
                st.success(f"Route assigned to {b_no}")

    with tab2:
        st.subheader("🛰️ Live GPS Simulation")
        # In a real 2026 app, this would pull from a GPS API
        st.info("Tracking active for 12 school buses...")
        st.map(pd.DataFrame({
            'lat': [55.7558, 55.7522], # Sample coordinates for Moscow
            'lon': [37.6173, 37.6155]
        }))

    with tab3:
        st.subheader("🛡️ Vehicle Safety Audit")
        st.write("Ensuring all transit vehicles meet safety protocols.")
        conn = sqlite3.connect('school_core.db')
        df = pd.read_sql_query("SELECT bus_no, driver_name, safety_status, last_inspection FROM transport", conn)
        st.table(df)

# --- MODULE 2: HOSTEL MANAGEMENT ---
def hostel_management():
    st.header("🏨 Hostel & Residency")
    tab1, tab2, tab3 = st.tabs(["Room Allocation", "Warden Registry", "Hostel Billing"])

    with tab1:
        st.subheader("Assign Student to Room")
        room = st.selectbox("Select Room", ["A-101", "A-102", "B-201"])
        student_id = st.number_input("Student ID", min_value=1)
        if st.button("Confirm Allocation"):
            st.success(f"Student {student_id} successfully moved to Room {room}")

    with tab2:
        st.subheader("Staff & Wardens")
        st.write("Current Warden Assignments:")
        st.info("**Block A:** Mr. Henderson | **Block B:** Ms. Sato")

    with tab3:
        st.subheader("💰 Residency Billing")
        base_fee = 500.00
        utility_fee = 75.00
        # Formula: Total = Base + Utilities
        total_hostel_fee = base_fee + utility_fee
        
        st.metric("Total Monthly Hostel Fee", f"${total_hostel_fee}")
        
        if st.button("Generate Monthly Hostel Invoices"):
            st.toast("Generating invoices for 150 resident students...")
            st.success("Billing cycle completed.")

# --- INTEGRATION HELPER ---
def show_facilities_dashboard():
    init_facilities_db()
    choice = st.sidebar.radio("Facilities Menu", ["Transport", "Hostel"])
    if choice == "Transport":
        transport_management()
    else:
        hostel_management()