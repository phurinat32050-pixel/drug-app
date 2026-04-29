import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Drug Ask ICD-10", page_icon="💊", layout="wide")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.main {background-color: #f4f6f9;}
.header {
    background-color: #1f4e79;
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0px 1px 5px rgba(0,0,0,0.1);
}
.highlight {
    background-color: #e6f2ff;
    padding: 15px;
    border-radius: 10px;
    border-left: 6px solid #1f4e79;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥 ระบบค้นหายาและรหัสโรคผู้ป่วยนอก (OPD)</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_excel("DRUG DISEASE.xlsx")
    df = df.dropna(how="all")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

drug_col = df.columns[0]
property_col = df.columns[1]
code_col = df.columns[2]

# =========================
# ICD กลุ่มเรื้อรัง
# =========================
chronic_codes = [
    "E10","E11","I10","I11","I20","I25","I50",
    "J44","J45","K21","M10","M06","N18",
    "E78","E03","M81","G20","G30","F32",
    "C50","N40"
]

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio(
    "เลือกการทำงาน",
    ["🔍 ค้นหาข้อมูล", "📊 Dashboard โรค"]
)

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหาข้อมูล":

    st.subheader("🔍 ค้นหายาและรหัสโรค")

    col1, col2 = st.columns(2)

    with col1:
        selected_drug = st.selectbox("💊 เลือกยา", [""] + sorted(df[drug_col].astype(str).unique()))

    with col2:
        selected_code = st.selectbox("🦠 เลือกรหัสโรค", [""] + sorted(df[code_col].astype(str).unique()))

    result = df.copy()

    if selected_drug:
        result = result[result[drug_col] == selected_drug]

    if selected_code:
        result = result[result[code_col] == selected_code]

    # สรรพคุณเด่น
    if selected_drug:
        props = result[property_col].dropna().unique()
        if len(props) > 0:
            st.markdown("### 💡 สรรพคุณของยา")
            for p in props:
                st.markdown(f'<div class="highlight">• {p}</div>', unsafe_allow_html=True)

    st.dataframe(result[[drug_col, property_col, code_col]], use_container_width=True)

# =========================
# 📊 DASHBOARD
# =========================
else:

    st.subheader("📊 Dashboard เฉพาะโรค")

    # เลือกเฉพาะ 26 โรคเรื้อรัง
    chronic_df = df[df[code_col].isin(chronic_codes)]

    selected_code = st.selectbox(
        "🦠 เลือกรหัสโรค",
        sorted(chronic_df[code_col].unique())
    )

    filtered = chronic_df[chronic_df[code_col] == selected_code]

    # =========================
    # METRIC
    # =========================
    col1, col2 = st.columns(2)
    col1.metric("จำนวนรายการยา", len(filtered))
    col2.metric("จำนวนสรรพคุณ", filtered[property_col].nunique())

    # =========================
    # กราฟ
    # =========================
    st.markdown("### 📈 จำนวนยาในโรคนี้")

    chart_data = filtered[drug_col].value_counts()

    st.bar_chart(chart_data)

    # =========================
    # รายการยา
    # =========================
    st.markdown("### 💊 รายการยา")
    st.dataframe(filtered[[drug_col, property_col]], use_container_width=True)
