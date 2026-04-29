import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Drug Ask ICD-10", page_icon="💊", layout="wide")

# =========================
# STYLE (UI โรงพยาบาล)
# =========================
st.markdown("""
<style>
.main {
    background-color: #f4f6f9;
}
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

try:
    df = load_data()
except:
    st.error("❌ ไม่พบไฟล์ DRUG DISEASE.xlsx")
    st.stop()

# =========================
# COLUMN
# =========================
drug_col = df.columns[0]
property_col = df.columns[1]
code_col = df.columns[2]

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio(
    "เลือกการทำงาน",
    ["🔍 ค้นหาข้อมูล", "📊 รายงาน"]
)

st.sidebar.markdown("---")
st.sidebar.info("Drug Ask ICD-10")

# =========================
# 🔍 PAGE 1
# =========================
if menu == "🔍 ค้นหาข้อมูล":

    st.subheader("🔍 ค้นหายาและรหัสโรค")

    col1, col2 = st.columns(2)

    with col1:
        keyword = st.text_input("💊 ค้นหาชื่อยา")

    with col2:
        code = st.text_input("🦠 ค้นหารหัสโรค")

    result = df.copy()

    if keyword:
        result = result[result[drug_col].astype(str).str.contains(keyword, case=False)]

    if code:
        result = result[result[code_col].astype(str).str.contains(code, case=False)]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(result[[drug_col, property_col, code_col]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 📊 PAGE 2
# =========================
else:

    st.subheader("📊 สรุปข้อมูล")

    col1, col2 = st.columns(2)
    col1.metric("จำนวนรายการยา", len(df))
    col2.metric("จำนวนรหัสโรค", df[code_col].nunique())

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
