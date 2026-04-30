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
    all_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="ALL_DATA")
    chronic_df = pd.read_excel("DRUG DISEASE.xlsx", sheet_name="CHRONIC_26")

    for temp_df in [all_df, chronic_df]:
        temp_df.dropna(how="all", inplace=True)
        temp_df.columns = temp_df.columns.str.strip() 

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

# --- แก้ไขจุดสำคัญ: กำหนด Column Name ให้ชัดเจนป้องกันการสลับ ---
if data_mode == "ข้อมูลทั้งหมด":
    data = df
    # สมมติลำดับชีท ALL_DATA: ยา, สรรพคุณ, ICD
    drug_col = data.columns[0]
    prop_col = data.columns[1]
    code_col = data.columns[2]
    extra_col = None
else:
    data = chronic_df
    # สำหรับชีท 26 โรคเรื้อรัง บังคับให้ตรงตามหัวข้อ
    # ตรวจสอบหาชื่อคอลัมน์ที่มีคำว่า 'ICD' หรือ 'รหัส' เพื่อความแม่นยำ
    drug_col = data.columns[0]  # คอลัมน์แรกมักเป็นชื่อยา
    prop_col = data.columns[1]  # คอลัมน์ที่สองเป็นสรรพคุณ
    code_col = data.columns[2]  # คอลัมน์ที่สามเป็นรหัสโรค
    extra_col = data.columns[3] if len(data.columns) > 3 else None # คอลัมน์ที่สี่เป็นชื่อโรค

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":
    st.subheader(f"🔍 ค้นหายา / ICD ({data_mode})")

    colb1, colb2, colb3 = st.columns(3)
    with colb1:
        if st.button("📌 เฉพาะโรคเรื้อรัง"):
            st.info("กรุณาเลือก '26 โรคเรื้อรัง' ที่แถบเมนูด้านซ้าย")
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

    search = st.text_input("🔍 พิมพ์ค้นหา", key="search")

    col1, col2 = st.columns(2)
    with col1:
        # DROP DOWN เลือกยา (ดึงจาก drug_col)
        drug_list = [""] + sorted(data[drug_col].dropna().astype(str).unique())
        selected_drug = st.selectbox("💊 เลือกยา", drug_list, key="drug")
    with col2:
        # DROP DOWN เลือกรหัสโรค (ดึงจาก code_col)
        code_list = [""] + sorted(data[code_col].dropna().astype(str).unique())
        selected_code = st.selectbox("🦠 เลือก ICD", code_list, key="code")

    result = data.copy()

    # FILTERING
    if search:
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False, na=False) |
            result[code_col].astype(str).str.contains(search, case=False, na=False)
        ]
    if selected_drug:
        result = result[result[drug_col].astype(str) == selected_drug]
    if selected_code:
        result = result[result[code_col].astype(str) == selected_code]

    # แสดงชื่อโรค (Success Box)
    if selected_code and extra_col:
        name = data[data[code_col].astype(str) == selected_code][extra_col].dropna().unique()
        if len(name) > 0:
            st.success(f"🦠 {name[0]}")

    # ตารางหลัก
    st.dataframe(result, use_container_width=True)

    # --- ส่วนที่ขยายข้อความสรรพคุณ (อ่านง่าย) ---
    if not result.empty:
        st.markdown("### 📄 รายละเอียดสรรพคุณยา (คลิกเพื่อขยายอ่าน)")
        for i, row in result.iterrows():
            exp_title = f"💊 {row[drug_col]} | รหัส: {row[code_col]}"
            if extra_col and pd.notna(row[extra_col]):
                exp_title += f" | 📌 {row[extra_col]}"
            
            with st.expander(exp_title):
                st.markdown("**สรรพคุณและรายละเอียด:**")
                st.info(row[prop_col])

# =========================
# 📊 DASHBOARD
# =========================
else:
    st.subheader(f"📊 Dashboard {data_mode}")

    # Dropdown ใน Dashboard (ต้องตรงตามรหัสโรค)
    selected_code_db = st.selectbox(
        "🦠 เลือก ICD",
        sorted(data[code_col].dropna().astype(str).unique())
    )

    filtered = data[data[code_col].astype(str) == selected_code_db]

    if extra_col:
        name_db = filtered[extra_col].dropna().unique()
        if len(name_db) > 0:
            st.success(f"📌 {name_db[0]}")

    col1, col2 = st.columns(2)
    col1.metric("จำนวนยา", len(filtered))
    col2.metric("จำนวนสรรพคุณ", filtered[prop_col].nunique())

    st.markdown("### 📈 Top ยา")
    st.bar_chart(filtered[drug_col].value_counts().head(10))

    st.markdown("### 📊 จำนวนยาแต่ละโรค")
    chart = data.groupby(code_col)[drug_col].count()
    st.bar_chart(chart)

    st.dataframe(filtered, use_container_width=True)
