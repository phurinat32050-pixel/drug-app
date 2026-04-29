import streamlit as st
import pandas as pd

# =========================
# CONFIG (คงเดิม)
# =========================
st.set_page_config(page_title="Drug Ask ICD-10", page_icon="💊", layout="wide")

# =========================
# STYLE (คงเดิม)
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
# LOAD DATA (คงเดิม แต่เพิ่มการล้างคอลัมน์ให้สะอาด)
# =========================
@st.cache_data
def load_data():
    all_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="ALL_DATA")
    chronic_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="CHRONIC_26")

    for temp_df in [all_df, chronic_df]:
        temp_df.dropna(how="all", inplace=True)
        temp_df.columns = temp_df.columns.str.strip() # ตัดช่องว่างหัวคอลัมน์

    return all_df, chronic_df

df, chronic_df = load_data()

# =========================
# SESSION STATE (คงเดิม)
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
# SIDEBAR (คงเดิม)
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio("เมนู", ["🔍 ค้นหา", "📊 Dashboard"])
data_mode = st.sidebar.radio(
    "📂 เลือกฐานข้อมูล",
    ["ข้อมูลทั้งหมด", "26 โรคเรื้อรัง"]
)

# --- จุดสำคัญ: เลือก Dataset และ Update ชื่อคอลัมน์ให้ตรงตาม Sheet ที่เลือก ---
if data_mode == "ข้อมูลทั้งหมด":
    data = df
else:
    data = chronic_df

# ดึงชื่อคอลัมน์ใหม่ทุกครั้งที่เปลี่ยน Sheet เพื่อป้องกัน KeyError
drug_col = data.columns[0]
property_col = data.columns[1]
code_col = data.columns[2]
# ถ้ามีคอลัมน์ที่ 4 (ใน Chronic 26) ให้เก็บชื่อไว้ใช้
extra_col = data.columns[3] if len(data.columns) > 3 else None

# =========================
# 🔍 SEARCH (คงสภาพเดิมของคุณไว้)
# =========================
if menu == "🔍 ค้นหา":
    st.subheader(f"🔍 ค้นหายา / ICD ({data_mode})")

    colb1, colb2, colb3 = st.columns(3)
    with colb1:
        if st.button("📌 เฉพาะโรคเรื้อรัง"):
            # ตัวเลือกนี้จะบังคับสลับโหมด แต่ปกติใช้ Radio ด้านข้างจะเสถียรกว่า
            st.info("กรุณาเลือก '26 โรคเรื้อรัง' ที่แถบด้านข้าง")

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

    # SEARCH UI
    search = st.text_input("🔍 พิมพ์ค้นหา", key="search")

    col1, col2 = st.columns(2)
    with col1:
        # ปรับ sorted ให้รองรับข้อมูลหลายแบบ และตัดค่าว่าง
        drug_options = [""] + sorted(data[drug_col].dropna().astype(str).unique())
        selected_drug = st.selectbox("💊 เลือกยา", drug_options, key="drug")

    with col2:
        code_options = [""] + sorted(data[code_col].dropna().astype(str).unique())
        selected_code = st.selectbox("🦠 เลือก ICD", code_options, key="code")

    # FILTER LOGIC (คงเดิม)
    result = data.copy()
    if search:
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False, na=False) |
            result[code_col].astype(str).str.contains(search, case=False, na=False)
        ]
    if selected_drug:
        result = result[result[drug_col].astype(str) == selected_drug]
    if selected_code:
        result = result[result[code_col].astype(str).str.startswith(selected_code)]

    # SHOW DISEASE NAME (รองรับคอลัมน์ที่ 4 ที่เพิ่มมา)
    if data_mode == "26 โรคเรื้อรัง" and selected_code and extra_col:
        # ค้นหาชื่อโรคจากคอลัมน์ที่ 4
        disease_names = data[data[code_col].astype(str).str.startswith(selected_code)][extra_col].dropna().unique()
        if len(disease_names) > 0:
            st.success(f"🦠 {disease_names[0]}")

    # HIGHLIGHT & GRAPH (คงเดิม)
    if "ใช้บ่อย" in result.columns:
        frequent = result[result["ใช้บ่อย"] == "⭐"]
        if not frequent.empty:
            st.markdown("### ⭐ ยาที่ใช้บ่อย")
            for d in frequent[drug_col].unique():
                st.markdown(f'<div class="highlight">⭐ {d}</div>', unsafe_allow_html=True)

    if not result.empty:
        st.markdown("### 📊 จำนวนยา")
        st.bar_chart(result[drug_col].value_counts().head(10))
        # แสดงตารางตามคอลัมน์ที่มี
        st.dataframe(result, use_container_width=True)

# =========================
# 📊 DASHBOARD (คงสภาพเดิมของคุณไว้)
# =========================
else:
    st.subheader(f"📊 Dashboard {data_mode}")
    # ใช้ data ตามที่เลือกจาก Sidebar
    selected_code_db = st.selectbox(
        "🦠 เลือก ICD สำหรับวิเคราะห์",
        sorted(data[code_col].astype(str).unique())
    )

    filtered = data[data[code_col].astype(str).str.startswith(selected_code_db)]

    if extra_col: # ถ้ามีคอลัมน์ที่ 4 แสดงชื่อโรค
        name = filtered[extra_col].dropna().unique()
        if len(name) > 0: st.info(f"📌 {name[0]}")

    col1, col2 = st.columns(2)
    col1.metric("จำนวนรายการยา", len(filtered))
    col2.metric("จำนวนสรรพคุณ", filtered[property_col].nunique())

    st.markdown("### 📈 Top ยา")
    st.bar_chart(filtered[drug_col].value_counts().head(10))
    st.dataframe(filtered, use_container_width=True)
