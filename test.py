import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from pandas import json_normalize
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import base64
import requests
import random
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet



# Load configuration from YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Set page configuration
st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Authentication
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Read Excel file or create an empty DataFrame if it doesn't exist
try:
    df = pd.read_pickle('employee.pkl')
except FileNotFoundError:
    df = pd.DataFrame()

# Display all columns
pd.set_option('display.max_columns', None)



# Login
name, authentication_status, username = authenticator.login()

def generate_pdf_report(start_date=None, end_date=None, title='Madhur Dairy Coupon Report'):
    c_df = pd.read_pickle('coupon.pkl')
    
    c_df = c_df.drop(columns=['OTP'])
    
    # Prepare data for the table
    table_data = [[Paragraph(str(val), getSampleStyleSheet()["BodyText"]) for val in c_df.columns]]  # Header row
    for _, row in c_df.iterrows():
        table_data.append([Paragraph(str(val), getSampleStyleSheet()["BodyText"]) for val in row])

    # Create a PDF document
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    
    # Create title paragraph
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    title_paragraph = Paragraph(title, title_style)

    # Create the table
    table = Table(table_data)
    style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0,0), (-1,0), 12),
                        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                        ('GRID', (0,0), (-1,-1), 1, colors.black)])
    table.setStyle(style)

    # Add title and table to PDF
    elements = [title_paragraph, Spacer(1, 20), table]
    pdf.build(elements)
    
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return pdf_bytes

coupons_data = {
    'Date': pd.date_range(start='2024-04-17', end='2024-04-23'),
    'Generated': np.random.randint(50, 70, 7),
    'Redeemed': np.random.randint(20, 50, 7)
}
coupons_df = pd.DataFrame(coupons_data)

def company_header():
    st.markdown(
        """
        <div style='background-color: #f0f0f0; padding: 10px; display: flex; align-items: center; justify-content: space-between;'>
            <div style='display: flex; align-items: center;'>
                <h2 style='color: #333333; margin: 0;'>Madhur Dairy Canteen Management System</h2>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    
    
    st.sidebar.image('logo.png', width = 250)


        
        
# Function to plot line graph
def plot_line_graph(data):
    fig = plt.figure(figsize=(10, 3))
    plt.plot(data['Date'], data['Redeemed'], marker='o', linestyle='-', label='Redeemed')
    plt.plot(data['Date'], data['Generated'], marker='o', linestyle='-', label='Generated')
    plt.title('Daily Coupons Redeemed')
    plt.xlabel('Date')
    plt.ylabel('Coupons Redeemed')
    plt.grid(True)
    plt.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Admin dashboard home page
def admin_dashboard_home():
    
    st.title('Home')
    # Layout for dividing the page into two parts
    col1, col2 = st.columns([0.25, 1])

    # First part: Coupons generated and redeemed data
    with col1:
        st.write("## Coupons Overview")
        generated_total = coupons_df['Generated'].sum()
        redeemed_total = coupons_df['Redeemed'].sum()

        # Display coupons generated and redeemed with small green arrows
        st.metric(label='Coupons Generated', value = generated_total, delta = 35)
        st.metric(label='Coupons Redeemed', value = redeemed_total, delta = -7)
        st.metric(label='No. of Employees', value = 3)
        #st.write(f"**Coupons Generated:** {generated_total}")
        #st.write(f"**Coupons Redeemed:** {redeemed_total}")


 # Second part: Line graph of daily coupons redeemed for past week
    with col2:
        st.write("## Daily Coupons Redeemed (Past Week)")
        plot_line_graph(coupons_df)
    

# Admin dashboard function
def admin_dashboard():
    
    st.sidebar.write("Welcome to the Admin Dashboard")
    page = st.sidebar.radio("Select Page", ["Home", "User Management", "Employee Management", "Menu Management", "Support"])
    
    # Add your user dashboard content here
    st.sidebar.title("Generate Report")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")
    
    

    # Button to generate PDF report
    if st.sidebar.button("Generate PDF"):
    
        pdf_bytes = generate_pdf_report(start_date=start_date, end_date=end_date)
        st.sidebar.download_button(label="Download PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        st.sidebar.success("PDF report generated successfully!")
    
    footer_html = """<div style='text-align: center;'>
                    <p>© 2024 Madhur Dairy | All Rights Reserved</p>
                    </div>"""
    st.sidebar.markdown(footer_html, unsafe_allow_html=True)

    
    if page == "Home":
        admin_dashboard_home()
        # Add content for the Home page
        
    elif page == "User Management":
        st.title("User Management")
        
        df_transposed = pd.DataFrame(config['credentials']['usernames']).T
        st.markdown(
        f"""<style>
            .reportview-container .main .block-container{{
                max-width: 100%;
                padding-top: 0rem;
                padding-right: 0rem;
                padding-left: 0rem;
                padding-bottom: 0rem;
            }}
        </style>""",
        unsafe_allow_html=True
        )
        edited_users = st.data_editor(df_transposed, num_rows="dynamic")
        
        if st.button('Save', key="unique5"):
            # Check if there are new users added
            new_users = edited_users.index.difference(df_transposed.index)
            
            # If there are new users, append them to the configuration
            if not new_users.empty:
                for user in new_users:
                    config['credentials']['usernames'][user] = edited_users.loc[user].to_dict()

            # Update the usernames in the configuration
            config['credentials']['usernames'] = edited_users.to_dict(orient='index')

            # Write the updated configuration back to the YAML file
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file)
   
        
    elif page == "Employee Management":
        st.title("Employee Management")
        dfm = pd.read_pickle('employee.pkl')
        
        
        
        edited_df = st.data_editor(dfm, 
                           num_rows="dynamic", 
                           use_container_width=True, 
                           column_config={
                               "Mobile No.": st.column_config.NumberColumn(format="%f"),
                               "Employee Code": st.column_config.NumberColumn(format="%f")
                           })
        if st.button('Save', key="unique4"):
            edited_df.to_pickle('employee.pkl')
            st.success('Changes Saved')
        
        uploaded = st.file_uploader("Choose a file")
        # Add content for the Customer Management page
        
    elif page == "Menu Management":
        st.title("Canteen Menu")
        df_menu = pd.read_pickle('menu.pkl')
        edited_menu = st.data_editor(df_menu, num_rows="dynamic")
        if st.button('Save', key="unique3"):
            edited_menu.to_pickle('menu.pkl')
            
    elif page == "Support":
        st.title('Support')
    
        # Input Fields
        issue_name = st.text_input('Name:')
        issue_email = st.text_input('Contact Email:')
        issue_number = st.text_input('Phone number:')
        issue = st.text_area('Describe your issue:')
        
        
        # Submit Button
        if st.button('Submit'):
            if issue and issue_name and issue_email and issue_number:
                #send_email(issue, contact_info)
                st.success('Your request has been submitted successfully!')
            else:
                st.error('Please fill in both issue description and contact information.')

# Regular user dashboard function
def user_dashboard():
    st.write("Welcome to the Timekeeper Dashboard")
    # Add your user dashboard content here
    st.sidebar.title("Generate Report")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    # Button to generate PDF report
    if st.sidebar.button("Generate PDF"):
    
        pdf_bytes = generate_pdf_report(start_date=start_date, end_date=end_date)
        st.sidebar.download_button(label="Download PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        st.sidebar.success("PDF report generated successfully!")
    # Read menu data
    
    menu_df = pd.read_pickle('menu.pkl')

    # Read employee data
    employee_df = pd.read_pickle('employee.pkl')


    # Display employee dropdown to select employee code
    selected_employee_code = st.selectbox("Select Employee Code:", [int(code) for code in employee_df['Employee Code'].tolist()])

    # Get employee details based on selected employee code
    employee_info = employee_df[employee_df['Employee Code'] == selected_employee_code]
    if not employee_info.empty:
        employee_name = employee_info.iloc[0]['Employee Name']
        employee_mobile = employee_info.iloc[0]['Mobile No.']
        
    else:
        employee_name = "Not Found"
        employee_mobile = "Not Found"
        
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Filter out items already ordered by the selected employee today
    ordered_items_today = []
    coupon_df = pd.read_pickle('coupon.pkl')
    if not coupon_df.empty:
        ordered_items_today = coupon_df[(coupon_df['Employee code'] == selected_employee_code) & (coupon_df['Date'] == current_date)]['Type of dish'].tolist()

    # Filter menu items not already ordered today
    menu_items = menu_df[~menu_df['Item'].isin(ordered_items_today)]['Item'].tolist()

    # Display menu items and allow user to select
    selected_items = st.selectbox("Select items from the menu:", menu_items)
    # Calculate total price based on selected items
    total_price = 0

    
    item_data = menu_df.loc[menu_df['Item'] == selected_items]
    if not item_data.empty:
        price = item_data['Price'].iloc[0]
        discount = item_data['Discount'].iloc[0]
        # Apply discount if available
        discounted_price = price - discount
        total_price += discounted_price

    # Display bill with selected items, employee details, and total price
    st.write("### Bill")
    st.write("**Selected Item:**")
    st.write(f"- {selected_items}")
    st.write(f"**Employee Name:** {employee_name}")
    st.write(f"**Total Price:** ₹{total_price:.2f}")
    button1 = st.button('Generate OTP', )
    if button1:
    
        c_df = pd.read_pickle('coupon.pkl')
        
        # Increment the coupon unique code number
        last_coupon_code = c_df['Coupon unique code no.'].iloc[-1]
        last_coupon_num = int(last_coupon_code[1:])
        new_coupon_num = last_coupon_num + 1
        new_coupon_code = f'C{new_coupon_num:03d}'
        
        # Get current date and time
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        # Generate 6-digit OTP
        
        otp = ''.join(str(random.randint(0, 9)) for _ in range(6))
        
        # Set redeemed to False
        redeemed = False

        # Create the new entry
        new_entry = {
            'Coupon unique code no.': new_coupon_code,
            'Date': current_date,
            'Time': current_time,
            'Employee code': selected_employee_code,
            'Employee name': employee_name,
            'Type of dish': selected_items,
            'Rupees of items': total_price,
            'OTP': otp,
            'Redeemed': redeemed
        }

        # Append the new entry to the DataFrame
        c_df = pd.concat([c_df, pd.DataFrame([new_entry])], ignore_index=True)
        c_df.to_pickle('coupon.pkl')
        
        variable = str(employee_name) + '|' + str(otp)
    
        url = "https://www.fast2sms.com/dev/bulkV2"

        querystring = {"authorization":"pPAR7SgKnuwyOvcxzUN3BhFfsaILJG142HWYjle8Zd6tXoVkDigXoLnctFQWVZI0PAUjDx31rl2SfhkJ","sender_id":"GDCCMS","message":"169006","variables_values":f"{str(variable)}","route":"dlt","numbers": str(int(employee_mobile))}

        headers = {
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        

        st.success("OTP sent to Employee")
        st.rerun()

    
def user2_dashboard():
    st.write("Welcome to the Operator Dashboard")
    otp_input = st.text_input("Enter OTP")

    st.sidebar.title("Generate Report")
    start_date = st.sidebar.date_input("Start Date")
    end_date = st.sidebar.date_input("End Date")

    # Button to generate PDF report
    if st.sidebar.button("Generate PDF"):
    
        pdf_bytes = generate_pdf_report(start_date=start_date, end_date=end_date)
        st.sidebar.download_button(label="Download PDF", data=pdf_bytes, file_name="report.pdf", mime="application/pdf")
        st.sidebar.success("PDF report generated successfully!")
        
    # Button to fetch details associated with OTP
    if st.button("Fetch Details"):
        # Read coupon data
        try:
            coupon_data = pd.read_pickle('coupon.pkl')
            # Check if OTP exists in the coupon data
            if otp_input in coupon_data['OTP'].values:
                # Retrieve details associated with OTP
                otp_details = coupon_data[coupon_data['OTP'] == otp_input].iloc[0]
                employee_name = otp_details['Employee name']
                dish_type = otp_details['Type of dish']
                amount = otp_details['Rupees of items']

                # Display details
                st.write(f"Employee Name: {employee_name}")
                st.write(f"Type of Dish: {dish_type}")
                st.write(f"Amount: {amount}")
                if st.button("Redeem"):
                    st.success('Coupon Redeemed')
            else:
                st.error("Invalid OTP. Please try again.")
        except FileNotFoundError:
            st.error("Coupon data not found. Please generate some coupons first.")

# Display dashboard if authenticated
if authentication_status:
    company_header()
    authenticator.logout('Logout', 'sidebar', 'my_crazy_random_signature_key')
      
    if username == 'admin':
        admin_dashboard()
    elif username == 'operator':
        user2_dashboard()
    elif username == 'timekeeper':
        user_dashboard()

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)


