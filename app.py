import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Drug Ask ICD-10", page_icon="💊", layout="wide")

# ปรับปรุง CSS เพิ่มเติม
st.markdown("""
<style>
    .header {
        background-color: #1f4e79;
        padding: 15px;
        border-radius: 10px;
        color: white;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .property-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f4e79;
        line-height: 1.6;
    }
    .disease-tag {
        background-color: #e1f5fe;
        color: #01579b;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.85em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥 ระบบค้นหายาและรหัสโรค 26 โรคเรื้อรัง</div>', unsafe_allow_html=True)

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

df_all, df_chronic = load_data()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio("เมนู", ["🔍 ค้นหา", "📊 Dashboard"])
data_mode = st.sidebar.radio("📂 ฐานข้อมูล", ["ข้อมูลทั้งหมด", "26 โรคเรื้อรัง"])

# เลือก Dataset หลัก
data = df_all if data_mode == "ข้อมูลทั้งหมด" else df_chronic

# แมพคอลัมน์ (อิงตามโครงสร้างใหม่ที่คุณต้องการ)
# 0:ชื่อยา, 1:สรรพคุณ, 2:ICD-10, 3:ชื่อโรค
drug_col = data.columns[0]
prop_col = data.columns[1]
icd_col = data.columns[2]
disease_col = data.columns[3] if len(data.columns) > 3 else None

# =========================
# 🔍 MENU: SEARCH (ปรับการแสดงผลให้อ่านง่าย)
# =========================
if menu == "🔍 ค้นหา":
    st.subheader(f"🔍 ค้นหายา / ICD ({data_mode})")
    
    search = st.text_input("🔍 พิมพ์เพื่อค้นหา (ชื่อยา, รหัส ICD หรือชื่อโรค)", "")

    # กรองข้อมูล
    result = data.copy()
    if search:
        search_filter = (
            result[drug_col].astype(str).str.contains(search, case=False, na=False) |
            result[icd_col].astype(str).str.contains(search, case=False, na=False)
        )
        if disease_col:
            search_filter |= result[disease_col].astype(str).str.contains(search, case=False, na=False)
        result = result[search_filter]

    st.write(f"พบข้อมูลทั้งหมด {len(result)} รายการ")
    st.divider()

    # แสดงผลรูปแบบ List/Cards อ่านง่าย
    for i, row in result.iterrows():
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"### 💊 {row[drug_col]}")
                if disease_col:
                    st.markdown(f"<span class='disease-tag'>🦠 {row[disease_col]}</span> | **ICD:** {row[icd_col]}", unsafe_allow_html=True)
                else:
                    st.markdown(f"**ICD:** {row[icd_col]}")
            
            # ส่วนของสรรพคุณที่เนื้อหาเยอะ ใช้ Expander เพื่อความสวยงาม
            with st.expander("📄 คลิกเพื่อดูสรรพคุณยา"):
                st.markdown(f"<div class='property-box'>{row[prop_col]}</div>", unsafe_allow_html=True)
            st.divider()

# =========================
# 📊 MENU: DASHBOARD (เน้นชื่อโรคภาษาไทย)
# =========================
else:
    st.subheader(f"📊 Dashboard: {data_mode}")

    if disease_col:
        # เลือกโรคจาก "ชื่อโรค" (คอลัมน์ที่ 4)
        disease_list = sorted(data[disease_col].dropna().unique())
        selected_disease = st.selectbox("🎯 เลือกชื่อโรคเรื้อรัง", disease_list)
        
        filtered = data[data[disease_col] == selected_disease]
        
        # แสดงรหัส ICD ของโรคนั้น
        icd_code = filtered[icd_col].iloc[0]
        st.info(f"**รหัสรหัสโรค (ICD-10):** {icd_code}")
    else:
        # กรณี Sheet ไม่มีชื่อโรค ให้ใช้ ICD ตามเดิม
        selected_code = st.selectbox("🦠 เลือก ICD", sorted(data[icd_col].unique()))
        filtered = data[data[icd_col] == selected_code]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("จำนวนยาในกลุ่มนี้", f"{len(filtered)} รายการ")
    col2.metric("จำนวนสรรพคุณ", f"{filtered[prop_col].nunique()} ประเภท")
    col3.metric("รหัสโรค", filtered[icd_col].iloc[0] if not filtered.empty else "-")

    # Visualization
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("### 📈 รายชื่อยาที่มีในระบบ")
        st.bar_chart(filtered[drug_col].value_counts())
    
    with c_right:
        st.markdown("### 📋 สรุปรายการยาและสรรพคุณ")
        # ในหน้า Dashboard แสดงเป็นตารางแบบย่อ
        st.dataframe(filtered[[drug_col, prop_col]], use_container_width=True, hide_index=True)

    # กราฟภาพรวมทั้งหมด
    st.markdown("---")
    st.markdown("### 📊 ภาพรวมจำนวนยาแยกตามโรค")
    target_col = disease_col if disease_col else icd_col
    overall_chart = data[target_col].value_counts()
    st.bar_chart(overall_chart)
