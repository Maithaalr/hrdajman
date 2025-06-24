import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import numpy as np

st.set_page_config(page_title="لوحة معلومات الموارد البشرية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@500;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        background-color: #f5f8fc;
    }
    .metric-box {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
    }
    .section-header {
        font-size: 20px;
        color: #1e3d59;
        margin-top: 20px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

col_logo, col_upload = st.columns([1, 3])

with col_logo:
    logo = Image.open("logo.png")
    st.image(logo, width=180)

with col_upload:
    st.markdown("<div class='section-header'>يرجى تحميل بيانات الموظفين</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=0)
    selected_sheet = st.selectbox("اختر الجهة", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    tab1, tab2, tab3, tab4 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات"])

    with tab2:
        st.markdown("### التحليلات البصرية")

        st.markdown("### توزيع الموظفين حسب نوع الوظيفة والدائرة (Stacked Bar Chart)")

        if 'نوع الوظيفة' in df.columns and 'الدائرة' in df.columns:
            job_dept_counts = df.groupby(['الدائرة', 'نوع الوظيفة']).size().reset_index(name='العدد')

            # حساب النسبة المئوية من مجموع كل دائرة
            total_per_dept = job_dept_counts.groupby('الدائرة')['العدد'].transform('sum')
            job_dept_counts['النسبة المئوية'] = round((job_dept_counts['العدد'] / total_per_dept) * 100, 1)

            fig_stack = px.bar(
                job_dept_counts,
                x='الدائرة',
                y='العدد',
                color='نوع الوظيفة',
                text=job_dept_counts.apply(lambda row: f"{row['العدد']} ({row['النسبة المئوية']}%)", axis=1),
                color_discrete_sequence=px.colors.sequential.Blues,
                title="Stacked Bar - توزيع الوظائف حسب الدوائر"
                )

            fig_stack.update_layout(barmode='stack', title_x=0.5, xaxis_title='الدائرة', yaxis_title='عدد الموظفين')
            st.plotly_chart(fig_stack, use_container_width=True)
        else:
            st.warning("البيانات لا تحتوي على أعمدة 'اسم الوظيفة' و 'الدائرة'.")



    with tab3:
        st.markdown("### تحليل البيانات المفقودة")

        df_citizens = df[df['الجنسية'] == 'إماراتية'].copy()
        df_non_citizens = df[df['الجنسية'] != 'إماراتية'].copy()

        st.subheader(" نواقص المواطنين ")
        excluded_cols = ['رقم الأقامة', 'الكفيل', 'تاريخ اصدار اللإقامة', 'تاريخ انتهاء اللإقامة']
        filtered_citizen_df = df_citizens.drop(columns=[col for col in excluded_cols if col in df_citizens.columns])
        missing_percent_c = filtered_citizen_df.isnull().mean() * 100
        missing_count_c = filtered_citizen_df.isnull().sum()

        missing_df_c = pd.DataFrame({
            'العمود': filtered_citizen_df.columns,
            'عدد القيم المفقودة': missing_count_c,
            'النسبة المئوية': missing_percent_c
        }).loc[lambda df: df['عدد القيم المفقودة'] > 0]

        fig_c = px.bar(
            missing_df_c,
            x='العمود',
            y='عدد القيم المفقودة',
            color='النسبة المئوية',
            text=missing_df_c.apply(lambda row: f"{row['عدد القيم المفقودة']} | {round(row['النسبة المئوية'], 1)}%", axis=1),
            color_continuous_scale=['#C8D9E6', '#2F4156']
        )
        fig_c.update_layout(title="المواطنين - عدد القيم المفقودة ونسبتها", title_x=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_c, use_container_width=True)

        st.subheader(" نواقص الوافدين ")
        missing_percent_n = df_non_citizens.isnull().mean() * 100
        missing_count_n = df_non_citizens.isnull().sum()

        missing_df_n = pd.DataFrame({
            'العمود': df_non_citizens.columns,
            'عدد القيم المفقودة': missing_count_n,
            'النسبة المئوية': missing_percent_n
        }).loc[lambda df: df['عدد القيم المفقودة'] > 0]

        fig_n = px.bar(
            missing_df_n,
            x='العمود',
            y='عدد القيم المفقودة',
            color='النسبة المئوية',
            text=missing_df_n.apply(lambda row: f"{row['عدد القيم المفقودة']} | {round(row['النسبة المئوية'], 1)}%", axis=1),
            color_continuous_scale=['#C8D9E6', '#2F4156']
        )
        fig_n.update_layout(title="الوافدين - عدد القيم المفقودة ونسبتها", title_x=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_n, use_container_width=True)
