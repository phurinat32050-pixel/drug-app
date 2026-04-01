import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drug & Disease System", page_icon="💊", layout="wide")
st.title("💊 ระบบค้นหายาและรหัสโรค")

# =========================
# โหลดข้อมูล
# =========================
try:
    df = pd.read_excel("DRUG DISEASE.xlsx")
    df = df.dropna(how="all")

    # 🔥 ล้างชื่อคอลัมน์ (กันช่องว่างแอบ)
    df.columns = df.columns.str.strip()

except:
    st.error("❌ โหลดไฟล์ DRUG DISEASE.xlsx ไม่ได้")
    st.stop()

# =========================
# 🔥 หา column อัตโนมัติ (แก้ปัญหา 'คำวินิจฉัย')
# =========================
drug_col = None
disease_col = None

for col in df.columns:
    if "ยา" in col:
        drug_col = col
    if "วินิจฉัย" in col or "โรค" in col:
        disease_col = col

# 🔥 เช็คว่าหาเจอไหม
if not drug_col or not disease_col:
    st.error(f"❌ หา column ไม่เจอ\nมีแค่: {list(df.columns)}")
    st.stop()

# =========================
# เปลี่ยนโหมดเป็นปุ่ม Radio
# =========================
mode = st.radio(
    "🔍 เลือกโหมดการค้นหา",
    ["ยา → รหัสโรค", "รหัสโรค → ยา"],
    horizontal=True
)

# =========================
# 🟢 โหมด 1: ยา → โรค
# =========================
if mode == "ยา → รหัสโรค":

    col1, col2 = st.columns(2)

    with col1:
        drugs = sorted(df[drug_col].astype(str).unique())
        selected_drugs = st.multiselect("💊 เลือกยา", drugs)

    with col2:
        keyword = st.text_input("🔎 ค้นหาเพิ่มเติม")

    result = df.copy()

    if selected_drugs:
        result = result[result[drug_col].isin(selected_drugs)]

    if keyword:
        result = result[result.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False).any(), axis=1
        )]

    if not result.empty:
        st.success("✅ พบข้อมูล")
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("ไม่พบข้อมูล")

# =========================
# 🔵 โหมด 2: โรค → ยา
# =========================
else:

    col1, col2 = st.columns(2)

    with col1:
        diseases = sorted(df[disease_col].astype(str).unique())
        selected_diseases = st.multiselect("🦠 เลือกรหัสโรค", diseases)

    with col2:
        keyword = st.text_input("🔎 ค้นหาเพิ่มเติม")

    result = df.copy()

    if selected_diseases:
        result = result[result[disease_col].isin(selected_diseases)]

    if keyword:
        result = result[result.astype(str).apply(
            lambda row: row.str.contains(keyword, case=False).any(), axis=1
        )]

    if not result.empty:
        st.success("✅ พบข้อมูล")
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("ไม่พบข้อมูล")
