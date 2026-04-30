import streamlit as st
import pandas as pd
import io

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
[data-testid="stDataEditor"] {
    border-radius: 10px;
    border: 1px solid #ddd;
}
thead tr th {
    background-color: #1f4e79 !important;
    color: white !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🏥 ระบบค้นหายาและรหัสโรคผู้ป่วยนอก (OPD)</div>', unsafe_allow_html=True)

# =========================
# FUNCTIONS
# =========================
def convert_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

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
# SIDEBAR
# =========================
st.sidebar.title("📋 เมนูระบบ")

menu = st.sidebar.radio("เมนู", ["🔍 ค้นหา", "📊 Dashboard"])
data_mode = st.sidebar.radio("📂 เลือกฐานข้อมูล", ["ข้อมูลทั้งหมด", "26 โรคเรื้อรัง"])

data = df if data_mode == "ข้อมูลทั้งหมด" else chronic_df

drug_col = data.columns[0]
property_col = data.columns[1]
code_col = data.columns[2]
disease_name_col = data.columns[3] if len(data.columns) > 3 else None

# =========================
# 🔍 SEARCH
# =========================
if menu == "🔍 ค้นหา":

    st.subheader(f"🔍 ค้นหายา / ICD ({data_mode})")

    search = st.text_input("🔍 พิมพ์ค้นหา")

    col1, col2 = st.columns(2)

    with col1:
        drug_list = [""] + sorted(data[drug_col].dropna().astype(str).unique())
        selected_drug = st.selectbox("💊 เลือกยา", drug_list)

    with col2:
        code_list = [""] + sorted(data[code_col].dropna().astype(str).unique())
        selected_code = st.selectbox("🦠 เลือก ICD", code_list)

    result = data.copy()

    # 🔎 NORMAL SEARCH (แทน fuzzy)
    if search:
        search = search.strip()
        result = result[
            result[drug_col].astype(str).str.contains(search, case=False, na=False, regex=False) |
            result[code_col].astype(str).str.contains(search, case=False, na=False, regex=False)
        ]

    if selected_drug:
        result = result[result[drug_col].astype(str) == selected_drug]

    if selected_code:
        result = result[result[code_col].astype(str).str.startswith(selected_code)]

    # 🦠 ชื่อโรค
    if selected_code and disease_name_col:
        name = data[data[code_col].astype(str).str.startswith(selected_code)][disease_name_col].dropna().unique()
        if len(name) > 0:
            st.success(f"🦠 {name[0]}")

    # ⭐ highlight ยาใช้บ่อย
    if "ใช้บ่อย" in result.columns:
        frequent = result[result["ใช้บ่อย"] == "⭐"]
        if not frequent.empty:
            st.markdown("### ⭐ ยาที่ใช้บ่อย")
            for d in frequent[drug_col].unique():
                st.markdown(f'<div class="highlight">⭐ {d}</div>', unsafe_allow_html=True)

    # =========================
    # 📋 TABLE SMART
    # =========================
    if not result.empty:

        display_df = result.copy()

        new_cols = ["💊 ยา", "📌 สรรพคุณ", "🦠 ICD"]
        if disease_name_col:
            new_cols.append("📖 ชื่อโรค")

        display_df.columns = new_cols
        display_df = display_df.sort_values(by="💊 ยา").reset_index(drop=True)

        st.markdown("### 📋 ตารางข้อมูล (Filter ได้)")

        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            height=500,
            num_rows="dynamic"
        )

        # 📊 GRAPH SYNC
        if not edited_df.empty:
            st.markdown("### 📊 กราฟจากตาราง")
            st.bar_chart(edited_df["💊 ยา"].value_counts())

        # 📥 EXPORT
        st.markdown("### 📥 ดาวน์โหลด")

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "📥 CSV",
                edited_df.to_csv(index=False),
                "data.csv"
            )

        with c2:
            st.download_button(
                "📥 Excel",
                convert_to_excel(edited_df),
                "data.xlsx"
            )

    else:
        st.warning("ไม่พบข้อมูล")

# =========================
# 📊 DASHBOARD
# =========================
else:

    st.subheader(f"📊 Dashboard {data_mode}")

    selected_code = st.selectbox(
        "🦠 เลือก ICD",
        sorted(data[code_col].dropna().astype(str).unique())
    )

    filtered = data[data[code_col].astype(str).str.startswith(selected_code)]

    if disease_name_col:
        name = filtered[disease_name_col].dropna().unique()
        if len(name) > 0:
            st.success(f"📌 {name[0]}")

    col1, col2 = st.columns(2)
    col1.metric("จำนวนยา", len(filtered))
    col2.metric("จำนวนสรรพคุณ", filtered[property_col].nunique())

    st.markdown("### 📈 Top ยา")
    st.bar_chart(filtered[drug_col].value_counts().head(10))

    st.markdown("### 📊 จำนวนยาแต่ละโรค")
    st.bar_chart(data.groupby(code_col)[drug_col].count())

    st.markdown("### 💊 รายการยา")
    st.dataframe(filtered, use_container_width=True)
