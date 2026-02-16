import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drug & Disease Search", page_icon="💊")

st.title("💊 เว็บค้นหาข้อมูลยาและโรค")

# อ่านไฟล์ Excel
df = pd.read_excel("DRUG DISEASE.xlsx")

# ลบแถวว่างทั้งหมด
df = df.dropna(how="all")

# ใช้คอลัมน์แรกเป็นตัวเลือก
column_name = df.columns[0]

# สร้างตัวเลือกแบบไม่ซ้ำ และเรียง A-Z
options = sorted(df[column_name].astype(str).unique())

# เลือกได้หลายรายการ
selected_items = st.multiselect(
    "เลือกชื่อยา / โรค (เลือกได้หลายรายการ)",
    options
)

# แสดงผลเมื่อมีการเลือก
if selected_items:
    result = df[df[column_name].isin(selected_items)]
    
    st.subheader("📋 ผลการค้นหา")
    st.dataframe(result, use_container_width=True)
