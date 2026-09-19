import pandas as pd
import streamlit as st

st.set_page_config(page_title="PR Catalog", page_icon="🔍", layout="wide")

st.title("📚 ระบบค้นหาข้อมูลแคตตาล็อกอุปกรณ์(PR)  ")
st.write("พิมพ์คำค้นหาเพื่อดูข้อมูล PR (ข้อมูลนี้สำหรับค้นหาเท่านั้น)")

# ส่วนดึงข้อมูลจาก Google Sheets (ใช้ลิงก์ CSV)
@st.cache_data(ttl=600)
def load_data():
  sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxcG6Zwu5wffcY9sYnrIo6Rukcv5Nw9EbtMU7TyCOR8uW2XGAEThrk-0500Y7ELiVDg_7EeJcitl4/pub?gid=0&single=true&output=csv"
  df = pd.read_csv(sheet_url)
  return df

try:
  df = load_data()

  # ใช้ st.form เพื่อให้มีปุ่มกดค้นหาและกด Enter ได้
  with st.form(key='search_form'):
    search_query = st.text_input(
        "🔍 ค้นหาข้อมูล (พิมพ์คีย์เวิร์ด เช่น ชื่ออุปกรณ์ โค้ดสินค้าหรือหมวดหมู่):"
    )
    submit_button = st.form_submit_button(label="🔍 ค้นหา")

  if submit_button:
    if search_query.strip() != "":
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
        # สร้างตารางสำหรับแสดงผล (ซ่อนคอลัมน์ ลิงก์รูปภาพ ไม่ให้รกตาในตาราง)
        display_df = result_df.copy()
        if "ลิงก์รูปภาพ" in display_df.columns:
          display_df = display_df.drop(columns=["ลิงก์รูปภาพ"])

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ส่วนสำหรับแสดงปุ่มคลิกดูรูปภาพ
        st.markdown("---")
        st.subheader("🖼️ คลิกเพื่อดูรูปภาพของรายการที่พบ")
        for index, row in result_df.iterrows():
          if (
              "ลิงก์รูปภาพ" in row
              and pd.notna(row["ลิงก์รูปภาพ"])
              and str(row["ลิงก์รูปภาพ"]).strip() != ""
          ):
            item_name = (
                str(row["ชื่อสินค้า"])
                if "ชื่อสินค้า" in row and pd.notna(row["ชื่อสินค้า"])
                else f"รายการที่ {index+1}"
            )
            
            # ตรวจสอบรหัสสินค้า ถ้าไม่มีหรือเป็น nan ให้ข้ามการแสดงรหัส
            item_code = (
                str(row["รหัสสินค้า"])
                if "รหัสสินค้า" in row and pd.notna(row["รหัสสินค้า"]) and str(row["รหัสสินค้า"]).strip().lower() != "nan"
                else ""
            )
            
            link_url = str(row["ลิงก์รูปภาพ"]).strip()

            # จัดรูปแบบข้อความปุ่ม: ถ้ามีรหัสให้แสดงรหัสด้วย ถ้าไม่มีให้แสดงแค่ชื่อสินค้า
            if item_code:
              button_label = f"🔗 ดูรูปภาพ: {item_code} - {item_name}"
            else:
              button_label = f"🔗 ดูรูปภาพ: {item_name}"

            st.link_button(button_label, link_url)
      else:
        st.warning("ไม่พบข้อมูลที่ค้นหา")
    else:
      st.warning("กรุณากรอกคำค้นหาก่อนกดปุ่มค้นหา")
  else:
    st.info("กรุณาพิมพ์คำค้นหาแล้วกดปุ่ม 'ค้นหา'")

except Exception as e:
  st.error(
      "ยังไม่ได้ใส่ลิงก์ Google Sheet หรือลิงก์ยังไม่ถูกต้อง กรุณาตรวจสอบลิงก์"
  )
