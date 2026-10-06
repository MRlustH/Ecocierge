import streamlit as st
import json
import pandas as pd

# ตั้งค่าหน้าตาเว็บ
st.set_page_config(page_title="ECOCIERGE - AI Carbon Concierge", page_icon="🌱", layout="wide")

st.title("🌱 ECOCIERGE: AI Carbon Footprint Calculator for SMEs")
st.caption("ระบบผู้ช่วยอัจฉริยะประเมิน Carbon Footprint อัตโนมัติสำหรับ SME ไทย")

# ฐานข้อมูล Emission Factor ล่าสุดของ อบก. (TGO)
EMISSION_FACTORS = {
    "บิลค่าไฟฟ้า (Electricity)": {"factor": 0.4999, "unit": "kWh", "scope": "Scope 2"},
    "สลิปน้ำมันดีเซล (Diesel)": {"factor": 2.7081, "unit": "Litre", "scope": "Scope 1"},
    "สลิปน้ำมันเบนซิน (Gasoline)": {"factor": 2.1896, "unit": "Litre", "scope": "Scope 1"}
}

# ส่วนรับข้อมูลในแอป
st.subheader("1. เลือกประเภทเอกสารและระบุปริมาณการใช้งาน")
selected_type = st.selectbox("เลือกประเภทเอกสาร/กิจกรรม:", list(EMISSION_FACTORS.keys()))
amount = st.number_input("ระบุปริมาณที่ใช้ (หน่วยตามประเภทเอกสาร):", min_value=0.0, value=100.0)

if st.button("🚀 คำนวณ Carbon Footprint"):
    ef_info = EMISSION_FACTORS[selected_type]
    carbon_footprint = amount * ef_info["factor"]
    
    st.success("✅ คำนวณผลลัพธ์สำเร็จ!")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("ประเภทกิจกรรม", selected_type.split(" ")[0])
    col2.metric("ปริมาณที่ใช้", f"{amount} {ef_info['unit']}")
    col3.metric("ปริมาณคาร์บอน", f"{carbon_footprint:.2f} kgCO2e", delta=ef_info["scope"])
    
    # แสดงตารางสรุป
    df = pd.DataFrame([{
        "ประเภทรายการ": selected_type,
        "ปริมาณที่ใช้": f"{amount} {ef_info['unit']}",
        "Emission Factor (TGO)": ef_info["factor"],
        "Scope": ef_info["scope"],
        "Carbon Footprint (kgCO2e)": round(carbon_footprint, 2)
    }])
    st.dataframe(df, use_container_width=True)
