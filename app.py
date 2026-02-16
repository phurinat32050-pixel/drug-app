import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drug & Disease Search", page_icon="💊")

st.title("💊 เว็บค้นหาข้อมูลยาและโรค")

# อ่านไฟล์ Excel
df = pd.read_excel("DRUG DISEASE.xlsx")

# ลบแถวว่าง
df = df.dropna()

# ใช้คอลัมน์แรกเป็นตัวเลือก
column_name = df.columns[0]

options = sorted(df[column_name].astype(str).unique())

# 🔥 เลือกได้หลายอัน
selected_items = st.multiselect(
    "เลือกชื่อยา / โรค (เลือกได้หลายรายการ)",
    options
)

if selected_items:
    result = df[df[column_name].isin(selected_items)]
    
    st.subheader("ผลการค้นหา")
    st.dataframe(result)
else:
    st.info("กรุณาเลือกอย่างน้อย 1 รายการ")
