import pandas as pd
import streamlit as st

st.set_page_config(page_title="PR System Portal", page_icon="🔍", layout="wide")

# --- ส่วนของการใส่รหัสผ่าน (รหัสผ่านคือ PR) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🔒 ระบบเข้าสู่ระบบภายใน</h2>", unsafe_allow_html=True)
    password = st.text_input("กรุณากรอกรหัสผ่านเพื่อเข้าสู่ระบบ:", type="password")
    
    if st.button("เข้าสู่ระบบ", use_container_width=True):
        if password == "PR":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")
    st.stop()

# --- แถบด้านข้าง (Sidebar) สำหรับเลือก 2 ระบบ ---
with st.sidebar:
    st.markdown("### 🏢 เมนูระบบงาน")
    
    # เมนูเลือกหน้า
    app_mode = st.radio(
        "เลือกใช้งานระบบ:",
        [
            "🔍 ค้นหาข้อมูลแคตตาล็อกอุปกรณ์(PR)",
            "📊 ติดตามข้อมูล PR (Purchase Requisition)"
        ]
    )
    
    st.markdown("---")
    if st.button("ออกจากระบบ", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

# --- ฟังก์ชันกลางสำหรับแสดงผลหน้าค้นหา ---
def render_search_page(title, subtitle, sheet_url):
    st.title(title)
    st.write(subtitle)

    @st.cache_data(ttl=600)
    def load_data(url):
        return pd.read_csv(url)

    try:
        df = load_data(sheet_url)

        with st.form(key=f"search_form_{title}"):
            search_query = st.text_input(
                "🔍 ค้นหาข้อมูล (พิมพ์คีย์เวิร์ด เช่น ชื่ออุปกรณ์, รหัส, หรือเลขที่เอกสาร):"
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
                    display_df = result_df.copy()
                    if "ลิงก์รูปภาพ" in display_df.columns:
                        display_df = display_df.drop(columns=["ลิงก์รูปภาพ"])

                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                    # ส่วนแสดงปุ่มรูปภาพเฉพาะถ้ามีคอลัมน์ลิงก์รูปภาพ
                    if "ลิงก์รูปภาพ" in result_df.columns:
                        st.markdown("---")
                        st.subheader("🖼️ คลิกเพื่อดูรูปภาพของรายการที่พบ")
                        for index, row in result_df.iterrows():
                            if (
                                pd.notna(row["ลิงก์รูปภาพ"])
                                and str(row["ลิงก์รูปภาพ"]).strip() != ""
                            ):
                                item_name = (
                                    str(row["ชื่อสินค้า"])
                                    if "ชื่อสินค้า" in row and pd.notna(row["ชื่อสินค้า"])
                                    else f"รายการที่ {index+1}"
                                )
                                
                                item_code = (
                                    str(row["รหัสสินค้า"])
                                    if "รหัสสินค้า" in row and pd.notna(row["รหัสสินค้า"]) and str(row["รหัสสินค้า"]).strip().lower() != "nan"
                                    else ""
                                )
                                
                                link_url = str(row["ลิงก์รูปภาพ"]).strip()

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
            "ไม่สามารถโหลดข้อมูลจาก Google Sheet ได้ กรุณาตรวจสอบลิงก์หรือการตั้งค่าใน Secrets"
        )

# --- สลับหน้าจอตามที่เลือกใน Sidebar (ดึงลิงก์จาก Secrets) ---
if app_mode == "🔍 ค้นหาข้อมูลแคตตาล็อกอุปกรณ์(PR)":
    catalog_url = st.secrets["CATALOG_URL"]
    render_search_page(
        "📚 ระบบค้นหาข้อมูลแคตตาล็อกอุปกรณ์ (PR)",
        "พิมพ์คำค้นหาเพื่อดูข้อมูล PR (ข้อมูลนี้สำหรับค้นหาเท่านั้น)",
        catalog_url
    )

elif app_mode == "📊 ติดตามข้อมูล PR (Purchase Requisition)":
    tracking_url = st.secrets["TRACKING_URL"]
    render_search_page(
        "📈 ระบบติดตามข้อมูล PR (Purchase Requisition)",
        "พิมพ์คำค้นหาเพื่อติดตามสถานะและข้อมูล PR",
        tracking_url
    )
