import streamlit as st
import pandas as pd
import os
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="OPD Coding System",
    page_icon="🏥",
    layout="wide"
)

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
    font-size: 24px;
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

drug_col = df.columns[0]
property_col = df.columns[1]
code_col = df.columns[2]

# =========================
# SIDEBAR MENU
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio(
    "เลือกการทำงาน",
    ["🔍 ค้นหาข้อมูล", "🤖 AI แนะนำ", "📊 รายงาน"]
)

st.sidebar.markdown("---")
st.sidebar.info("ระบบ Drug Ask ICD-10")

# =========================
# AI SETUP
# =========================
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(text):
    if not client:
        return "⚠️ ยังไม่ได้ตั้งค่า API KEY"

    context = df.head(30).to_string()

    prompt = f"""
คุณคือผู้ช่วยเวชสถิติ
ให้แนะนำข้อมูลจากยา

{context}

คำถาม: {text}

ตอบแบบ:
ชื่อยา | สรรพคุณ | รหัสโรค
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content

# =========================
# PAGE 1: SEARCH
# =========================
if menu == "🔍 ค้นหาข้อมูล":

    st.subheader("🔍 ค้นหาข้อมูลยาและรหัสโรค")

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
# PAGE 2: AI
# =========================
elif menu == "🤖 AI แนะนำ":

    st.subheader("🤖 ระบบช่วยแนะนำ (AI)")

    user_input = st.text_input("พิมพ์ เช่น Metformin หรือ เบาหวาน")

    if user_input:
        with st.spinner("กำลังวิเคราะห์..."):
            result = ask_ai(user_input)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(result)
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# PAGE 3: REPORT
# =========================
else:

    st.subheader("📊 รายงานข้อมูล")

    st.metric("จำนวนรายการยา", len(df))
    st.metric("จำนวนรหัสโรค", df[code_col].nunique())

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
