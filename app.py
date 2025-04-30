import streamlit as st
import os
import asyncio
import shutil
from engine import REQUIRED_FIELDS, normalize_date, run_parser

st.title("Resume Parser")
st.write("Upload one or more resume PDFs (text-based or image-based) to extract key information.")

# Allow multiple file uploads
uploaded_files = st.file_uploader("Choose resume PDFs", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    temp_folder = os.path.abspath("temp_resumes")
    os.makedirs(temp_folder, exist_ok=True)
    
    with st.spinner("Processing resumes..."):
        try:
            # Process each uploaded file
            for idx, uploaded_file in enumerate(uploaded_files):
                st.subheader(f"Resume {idx + 1}: {uploaded_file.name}")
                file_content = uploaded_file.read()
                
                # Process the current PDF
                result = asyncio.run(run_parser(file_content, temp_folder))
                
                # Display extracted information
                st.write("**Extracted Information**")
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
                
                # Display raw JSON
                st.write("**Raw JSON Output**")
                st.json(result)
                st.write("---")  # Separator between resumes
                
        except Exception as e:
            st.error(f"Error processing resumes: {str(e)}")
        finally:
            # Clean up the temp folder after processing all files
            if os.path.exists(temp_folder):
                shutil.rmtree(temp_folder)