import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO

st.set_page_config(page_title="Dependent Eligibility Tracker", layout="wide")

st.title("Dependent Eligibility Tracker")

uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx","csv"])

def read_file(f):
    if f.name.lower().endswith(".csv"):
        return pd.read_csv(f)
    return pd.read_excel(f)

if uploaded:
    df = read_file(uploaded)

    required = ["Relation","DOB"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {', '.join(missing)}")
        st.stop()

    today = datetime.today()
    df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")

    def calc(row):
        rel = str(row["Relation"]).strip().lower()

        if rel == "son":
            age = 18
        elif rel == "daughter":
            age = 21
        else:
            return pd.Series([None,None,None])

        if pd.isna(row["DOB"]):
            return pd.Series([None,None,None])

        target = row["DOB"] + relativedelta(years=age)

        if target <= today:
            return pd.Series([target.date(),"Eligible Now","blue"])

        diff = relativedelta(target, today)

        if diff.years > 0:
            txt = f"After {diff.years} years"
        elif diff.months > 0:
            txt = f"After {diff.months} months"
        else:
            txt = f"After {diff.days} days"

        days = (target - today).days

        if days < 183:
            color = "red"
        elif days < 365:
            color = "orange"
        else:
            color = ""

        return pd.Series([target.date(),txt,color])

    df[["Eligible Date","Time Remaining","Color"]] = df.apply(calc, axis=1)

    def highlight(row):
        if row["Color"]=="red":
            return ["background-color:#ffb3b3"]*len(row)
        elif row["Color"]=="orange":
            return ["background-color:#ffe0b3"]*len(row)
        elif row["Color"]=="blue":
            return ["background-color:#b3d9ff"]*len(row)
        return [""]*len(row)

    st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True)

    output = BytesIO()
    export = df.drop(columns=["Color"])
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export.to_excel(writer, index=False)

    st.download_button(
        "Download Result",
        data=output.getvalue(),
        file_name="Dependent_Eligibility.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
