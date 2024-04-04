import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Set page configuration
st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")



# Read Excel file
dfm = pd.read_excel(
    io="Canteen.xlsx",
    engine="openpyxl",
    sheet_name="Master Report",
    skiprows=2,
    usecols="A:F",
    nrows=554,
)

# Display all columns
pd.set_option('display.max_columns', None)

name, authentication_status, username = authenticator.login('Login', 'main')

if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

def dashboard():
   
    # Sidebar for filtering by Employee Code
    ecode = st.sidebar.selectbox("Employee Code",options=dfm["Employee Code"].unique(),
	)

	# Filter data based on selected Employee Codes
    dfm_selection = dfm[dfm["Employee Code"] == ecode]

    # Display filtered data in a table
    st.write(dfm_selection)


# Hide Streamlit menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
