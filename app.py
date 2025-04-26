import streamlit as st
import os
import asyncio
import shutil
from engine import REQUIRED_FIELDS, normalize_date, run_parser

st.title("Resume Parser")
st.write("Upload a resume PDF (text-based or image-based) to extract key information.")

uploaded_file = st.file_uploader("Choose a resume PDF", type=["pdf"])

if uploaded_file:
    temp_folder = os.path.abspath("temp_resumes")
    os.makedirs(temp_folder, exist_ok=True)
    
    with st.spinner("Processing resume..."):
        try:
            file_content = uploaded_file.read()
            result = asyncio.run(run_parser(file_content, temp_folder))
            
            st.subheader("Extracted Information")
            for field in REQUIRED_FIELDS:
                data = result.get(field, {"value": None, "confidence": 0})
                value = data["value"]
                confidence = data["confidence"]
                
                st.write(f"**{field}** (Confidence: {confidence:.2f})")
                if value is None:
                    st.write("Not found")
                    st.write(f"Log: {field} missing from resume.")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                if k in ["Year", "Duration"] and v:
                                    v = normalize_date(v) if isinstance(v, str) else v
                                st.write(f"- {k}: {v}")
                        else:
                            st.write(f"- {item}")
                else:
                    st.write(value)
                st.write("")
            
            st.subheader("Raw JSON Output")
            st.json(result)
            
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
        finally:
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)