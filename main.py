import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Load existing employee data or create a new DataFrame
try:
    df = pd.read_csv('employees.csv')
except FileNotFoundError:
    df = pd.DataFrame(columns=['Employee ID', 'Name', 'Status', 'Timestamp'])

# Form for employee check-in/check-out
with st.form(key='employee_form'):
    employee_id = st.text_input('Employee ID')
    employee_name = st.text_input('Employee Name')
    status = st.selectbox('Status', ['In', 'Out'])
    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        if employee_id and employee_name:
            new_entry = pd.DataFrame({
                'Employee ID': [employee_id],
                'Name': [employee_name],
                'Status': [status],
                'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv('employees.csv', index=False)
            st.success('Data recorded successfully!')
        else:
            st.error('Please enter both Employee ID and Name.')

# Function to calculate hours
def calculate_hours(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    in_df = df[df['Status'] == 'In']
    out_df = df[df['Status'] == 'Out']
    
    merged_df = pd.merge(in_df, out_df, on='Employee ID', suffixes=('_In', '_Out'))
    merged_df['Hours'] = (merged_df['Timestamp_Out'] - merged_df['Timestamp_In']).dt.total_seconds() / 3600
    
    return merged_df[['Employee ID', 'Name_In', 'Hours']]

# Sidebar for navigation
st.sidebar.title('Dashboard Navigation')
selection = st.sidebar.radio("Go to", ["Employee List", "Analytics", "Dashboard"])

# Display employee data
if selection == "Employee List":
    st.subheader('Employee List')
    st.write(df)

# Analytics
elif selection == "Analytics":
    if not df.empty:
        st.subheader('Analytics')
        
        # Total Check-Ins and Check-Outs
        check_in_counts = df[df['Status'] == 'In'].groupby('Name').size()
        check_out_counts = df[df['Status'] == 'Out'].groupby('Name').size()
        
        st.write(f"Total Check-Ins: {check_in_counts.sum()}")
        st.write(f"Total Check-Outs: {check_out_counts.sum()}")

        # Average Working Hours
        hours_report = calculate_hours(df)
        if not hours_report.empty:
            avg_hours = hours_report['Hours'].mean()
            st.write(f"Average Working Hours: {avg_hours:.2f} hours")

        # Visualization: Check-In/Check-Out Counts
        fig, ax = plt.subplots()
        sns.barplot(x=check_in_counts.index, y=check_in_counts.values, ax=ax, color='green', label='Check-In')
        sns.barplot(x=check_out_counts.index, y=check_out_counts.values, ax=ax, color='red', label='Check-Out')

        ax.set_xlabel('Employee Name')
        ax.set_ylabel('Count')
        ax.set_title('Check-In/Check-Out Counts')
        ax.legend()

        st.pyplot(fig)

        # Visualization: Average Working Hours by Employee
        if not hours_report.empty:
            fig2, ax2 = plt.subplots()
            sns.barplot(x=hours_report['Name_In'], y=hours_report['Hours'], ax=ax2, color='blue')

            ax2.set_xlabel('Employee Name')
            ax2.set_ylabel('Hours')
            ax2.set_title('Average Working Hours by Employee')

            st.pyplot(fig2)

# Dashboard
elif selection == "Dashboard":
    st.subheader('Dashboard')
    
    if not df.empty:
        # Total Check-Ins and Check-Outs
        check_in_counts = df[df['Status'] == 'In'].groupby('Name').size()
        check_out_counts = df[df['Status'] == 'Out'].groupby('Name').size()
        
        # Average Working Hours
        hours_report = calculate_hours(df)
        if not hours_report.empty:
            avg_hours = hours_report['Hours'].mean()
            st.write(f"Average Working Hours: {avg_hours:.2f} hours")

        # Create interactive plots
        st.write("### Check-In/Check-Out Counts")
        check_in_plot = st.selectbox("Select Check-In/Check-Out Visualization", ["Bar Chart", "Pie Chart"])
        
        if check_in_plot == "Bar Chart":
            fig, ax = plt.subplots()
            sns.barplot(x=check_in_counts.index, y=check_in_counts.values, ax=ax, color='green', label='Check-In')
            sns.barplot(x=check_out_counts.index, y=check_out_counts.values, ax=ax, color='red', label='Check-Out')

            ax.set_xlabel('Employee Name')
            ax.set_ylabel('Count')
            ax.set_title('Check-In/Check-Out Counts')
            ax.legend()

            st.pyplot(fig)
        elif check_in_plot == "Pie Chart":
            fig, ax = plt.subplots()
            sizes = [check_in_counts.sum(), check_out_counts.sum()]
            labels = ['Check-In', 'Check-Out']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['green', 'red'])

            ax.set_title('Check-In/Check-Out Distribution')

            st.pyplot(fig)
        
        st.write("### Average Working Hours by Employee")
        if not hours_report.empty:
            fig2, ax2 = plt.subplots()
            sns.barplot(x=hours_report['Name_In'], y=hours_report['Hours'], ax=ax2, color='blue')

            ax2.set_xlabel('Employee Name')
            ax2.set_ylabel('Hours')
            ax2.set_title('Average Working Hours by Employee')

            st.pyplot(fig2)

# Download button for CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='employees_list.csv',
    mime='text/csv'
)
