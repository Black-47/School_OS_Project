import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE EXTENSION ---
def init_admin_db():
    conn = sqlite3.connect('school_core.db', check_same_thread=False)
    c = conn.cursor()
    
    # 1. Staff & HR Table
    c.execute('''CREATE TABLE IF NOT EXISTS staff 
                 (id INTEGER PRIMARY KEY, full_name TEXT, role TEXT, 
                  salary REAL, leave_balance INTEGER, join_date TEXT)''')
    
    # 2. Finance: Fee Structure & Invoices
    c.execute('''CREATE TABLE IF NOT EXISTS fees 
                 (id INTEGER PRIMARY KEY, student_id INTEGER, fee_type TEXT, 
                  amount REAL, status TEXT, due_date TEXT)''')
    
    conn.commit()
    conn.close()

# --- MODULE 1: STAFF & HR ---
def hr_management():
    st.header("👔 Staff & Human Resources")
    tab1, tab2, tab3 = st.tabs(["Staff Profiles", "Leave Management", "Payroll"])

    with tab1:
        st.subheader("Register New Staff Member")
        with st.form("staff_reg"):
            name = st.text_input("Full Name")
            pos = st.selectbox("Position", ["Teacher", "Accountant", "Security", "Janitor"])
            sal = st.number_input("Monthly Salary ($)", min_value=0.0)
            if st.form_submit_button("Add Staff"):
                conn = sqlite3.connect('school_core.db')
                c = conn.cursor()
                c.execute("INSERT INTO staff (full_name, role, salary, leave_balance, join_date) VALUES (?,?,?,?,?)",
                          (name, pos, sal, 15, str(datetime.now().date())))
                conn.commit()
                st.success(f"Record created for {name}")

    with tab2:
        st.subheader("Leave Requests")
        st.info("Currently monitoring 15 standard annual leave days per staff member.")
        # Simplified view of staff and their remaining leave
        conn = sqlite3.connect('school_core.db')
        df = pd.read_sql_query("SELECT full_name, role, leave_balance FROM staff", conn)
        st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("Payroll Processing")
        st.write("Generate monthly salary slips based on base pay.")
        conn = sqlite3.connect('school_core.db')
        staff_df = pd.read_sql_query("SELECT id, full_name, salary FROM staff", conn)
        if not staff_df.empty:
            selected_staff = st.selectbox("Select Staff Member", staff_df['full_name'])
            row = staff_df[staff_df['full_name'] == selected_staff].iloc[0]
            
            st.code(f"""
            PAYROLL SLIP - {datetime.now().strftime('%B %Y')}
            ------------------------------------------
            Employee: {row['full_name']} (ID: {row['id']})
            Base Salary: ${row['salary']:,.2f}
            Tax (10%):  -${(row['salary'] * 0.1):,.2f}
            ------------------------------------------
            NET PAY:    ${(row['salary'] * 0.9):,.2f}
            """)
        else:
            st.warning("No staff found in records.")

# --- MODULE 2: FINANCE & FEES ---
def finance_management():
    st.header("💰 Finance & Fees")
    tab1, tab2 = st.tabs(["Invoice Generation", "Financial Reports"])

    with tab1:
        st.subheader("Create Student Invoice")
        with st.form("fee_form"):
            s_id = st.number_input("Student ID", min_value=1)
            f_type = st.selectbox("Fee Category", ["Tuition", "Library", "Transport", "Exam Fee"])
            amt = st.number_input("Amount ($)", min_value=0.0)
            due = st.date_input("Due Date")
            if st.form_submit_button("Generate Invoice"):
                conn = sqlite3.connect('school_core.db')
                c = conn.cursor()
                c.execute("INSERT INTO fees (student_id, fee_type, amount, status, due_date) VALUES (?,?,?,?,?)",
                          (s_id, f_type, amt, 'Unpaid', str(due)))
                conn.commit()
                st.success(f"Invoice generated for Student #{s_id}")

    with tab2:
        st.subheader("School Financial Health")
        conn = sqlite3.connect('school_core.db')
        fees_df = pd.read_sql_query("SELECT * FROM fees", conn)
        
        if not fees_df.empty:
            total_rev = fees_df[fees_df['status'] == 'Paid']['amount'].sum()
            pending_rev = fees_df[fees_df['status'] == 'Unpaid']['amount'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Collected Revenue", f"${total_rev:,.2f}")
            col2.metric("Outstanding Fees", f"${pending_rev:,.2f}", delta="-Pending")
            
            st.write("Full Transaction Ledger:")
            st.dataframe(fees_df, use_container_width=True)
        else:
            st.write("No financial data available.")

# --- HELPER: LOGIC FOR ONLINE PAYMENTS (Conceptual) ---
def process_payment_logic(invoice_id):
    """
    In a real 2026 app, you would integrate Stripe or PayPal API here.
    For this build, we simulate a successful transaction.
    """
    conn = sqlite3.connect('school_core.db')
    c = conn.cursor()
    c.execute("UPDATE fees SET status='Paid' WHERE id=?", (invoice_id,))
    conn.commit()
    conn.close()