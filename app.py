import pandas as pd
import streamlit as st

st.set_page_config(page_title="PR Catalog", page_icon="🔍", layout="wide")

st.title("📚 ระบบค้นหาข้อมูล Purchase Requisition (ใบขอซื้อ)  แคตตาล็อกอุปกรณ์")
st.write("พิมพ์คำค้นหาเพื่อดูข้อมูล PR (ข้อมูลนี้สำหรับค้นหาเท่านั้น)")

# ส่วนดึงข้อมูลจาก Google Sheets (ใช้ลิงก์ CSV)
@st.cache_data(ttl=600)
def load_data():
  # แทนที่ URL ด้านล่างด้วยลิงก์ CSV ของ Google Sheet ของคุณ
  sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxcG6Zwu5wffcY9sYnrIo6Rukcv5Nw9EbtMU7TyCOR8uW2XGAEThrk-0500Y7ELiVDg_7EeJcitl4/pub?gid=0&single=true&output=csv"
  df = pd.read_csv(sheet_url)
  return df


try:
  df = load_data()

  search_query = st.text_input(
      "🔍 ค้นหาข้อมูล (พิมพ์คีย์เวิร์ด เช่น ชื่ออุปกรณ์ โค้ดสินค้าหรือหมวดหมู่):"
  )

  if search_query:
    mask = (
        df.astype(str)
        .apply(lambda x: x.str.contains(search_query, case=False, na=False))
        .any(axis=1)
    )
    result_df = df[mask]

    st.write(
        f"ผลการค้นหา: พบ {len(result_df)} รายการสำหรับ '{search_query}'"
    )

    if not result_df.empty:
      st.dataframe(result_df, use_container_width=True, hide_index=True)
    else:
      st.warning("ไม่พบข้อมูลที่ค้นหา")
  else:
    st.info("กรุณาพิมพ์คำค้นหาในช่องด้านบน")

except Exception as e:
  st.error(
      "ยังไม่ได้ใส่ลิงก์ Google Sheet หรือลิงก์ยังไม่ถูกต้อง กรุณาตรวจสอบลิงก์"
  )
