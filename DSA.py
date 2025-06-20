import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Load employee data
@st.cache_data
def load_employee_data():
    return pd.read_csv("employee_data.csv")

# Load request data from CSV (no caching to reflect live updates)
def load_data():
    if os.path.exists("requests.csv"):
        return pd.read_csv("requests.csv")
    else:
        return pd.DataFrame(columns=[
            'Timestamp', 'Employee ID', 'Name', 'Department', 'Phone Number', 'Email',
            'Location', 'Status', 'Supplies Needed', 'Additional Notes', 'Request Status'
        ])

# Load existing or initialize data
data = load_data()
employee_df = load_employee_data()

st.set_page_config(page_title="WaieFYP Disaster Support App", layout="wide")
st.title("🖘 WAIE Disaster Emergency Support System")

menu = st.sidebar.selectbox("Select Role", ["Employee", "Admin"])

# ------------------- EMPLOYEE INTERFACE -------------------
if menu == "Employee":
    st.header("📋 Submit Your Emergency Request")

    emp_id = st.text_input("Enter Your Employee ID")

    if emp_id:
        emp_info = employee_df[employee_df['Employee ID'] == emp_id]
        if not emp_info.empty:
            emp_info_row = emp_info.iloc[0]
            name = emp_info_row['Name']
            dept = emp_info_row['Department']
            phone = emp_info_row['Phone Number']
            email = emp_info_row['Email']

            st.write("### 👤 Employee Information")
            st.write(emp_info)

            with st.form("emergency_form"):
                location = st.text_input("Your Current Location")
                status = st.selectbox("Your Situation", ["Safe", "Evacuated", "In Need of Help"])

                supplies = st.multiselect(
                    "Supplies Needed",
                    ["Food", "Water", "Baby Supplies", "Hygiene Kit", "Medical Kit", "Blanket"]
                )

                notes = st.text_area("Additional Notes")
                submit = st.form_submit_button("Submit Request")

                if submit:
                    new_data = pd.DataFrame({
                        'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        'Employee ID': [emp_id],
                        'Name': [name],
                        'Department': [dept],
                        'Phone Number': [phone],
                        'Email': [email],
                        'Location': [location],
                        'Status': [status],
                        'Supplies Needed': [", ".join(supplies)],
                        'Additional Notes': [notes],
                        'Request Status': ["Pending"]
                    })

                    updated_data = pd.concat([data, new_data], ignore_index=True)
                    updated_data.to_csv("requests.csv", index=False)
                    st.success("Your request has been submitted.")

            st.markdown("---")
            st.subheader("🗂️ Your Previous Requests")
            if not data.empty:
                st.dataframe(data[data['Employee ID'] == emp_id])
        else:
            st.warning("Employee ID not found. Please check again.")

# ------------------- ADMIN INTERFACE -------------------
if menu == "Admin":
    st.header("🚰 Admin Dashboard - Manage Requests")

    # Reload fresh data without cache
    data = load_data()

    if data.empty:
        st.warning("No requests submitted yet.")
    else:
        st.dataframe(data)

        selected_index = st.selectbox("Select request to update:", data.index)
        current_status = data.loc[selected_index, 'Request Status']

        new_status = st.selectbox("Update Status", ["Pending", "Approved", "Delivered", "Rejected"], index=["Pending", "Approved", "Delivered", "Rejected"].index(current_status))
        if st.button("Update Status"):
            data.at[selected_index, 'Request Status'] = new_status
            data.to_csv("requests.csv", index=False)
            st.success("Request status updated.")

    st.markdown("---")
    st.subheader("📊 Summary Report")
    st.write(data['Request Status'].value_counts())
