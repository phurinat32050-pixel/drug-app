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
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
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
# 📌 รายการ ICD-10 กลุ่ม 26 โรคเรื้อรัง (ตัวอย่างหลัก)
# =========================
chronic_codes = [
    "E10","E11","I10","I11","I20","I25","I50",
    "J44","J45","K21","M10","M06","N18",
    "E78","E03","M81","G20","G30","F32",
    "C50","N40"
]

# =========================
# SESSION STATE
# =========================
if "chronic_mode" not in st.session_state:
    st.session_state.chronic_mode = False

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio("เลือกการทำงาน", ["🔍 ค้นหาข้อมูล", "📊 รายงาน"])

# =========================
# 🔍 SEARCH PAGE
# =========================
if menu == "🔍 ค้นหาข้อมูล":

    st.subheader("🔍 ค้นหายาและรหัสโรค")

    # =========================
    # 🔥 ปุ่ม 26 โรคเรื้อรัง
    # =========================
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("📌 แสดง 26 โรคเรื้อรัง"):
            st.session_state.chronic_mode = True

    with col_btn2:
        if st.button("❌ ล้างตัวกรอง"):
            st.session_state.chronic_mode = False

    # =========================
    # DROPDOWN
    # =========================
    col1, col2 = st.columns(2)

    with col1:
        selected_drug = st.selectbox(
            "💊 เลือกยา",
            [""] + sorted(df[drug_col].astype(str).unique())
        )

    with col2:
        selected_code = st.selectbox(
            "🦠 เลือกรหัสโรค",
            [""] + sorted(df[code_col].astype(str).unique())
        )

    result = df.copy()

    # =========================
    # 🔗 FILTER
    # =========================
    if st.session_state.chronic_mode:
        result = result[result[code_col].isin(chronic_codes)]

    if selected_drug:
        result = result[result[drug_col] == selected_drug]

    if selected_code:
        result = result[result[code_col] == selected_code]

    # =========================
    # 💡 แสดงสถานะ
    # =========================
    if st.session_state.chronic_mode:
        st.info("📌 กำลังแสดงเฉพาะกลุ่ม 26 โรคเรื้อรัง")

    # =========================
    # 🔥 สรรพคุณเด่น
    # =========================
    if selected_drug:
        properties = result[property_col].dropna().unique()

        if len(properties) > 0:
            st.markdown("### 💡 สรรพคุณของยา")
            for prop in properties:
                st.markdown(f'<div class="highlight">• {prop}</div>', unsafe_allow_html=True)

    # =========================
    # TABLE
    # =========================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(result[[drug_col, property_col, code_col]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # 🔗 SUGGEST
    # =========================
    if selected_drug:
        st.success(f"💡 ยา '{selected_drug}' ใช้กับรหัสโรค:")
        st.write(result[code_col].unique())

    if selected_code:
        st.success(f"💡 รหัสโรค '{selected_code}' ใช้ยาดังนี้:")
        st.write(result[drug_col].unique())

# =========================
# 📊 REPORT
# =========================
else:

    st.subheader("📊 สรุปข้อมูล")

    col1, col2 = st.columns(2)
    col1.metric("จำนวนรายการยา", len(df))
    col2.metric("จำนวนรหัสโรค", df[code_col].nunique())

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
