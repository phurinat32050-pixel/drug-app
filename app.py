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
.highlight {
    background-color: #fff3cd;
    padding: 10px;
    border-radius: 8px;
    border-left: 6px solid orange;
    margin-bottom:5px;
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
# SESSION INIT
# =========================
if "chronic" not in st.session_state:
    st.session_state.chronic = False
if "drug_select" not in st.session_state:
    st.session_state.drug_select = ""
if "code_select" not in st.session_state:
    st.session_state.code_select = ""
if "search_box" not in st.session_state:
    st.session_state.search_box = ""

# =========================
# ICD
# =========================
disease_map = {
    "E11":"เบาหวาน","I10":"ความดัน","I50":"หัวใจล้มเหลว"
}

chronic_codes = list(disease_map.keys())

# =========================
# MENU
# =========================
st.sidebar.title("📋 เมนูระบบ")
menu = st.sidebar.radio("เลือกการทำงาน", ["🔍 ค้นหา", "📊 Dashboard"])

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":

    st.subheader("🔍 ค้นหายาและรหัสโรค")

    # ===== ปุ่ม =====
    colb1, colb2, colb3 = st.columns(3)

    with colb1:
        if st.button("📌 26 โรคเรื้อรัง"):
            st.session_state.chronic = True

    with colb2:
        if st.button("❌ ล้างตัวกรอง"):
            st.session_state.chronic = False
            st.session_state.drug_select = ""
            st.session_state.code_select = ""
            st.session_state.search_box = ""
            st.rerun()

    with colb3:
        if st.button("🔄 รีเซ็ตทั้งหมด"):
            st.session_state.clear()
            st.rerun()

    # ===== search =====
    search = st.text_input("🔍 ค้นหา", key="search_box")

    col1, col2 = st.columns(2)

    with col1:
        selected_drug = st.selectbox(
            "💊 เลือกยา",
            [""] + sorted(df[drug_col].astype(str).unique()),
            key="drug_select"
        )

    with col2:
        selected_code = st.selectbox(
            "🦠 เลือกรหัสโรค",
            [""] + sorted(df[code_col].astype(str).unique()),
            key="code_select"
        )

    result = df.copy()

    # ===== filter =====
    if st.session_state.chronic:
        result = result[
            result[code_col]
            .astype(str)
            .str.strip()
            .str.startswith(tuple(chronic_codes))
        ]

    if search:
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False) |
            result[code_col].astype(str).str.contains(search, case=False)
        ]

    if selected_drug:
        result = result[result[drug_col] == selected_drug]

    if selected_code:
        result = result[
            result[code_col]
            .astype(str)
            .str.startswith(selected_code)
        ]

        if selected_code in disease_map:
            st.info(f"🦠 {disease_map[selected_code]}")

    # =========================
    # TABLE
    # =========================
    st.dataframe(result[[drug_col, property_col, code_col]], use_container_width=True)

# =========================
# DASHBOARD
# =========================
else:

    st.subheader("📊 Dashboard")

    selected_code = st.selectbox(
        "🦠 เลือกโรค",
        sorted(df[code_col].astype(str).unique()),
        key="dashboard_code"
    )

    filtered = df[
        df[code_col]
        .astype(str)
        .str.strip()
        .str.startswith(selected_code)
    ]

    st.bar_chart(filtered[drug_col].value_counts().head(10))
