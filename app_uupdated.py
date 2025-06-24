
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" نظرة عامة", " تحليلات بصرية", " البيانات المفقودة", " عرض البيانات", "تحليل حسب الجنس", "تحليل تعليمي"])

    with tab6:
        st.markdown("### توزيع المستوى التعليمي حسب الدوائر (مجمّع)")

        if 'الدائرة' in df.columns and 'المستوى التعليمي' in df.columns:
            edu_grouped = df.groupby(['الدائرة', 'المستوى التعليمي']).size().reset_index(name='عدد')
            total_per_dept = edu_grouped.groupby('الدائرة')['عدد'].transform('sum')
            edu_grouped['النسبة'] = round((edu_grouped['عدد'] / total_per_dept) * 100, 1)
            edu_grouped['label'] = edu_grouped.apply(lambda row: f"{row['عدد']} | {row['النسبة']}%", axis=1)

            fig_edu = px.bar(
                edu_grouped,
                x='الدائرة',
                y='عدد',
                color='المستوى التعليمي',
                text='label',
                barmode='stack',
                color_discrete_sequence=px.colors.sequential.Blues[::-1]
            )

            fig_edu.update_layout(
                title='توزيع الموظفين حسب المستوى التعليمي في كل دائرة',
                title_x=0.5,
                xaxis_tickangle=-45
            )

            fig_edu.update_traces(textposition='inside', insidetextanchor='middle')
            st.plotly_chart(fig_edu, use_container_width=True)

        st.markdown("### توزيع المستوى التعليمي - اختر جهة محددة")

        if 'الدائرة' in df.columns and 'المستوى التعليمي' in df.columns:
            selected_dept = st.selectbox("اختر الدائرة:", sorted(df['الدائرة'].dropna().unique()))
            df_dept = df[df['الدائرة'] == selected_dept]

            edu_counts = df_dept['المستوى التعليمي'].value_counts().reset_index()
            edu_counts.columns = ['المستوى التعليمي', 'عدد']
            edu_counts['النسبة'] = round((edu_counts['عدد'] / edu_counts['عدد'].sum()) * 100, 1)
            edu_counts['label'] = edu_counts.apply(lambda row: f"{row['عدد']} | {row['النسبة']}%", axis=1)

            fig_dept = px.bar(
                edu_counts,
                x='المستوى التعليمي',
                y='عدد',
                text='label',
                color='المستوى التعليمي',
                color_discrete_sequence=px.colors.sequential.Blues[::-1]
            )

            fig_dept.update_layout(
                title=f'توزيع المستوى التعليمي في {selected_dept}',
                title_x=0.5,
                xaxis_tickangle=-45,
                showlegend=False
            )

            fig_dept.update_traces(textposition='inside', insidetextanchor='middle')
            st.plotly_chart(fig_dept, use_container_width=True)
