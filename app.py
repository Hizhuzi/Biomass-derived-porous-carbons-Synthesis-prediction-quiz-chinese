import streamlit as st  
import pandas as pd  
import requests  
from io import BytesIO  
from datetime import datetime  

# GitHub raw content URL for your Excel file  
GITHUB_EXCEL_URL = "https://raw.githubusercontent.com/Hizhuzi/Biomass-derived-porous-carbons-Synthesis-prediction-quiz/main/your_data.xlsx"  

st.markdown("## 欢迎参加生物质衍生多孔碳 (BDPCs) 合成预测问答！")  
st.markdown("### 请查看以下页面的BDPCs，并提供您的最佳预测。")  

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

# Add name, position and institution input fields  
st.markdown("### 个人信息")  
name = st.text_input("请输入您的姓名：")  
title = st.text_input("请输入您的职位：")  
institution = st.text_input("请输入您的机构：")  

# Ensure name, position and institution are filled before proceeding  
if not name or not title or not institution:  
    st.warning("请先填写您的个人信息。")  
else:  
    def display_question(index):  
        st.markdown(f"### 多孔碳结构信息 (问题 {index + 1}/50)")  
        st.markdown(f"<h4 style='font-size: 20px;'>介孔比表面积：{selected_data.iloc[index, 0]} m²/g</h4>", unsafe_allow_html=True)  
        st.markdown(f"<h4 style='font-size: 20px;'>微孔比表面积：{selected_data.iloc[index, 1]} cm²/g</h4>", unsafe_allow_html=True)  

    # Display current question  
    display_question(st.session_state.current_index)  

    # Define questionnaire content  
    st.markdown("### 请填写以下信息：")  
    st.markdown("<h4 style='font-size: 20px;'>质料与原料的活化剂比</h4>", unsafe_allow_html=True)  
    mass_ratio = st.slider('', 0.25, 8.00, 0.25)  
    st.markdown("<h4 style='font-size: 20px;'>温度 (°C)</h4>", unsafe_allow_html=True)  
    temperature = st.slider('', 300, 1000, 300) # 修改为300-1000°C  
    st.markdown("<h4 style='font-size: 20px;'>时间 (小时)</h4>", unsafe_allow_html=True)  
    time = st.slider('', 1.0, 8.0, 1.0, 0.1)  
    st.markdown("<h4 style='font-size: 20px;'>加热速率 (°C/分钟)</h4>", unsafe_allow_html=True)  
    heating_rate = st.slider('', 1, 40, 1)  
    st.markdown("<h4 style='font-size: 20px;'>活化剂</h4>", unsafe_allow_html=True)  
    activator = st.selectbox('', ['Air', 'CO₂', 'Steam', 'KOH', 'NaOH', 'K₂CO₃', 'ZnCl₂', 'NaNH₂', 'K₂SiO₃', 'H₃PO₄', 'H₂SO₄', 'HNO₃', 'HCl', 'No Activator'])  
    st.markdown("<h4 style='font-size: 20px;'>信心级别</h4>", unsafe_allow_html=True)  
    certainty = st.slider('', 1, 5, 1)  

    def save_data():  
        result_df = pd.DataFrame(st.session_state.data)  
        buffer = BytesIO()  
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:  
            result_df.to_excel(writer, index=False)  
        st.download_button(  
            label="下载预测结果",  
            data=buffer.getvalue(),  
            file_name=f"human_expert_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",  
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  
        )  

    def submit_data():  
        st.session_state.data.append({  
            'Name': name,  
            'Position': title,  
            'Institution': institution,  
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
        st.success('数据提交成功!')  

        st.session_state.current_index += 1  
        if st.session_state.current_index < len(selected_data):  
            st.experimental_rerun()  
        else:  
            st.success('所有问题已回答完毕!')  
            save_data()  

    st.button("提交", on_click=submit_data)  

    # Display progress  
    st.progress(st.session_state.current_index / len(selected_data))