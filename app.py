import streamlit as st
from google import genai
from google.genai import types
import json
import pandas as pd

# ตั้งค่าหน้าตาเว็บ
st.set_page_config(page_title="ECOCIERGE - AI Carbon Concierge", layout="wide")

st.title("ECOCIERGE: AI Carbon Footprint Concierge for SMEs")
st.caption("เพื่อการขับเคลื่อน SME สู่ธุรกิจคาร์บอนต่ำและ ESG ที่ทำได้จริง")

# ช่องใส่ Gemini API Key
api_key = st.text_input("กรอก API Key ของคุณ:", type="password")

# ฐานข้อมูล Emission Factor ของ อบก. (TGO)
EMISSION_FACTORS = {
    "electricity": {"factor": 0.4999, "unit": "kWh", "scope": "Scope 2", "name": "ค่าไฟฟ้า"},
    "diesel": {"factor": 2.7081, "unit": "Litre", "scope": "Scope 1", "name": "น้ำมันดีเซล"},
    "gasoline": {"factor": 2.1896, "unit": "Litre", "scope": "Scope 1", "name": "น้ำมันเบนซิน"}
}

# ส่วนอัปโหลดเอกสาร
uploaded_file = st.file_uploader("อัปโหลดใบเสร็จค่าไฟ หรือสลิปน้ำมัน (รูปภาพ JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file and api_key:
    st.image(uploaded_file, caption="เอกสารที่อัปโหลด", width=400)
    
    if st.button("ให้ AI สกัดข้อมูลและคำนวณคาร์บอน"):
        with st.spinner("AI กำลังอ่านข้อมูลจากเอกสาร..."):
            try:
                client = genai.Client(api_key=api_key)
                
                # Prompt สั่งให้ AI อ่านภาพและแปลงเป็น JSON
                prompt = """
                คุณคือ AI ผู้เชี่ยวชาญด้าน Carbon Accounting สำหรับ SME
                จงอ่านรูปภาพบิลหรือใบเสร็จนี้ แล้วสกัดข้อมูลออกมาเป็น JSON รูปแบบนี้เท่านั้น ห้ามมีข้อความอื่น:
                {
                    "item_type": "electricity" หรือ "diesel" หรือ "gasoline" หรือ "unknown",
                    "amount": ตัวเลขปริมาณการใช้งาน เช่น 150.5 (ถ้าไม่มีให้ใส่ 0),
                    "unit": "kWh" หรือ "Litre" หรือ "unknown"
                }
                """
                
                bytes_data = uploaded_file.getvalue()
                
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[
                        types.Part.from_bytes(data=bytes_data, mime_type=uploaded_file.type),
                        prompt
                    ]
                )
                
                cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(cleaned_text)
                
                item_type = data.get("item_type", "unknown")
                amount = float(data.get("amount", 0))
                
                if item_type in EMISSION_FACTORS:
                    ef_info = EMISSION_FACTORS[item_type]
                    carbon_footprint = amount * ef_info["factor"]
                    
                    st.success("AI สกัดข้อมูลและคำนวณสำเร็จ!")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("ประเภทกิจกรรม", ef_info["name"])
                    col2.metric("ปริมาณที่ใช้", f"{amount} {ef_info['unit']}")
                    col3.metric("ปริมาณคาร์บอน", f"{carbon_footprint:.2f} kgCO2e", delta=ef_info["scope"])
                    
                    df = pd.DataFrame([{
                        "ประเภทรายการ": ef_info["name"],
                        "ปริมาณที่ใช้": f"{amount} {ef_info['unit']}",
                        "Emission Factor (TGO)": ef_info["factor"],
                        "Scope": ef_info["scope"],
                        "Carbon Footprint (kgCO2e)": round(carbon_footprint, 2)
                    }])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("AI ไม่สามารถระบุประเภทบิลนี้ได้ กรุณาลองอัปโหลดภาพบิลค่าไฟหรือสลิปน้ำมันที่ชัดเจนขึ้น")
                    
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
