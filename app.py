import streamlit as st
import pandas as pd

st.set_page_config(page_title="Drug Search", page_icon="💊")

st.title("💊 เว็บค้นหาข้อมูลยา")

# อ่านไฟล์ Excel
df = pd.read_excel("drug.xlsx")

search = st.text_input("พิมพ์ชื่อยาเพื่อค้นหา")

if search:
    result = df[df.iloc[:,0].astype(str).str.contains(search, case=False, na=False)]

    if not result.empty:
        st.dataframe(result)
    else:
        st.warning("ไม่พบข้อมูลยา")
