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
    df.columns = df.columns.str.strip()
except:
    st.error("❌ โหลดไฟล์ไม่ได้")
    st.stop()

# =========================
# หา column อัตโนมัติ
# =========================
drug_col = None
disease_col = None
code_col = None

for col in df.columns:
    if "ยา" in col:
        drug_col = col
    elif "วินิจฉัย" in col:
        disease_col = col
    elif "รหัส" in col:
        code_col = col

if not drug_col or not disease_col or not code_col:
    st.error(f"❌ คอลัมน์ไม่ครบ: {list(df.columns)}")
    st.stop()

# =========================
# 🔥 ฟังก์ชัน AI (กึ่ง AI)
# =========================
def ai_suggest(drug_input):
    drug_input = drug_input.lower()
    result = df[df[drug_col].astype(str).str.lower().str.contains(drug_input)]

    if not result.empty:
        return result[[drug_col, disease_col, code_col]].drop_duplicates()
    else:
        return None

# =========================
# เลือกโหมด
# =========================
mode = st.radio(
    "🔍 เลือกโหมด",
    ["ยา → รหัสโรค", "รหัสโรค → ยา", "🤖 AI แนะนำโรค"],
    horizontal=True
)

st.divider()

# =========================
# 🟢 โหมด 1
# =========================
if mode == "ยา → รหัสโรค":

    selected = st.multiselect("💊 เลือกยา", sorted(df[drug_col].astype(str).unique()))
    result = df[df[drug_col].isin(selected)] if selected else df

    st.dataframe(result[[drug_col, code_col]], use_container_width=True)

# =========================
# 🔵 โหมด 2
# =========================
elif mode == "รหัสโรค → ยา":

    selected = st.multiselect("🦠 เลือกรหัสโรค", sorted(df[code_col].astype(str).unique()))
    result = df[df[code_col].isin(selected)] if selected else df

    st.dataframe(result[[drug_col, code_col]], use_container_width=True)

# =========================
# 🤖 โหมด 3: AI
# =========================
else:

    st.subheader("🤖 AI แนะนำโรคจากชื่อยา")

    user_input = st.text_input("💬 พิมพ์ชื่อยา เช่น Metformin")

    if user_input:
        ai_result = ai_suggest(user_input)

        if ai_result is not None:
            st.success("✅ AI แนะนำผลลัพธ์")
            st.dataframe(ai_result, use_container_width=True)
        else:
            st.warning("❌ ไม่พบข้อมูล")
