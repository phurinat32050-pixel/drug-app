import streamlit as st
import pandas as pd

# =========================
# CONFIG & STYLE
# =========================
st.set_page_config(page_title="Drug Ask ICD-10", page_icon="💊", layout="wide")

st.markdown("""
<style>
.header { background-color: #1f4e79; padding: 15px; border-radius: 10px; color: white; font-size: 22px; font-weight: bold; }
.highlight { background-color: #fff3cd; padding: 10px; border-left: 6px solid orange; border-radius: 8px; margin-bottom:5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥 ระบบค้นหายาและรหัสโรคผู้ป่วยนอก (OPD)</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA
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
# SIDEBAR & DATA SELECTION
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio("เมนู", ["🔍 ค้นหา", "📊 Dashboard"])
data_mode = st.sidebar.radio("📂 เลือกฐานข้อมูล", ["ข้อมูลทั้งหมด", "26 โรคเรื้อรัง"])

data = df if data_mode == "ข้อมูลทั้งหมด" else chronic_df

# --- แมพคอลัมน์ตามโจทย์ ---
# คอลัมน์ 1 (Index 0): ชื่อยา
# คอลัมน์ 2 (Index 1): ชื่อโรค -> ใช้ใน Dropdown 2
# คอลัมน์ 3 (Index 2): รหัส ICD
# คอลัมน์ 4 (Index 3): สรรพคุณยา -> ใช้แสดงผลในรายละเอียด
drug_col = data.columns[0]
disease_col = data.columns[1] # คอลัมน์ 2
code_col = data.columns[2]
prop_col = data.columns[3]    # คอลัมน์ 4

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":
    st.subheader(f"🔍 ค้นหา ({data_mode})")

    colb1, colb2, colb3 = st.columns(3)
    with colb2:
        if st.button("❌ ล้างค่า"):
            st.session_state.clear()
            st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        drug_list = [""] + sorted(data[drug_col].dropna().astype(str).unique())
        selected_drug = st.selectbox("💊 เลือกชื่อยา (คอลัมน์ 1)", drug_list, key="drug_select")
    
    with col2:
        # Dropdown ตัวที่ 2 แสดง "ชื่อโรค" (คอลัมน์ที่ 2)
        disease_list = [""] + sorted(data[disease_col].dropna().astype(str).unique())
        selected_disease = st.selectbox("🦠 เลือกชื่อโรค (คอลัมน์ 2)", disease_list, key="disease_select")

    result = data.copy()

    # Filter ข้อมูล
    if selected_drug:
        result = result[result[drug_col].astype(str) == selected_drug]
    if selected_disease:
        result = result[result[disease_col].astype(str) == selected_disease]

    # การแสดงผล
    if not result.empty:
        st.markdown("### 📊 ผลการค้นหา")
        st.dataframe(result, use_container_width=True)

        # --- ส่วนขยาย: แสดงสรรพคุณยา (ดึงจากคอลัมน์ที่ 4) ---
        st.markdown("### 📄 รายละเอียดสรรพคุณยา (ข้อมูลจากคอลัมน์ 4)")
        for i, row in result.iterrows():
            # หัวข้อแสดง ชื่อยา และ ชื่อโรค
            exp_title = f"💊 {row[drug_col]} | 📌 โรค: {row[disease_col]} | 🦠 ICD: {row[code_col]}"
            
            with st.expander(exp_title):
                st.write("**รายละเอียดสรรพคุณ:**")
                # ดึงข้อมูลจากคอลัมน์ที่ 4 มาแสดง
                st.info(row[prop_col])

# =========================
# 📊 DASHBOARD
# =========================
else:
    st.subheader(f"📊 Dashboard {data_mode}")
    
    selected_db = st.selectbox("🦠 เลือกชื่อโรค", sorted(data[disease_col].dropna().unique()))
    filtered = data[data[disease_col] == selected_db]
    
    col1, col2 = st.columns(2)
    col1.metric("จำนวนยาที่พบ", len(filtered))
    col2.metric("รหัสโรค", filtered[code_col].iloc[0] if not filtered.empty else "-")

    st.bar_chart(filtered[drug_col].value_counts())
    st.markdown("### รายการข้อมูลทั้งหมด")
    st.dataframe(filtered, use_container_width=True)
