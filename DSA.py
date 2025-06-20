import streamlit as st
import pandas as pd
from datetime import datetime
import os
import altair as alt

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

st.set_page_config(page_title="Tetron Disaster Support App", layout="wide")
st.title("🖘 Tetron Disaster Emergency Support System")

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

    # Additional Reporting
    st.markdown("---")
    st.subheader("📦 Stock Request Overview")
    supply_counts = data['Supplies Needed'].str.get_dummies(sep=", ").sum().sort_values(ascending=False)
    st.bar_chart(supply_counts)

    st.subheader("💰 Budget Estimation")
    unit_cost = {
        "Food": 10,
        "Water": 5,
        "Baby Supplies": 15,
        "Hygiene Kit": 12,
        "Medical Kit": 20,
        "Blanket": 8
    }

    total_cost = 0
    supply_cost_data = []

    for item, count in supply_counts.items():
        cost = count * unit_cost.get(item, 0)
        total_cost += cost
        supply_cost_data.append({"Item": item, "Quantity": count, "Total Cost (MYR)": cost})

    cost_df = pd.DataFrame(supply_cost_data)
    st.dataframe(cost_df)

    st.metric("Estimated Total Budget Needed (MYR)", f"RM {total_cost:.2f}")

    st.subheader("📈 Delivery Status Report")
    delivery_chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Request Status:N', title='Request Status'),
        y=alt.Y('count():Q', title='Number of Requests'),
        color='Request Status:N'
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(delivery_chart)

    st.subheader("📅 Requests Over Time")
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
    daily_requests = data.groupby(data['Timestamp'].dt.date).size().reset_index(name='Request Count')
    st.line_chart(daily_requests.set_index('Timestamp'))
