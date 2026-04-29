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
.header {
    background-color: #1f4e79;
    padding: 15px;
    border-radius: 10px;
    color: white;
    font-size: 22px;
    font-weight: bold;
}
.highlight {
    background-color: #fff3cd;
    padding: 10px;
    border-left: 6px solid orange;
    border-radius: 8px;
    margin-bottom:5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥 ระบบค้นหายาและรหัสโรคผู้ป่วยนอก (OPD)</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA (2 SHEET)
# =========================
@st.cache_data
def load_data():
    # โหลดข้อมูล
    all_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="ALL_DATA")
    chronic_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="CHRONIC_26")

    # ล้างข้อมูลเบื้องต้น
    for temp_df in [all_df, chronic_df]:
        temp_df.dropna(how="all", inplace=True)
        temp_df.columns = temp_df.columns.str.strip() # ตัดช่องว่างที่ชื่อคอลัมน์

    return all_df, chronic_df

df, chronic_df = load_data()

# =========================
# SESSION STATE
# =========================
defaults = {
    "drug": "",
    "code": "",
    "search": "",
    "mode": "ข้อมูลทั้งหมด"
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")

menu = st.sidebar.radio("เมนู", ["🔍 ค้นหา", "📊 Dashboard"])

data_mode = st.sidebar.radio(
    "📂 เลือกฐานข้อมูล",
    ["ข้อมูลทั้งหมด", "26 โรคเรื้อรัง"]
)

# --- แก้ไขจุดนี้: เลือก dataset และดึงชื่อคอลัมน์ให้ตรงตามชุดข้อมูลที่เลือก ---
if data_mode == "ข้อมูลทั้งหมด":
    data = df
else:
    data = chronic_df

# ดึงชื่อคอลัมน์จากข้อมูลปัจจุบัน (ป้องกัน KeyError เพราะแต่ละ Sheet คอลัมน์ไม่เท่ากัน)
drug_col = data.columns[0]
property_col = data.columns[1]
code_col = data.columns[2]
# สำหรับ Chronic 26 ที่มี 4 คอลัมน์ (คอลัมน์ที่ 4 มักเป็นชื่อโรค)
disease_name_col = data.columns[3] if len(data.columns) > 3 else None

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":

    st.subheader(f"🔍 ค้นหายา / ICD ({data_mode})")

    colb1, colb2, colb3 = st.columns(3)

    with colb1:
        if st.button("📌 เฉพาะโรคเรื้อรัง"):
            # แจ้งเตือนให้เลือกที่ Sidebar เพื่อความเสถียรของ State
            st.info("กรุณาเลือก '26 โรคเรื้อรัง' ที่เมนูด้านซ้าย")

    with colb2:
        if st.button("❌ ล้างค่า"):
            st.session_state.drug = ""
            st.session_state.code = ""
            st.session_state.search = ""
            st.rerun()

    with colb3:
        if st.button("🔄 รีเซ็ต"):
            st.session_state.clear()
            st.rerun()

    # SEARCH
    search = st.text_input("🔍 พิมพ์ค้นหา", key="search")

    col1, col2 = st.columns(2)

    with col1:
        # เพิ่ม dropna() เพื่อกันพังถ้าใน Excel มีแถวว่าง
        drug_list = [""] + sorted(data[drug_col].dropna().astype(str).unique())
        selected_drug = st.selectbox("💊 เลือกยา", drug_list, key="drug")

    with col2:
        code_list = [""] + sorted(data[code_col].dropna().astype(str).unique())
        selected_code = st.selectbox("🦠 เลือก ICD", code_list, key="code")

    result = data.copy()

    # SEARCH FILTER
    if search:
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False, na=False) |
            result[code_col].astype(str).str.contains(search, case=False, na=False)
        ]

    # DRUG FILTER
    if selected_drug:
        result = result[result[drug_col].astype(str) == selected_drug]

    # ICD FILTER
    if selected_code:
        result = result[result[code_col].astype(str).str.startswith(selected_code)]

    # =========================
    # 🦠 SHOW DISEASE NAME (ปรับให้ใช้จากคอลัมน์ที่ 4 ของ Sheet นั้นๆ)
    # =========================
    if selected_code and disease_name_col:
        name = data[data[code_col].astype(str).str.startswith(selected_code)][disease_name_col].dropna().unique()
        if len(name) > 0:
            st.success(f"🦠 {name[0]}")

    # =========================
    # ⭐ HIGHLIGHT DRUG
    # =========================
    if "ใช้บ่อย" in result.columns:
        frequent = result[result["ใช้บ่อย"] == "⭐"]
        if not frequent.empty:
            st.markdown("### ⭐ ยาที่ใช้บ่อย")
            for d in frequent[drug_col].unique():
                st.markdown(f'<div class="highlight">⭐ {d}</div>', unsafe_allow_html=True)

    # =========================
    # 📊 GRAPH
    # =========================
    if not result.empty:
        st.markdown("### 📊 จำนวนยา")
        st.bar_chart(result[drug_col].value_counts().head(10))

    # TABLE (เลือกแสดงเฉพาะคอลัมน์พื้นฐานที่มี)
    st.dataframe(result, use_container_width=True)

# =========================
# 📊 DASHBOARD
# =========================
else:
    st.subheader(f"📊 Dashboard {data_mode}")

    # ดึงค่าจาก Data ปัจจุบัน
    selected_code = st.selectbox(
        "🦠 เลือก ICD",
        sorted(data[code_col].dropna().astype(str).unique())
    )

    filtered = data[data[code_col].astype(str).str.startswith(selected_code)]

    # ชื่อโรค (ถ้ามีคอลัมน์ที่ 4)
    if disease_name_col:
        name = filtered[disease_name_col].dropna().unique()
        if len(name) > 0:
            st.success(f"📌 {name[0]}")

    # METRIC
    col1, col2 = st.columns(2)
    col1.metric("จำนวนยา", len(filtered))
    col2.metric("จำนวนสรรพคุณ", filtered[property_col].nunique())

    # TOP DRUG
    st.markdown("### 📈 Top ยา")
    st.bar_chart(filtered[drug_col].value_counts().head(10))

    # SUMMARY ALL
    st.markdown("### 📊 จำนวนยาแต่ละโรค")
    chart = data.groupby(code_col)[drug_col].count()
    st.bar_chart(chart)

    # TABLE
    st.markdown("### 💊 รายการยา")
    st.dataframe(filtered, use_container_width=True)
