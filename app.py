import streamlit as st  
import pandas as pd  
import requests  
from io import BytesIO  
from datetime import datetime  

# GitHub raw content URL for your Excel file  
GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/Hizhuzi/Biomass-derived-porous-carbons-Synthesis-prediction-quiz/main/your_data.xlsx"  

st.markdown("## Welcome to the Biomass-derived porous carbons (BDPCs) Synthesis Prediction Quiz!")  
st.markdown("### Please review the BDPCs on the following pages and provide your best predictions.")  

@st.cache_data  
def load_data():  
    response = requests.get(GITHUB_EXCEL_URL)  
    content = BytesIO(response.content)  
    df = pd.read_excel(content)  
    return df.iloc[:, [8, 9]].sample(n=50, random_state=42).reset_index(drop=True)  

# Load data  
selected_data = load_data()  

# Initialize session_state  
if 'current_index' not in st.session_state:  
    st.session_state.current_index = 0  
if 'data' not in st.session_state:  
    st.session_state.data = []  
if 'name' not in st.session_state:  
    st.session_state.name = ""  
if 'title' not in st.session_state:  
    st.session_state.title = ""  
if 'institution' not in st.session_state:  
    st.session_state.institution = ""  

# Get user information on the first page  
if st.session_state.current_index == 0:  
    st.markdown("### Personal Information")  
    st.session_state.name = st.text_input("Please enter your name:")  
    st.session_state.title = st.text_input("Please enter your position:")  
    st.session_state.institution = st.text_input("Please enter your institution:")  

    # Ensure name, position and institution are filled before proceeding  
    if not st.session_state.name or not st.session_state.title or not st.session_state.institution:  
        st.warning("Please fill in your personal information before proceeding.")  
        st.stop()  # Stop execution until user fills the information  

def display_question(index):  
    st.markdown(f"### Porous Carbon Structure Information (Question {index + 1}/50)")  
    st.markdown(f"<h4 style='font-size: 20px;'>Mesoporous Specific Surface Area: {selected_data.iloc[index, 0]} m²/g</h4>", unsafe_allow_html=True)  
    st.markdown(f"<h4 style='font-size: 20px;'>Micropore Specific Surface Area: {selected_data.iloc[index, 1]} cm²/g</h4>", unsafe_allow_html=True)  

# Display current question  
display_question(st.session_state.current_index)  

# Define questionnaire content  
st.markdown("### Please fill in the following information:")  
st.markdown("<h4 style='font-size: 20px;'>Mass ratio of precursor to activator</h4>", unsafe_allow_html=True)  
mass_ratio = st.slider('', 0.25, 8.00, 0.25)  
st.markdown("<h4 style='font-size: 20px;'>Temperature (°C)</h4>", unsafe_allow_html=True)  
temperature = st.slider('', 300, 1000, 300)  # Modified to 300-1000°C  
st.markdown("<h4 style='font-size: 20px;'>Time (hours)</h4>", unsafe_allow_html=True)  
time = st.slider('', 1.0, 8.0, 1.0, 0.1)  
st.markdown("<h4 style='font-size: 20px;'>Heating Rate (°C/minute)</h4>", unsafe_allow_html=True)  
heating_rate = st.slider('', 1, 40, 1)  
st.markdown("<h4 style='font-size: 20px;'>Activator</h4>", unsafe_allow_html=True)  
activator = st.selectbox('', ['Air', 'CO₂', 'Steam', 'KOH', 'NaOH', 'K₂CO₃', 'ZnCl₂', 'NaNH₂', 'K₂SiO₃', 'H₃PO₄', 'H₂SO₄', 'HNO₃', 'HCl', 'No Activator'])  
st.markdown("<h4 style='font-size: 20px;'>Confidence Level</h4>", unsafe_allow_html=True)  
certainty = st.slider('', 1, 5, 1)  

def save_data():  
    result_df = pd.DataFrame(st.session_state.data)  
    buffer = BytesIO()  
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:  
        result_df.to_excel(writer, index=False)  
    st.download_button(  
        label="Download prediction results",  
        data=buffer.getvalue(),  
        file_name=f"human_expert_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",  
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  
    )  

def submit_data():  
    st.session_state.data.append({  
        'Name': st.session_state.name,  
        'Position': st.session_state.title,  
        'Institution': st.session_state.institution,  
        'Question Number': st.session_state.current_index + 1,  
        'Activator Amount': mass_ratio,  
        'Temperature': temperature,  
        'Time': time,  
        'Heating Rate': heating_rate,  
        'Activator': activator,  
        'Confidence Level': certainty,  
        'Actual SSA': selected_data.iloc[st.session_state.current_index, 0],  
        'Actual Total Pore Volume': selected_data.iloc[st.session_state.current_index, 1]  
    })  
    st.success('Data submitted successfully!')  

    st.session_state.current_index += 1  
    if st.session_state.current_index < len(selected_data):  
        query_params = st.experimental_get_query_params()  
        query_params['index'] = st.session_state.current_index  
        st.experimental_set_query_params(**query_params)  
    else:  
        st.success('All questions answered!')  
        save_data()  

st.button("Submit", on_click=submit_data)  

# Display progress  
st.progress(st.session_state.current_index / len(selected_data))