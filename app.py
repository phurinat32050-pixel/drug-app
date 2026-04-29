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

    for df in [all_df, chronic_df]:
        df.dropna(how="all", inplace=True)
        df.columns = df.columns.str.strip()

    return all_df, chronic_df

df, chronic_df = load_data()

# =========================
# COLUMN AUTO MAP
# =========================
drug_col = df.columns[0]
property_col = df.columns[1]
code_col = df.columns[2]

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

# เลือก dataset
data = df if data_mode == "ข้อมูลทั้งหมด" else chronic_df

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":

    st.subheader("🔍 ค้นหายา / ICD")

    colb1, colb2, colb3 = st.columns(3)

    with colb1:
        if st.button("📌 เฉพาะโรคเรื้อรัง"):
            data = chronic_df

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
        selected_drug = st.selectbox(
            "💊 เลือกยา",
            [""] + sorted(data[drug_col].astype(str).unique()),
            key="drug"
        )

    with col2:
        selected_code = st.selectbox(
            "🦠 เลือก ICD",
            [""] + sorted(data[code_col].astype(str).unique()),
            key="code"
        )

    result = data.copy()

    # SEARCH FILTER
    if search:
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False) |
            result[code_col].astype(str).str.contains(search, case=False)
        ]

    # DRUG FILTER
    if selected_drug:
        result = result[result[drug_col] == selected_drug]

    # ICD FILTER
    if selected_code:
        result = result[
            result[code_col].astype(str).str.startswith(selected_code)
        ]

    # =========================
    # 🦠 SHOW DISEASE NAME
    # =========================
    if data_mode == "26 โรคเรื้อรัง" and selected_code:
        if "ชื่อโรค" in chronic_df.columns:
            name = chronic_df[
                chronic_df[code_col].astype(str).str.startswith(selected_code)
            ]["ชื่อโรค"].dropna().unique()

            if len(name) > 0:
                st.success(f"🦠 {name[0]}")

    # =========================
    # ⭐ HIGHLIGHT DRUG
    # =========================
    if data_mode == "26 โรคเรื้อรัง" and "ใช้บ่อย" in result.columns:

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

    # TABLE
    st.dataframe(result[[drug_col, property_col, code_col]], use_container_width=True)

# =========================
# 📊 DASHBOARD
# =========================
else:

    st.subheader("📊 Dashboard โรคเรื้อรัง")

    # ใช้เฉพาะ chronic
    data = chronic_df.copy()

    selected_code = st.selectbox(
        "🦠 เลือก ICD",
        sorted(data[code_col].astype(str).unique())
    )

    filtered = data[
        data[code_col].astype(str).str.startswith(selected_code)
    ]

    # ชื่อโรค
    if "ชื่อโรค" in data.columns:
        name = filtered["ชื่อโรค"].dropna().unique()
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
    st.dataframe(filtered[[drug_col, property_col]], use_container_width=True)
