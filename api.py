import os
import json
import asyncio
import re
import shutil
import hashlib
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import aiofiles
import pymupdf
import pymupdf4llm
from paddleocr import PaddleOCR
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
from dateutil.parser import parse
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Failed to configure Gemini API: {str(e)}")

# Model configuration for Gemini
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 90000,
    "response_mime_type": "text/plain",
}

# Initialize PaddleOCR
OCR_CLIENT = None
try:
    OCR_CLIENT = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
except Exception as e:
    print(f"Failed to initialize PaddleOCR: {str(e)}")

# Define required fields
REQUIRED_FIELDS = [
    "Full Name", "Email Address", "Phone Number", "LinkedIn Profile URL",
    "Skills", "Education", "Work Experience", "Certifications", "Projects"
]

# Utility functions
def compute_file_hash(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()

def normalize_date(date_str: str) -> str:
    try:
        parsed_date = parse(date_str, fuzzy=True)
        return parsed_date.strftime("%b %Y")
    except Exception:
        return date_str

def is_meaningful_text(text: str) -> bool:
    if not text or text.isspace():
        return False
    cleaned_text = re.sub(r'[-=]{3,}', '', text).strip()
    if not cleaned_text or len(cleaned_text) < 10:
        return False
    return True

# PDF and Image processing functions
def convert_to_png_sync(file_path: str, file_hash: str, temp_folder: str) -> List[str]:
    image_paths = []
    try:
        doc = pymupdf.open(file_path)
        for page_num in range(len(doc)):
            image_path = os.path.join(temp_folder, f"resume_page_{page_num}_{file_hash}.png")
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=300)
            pix.save(image_path)
            image_paths.append(image_path)
        doc.close()
        return image_paths
    except Exception as e:
        print(f"Error converting PDF to PNG: {str(e)}")
        return []

async def convert_to_png(file_path: str, file_hash: str, temp_folder: str) -> List[str]:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        return await loop.run_in_executor(executor, convert_to_png_sync, file_path, file_hash, temp_folder)

def extract_text_from_image_sync(image_path: str, file_hash: str) -> str:
    if OCR_CLIENT is None:
        return "PaddleOCR failed to initialize."
    try:
        result = OCR_CLIENT.ocr(image_path, cls=True)
        if result and len(result[0]):
            text = '\n'.join([line[1][0] for line in result[0]])
            return text
        return "No text detected in the image."
    except Exception as e:
        return f"Error processing image with PaddleOCR: {str(e)}"

async def extract_text_from_image(image_path: str, file_hash: str) -> str:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        return await loop.run_in_executor(executor, extract_text_from_image_sync, image_path, file_hash)

async def extract_text_from_images(image_paths: List[str], file_hash: str) -> str:
    full_text = ""
    for image_path in image_paths:
        text = await extract_text_from_image(image_path, file_hash)
        full_text += text + "\n"
        if os.path.exists(image_path):
            os.remove(image_path)
    return full_text

def extract_markdown_from_pdf_sync(pdf_path: str, file_hash: str, temp_folder: str) -> str:
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path).strip()
        if not is_meaningful_text(md_text):
            image_paths = convert_to_png_sync(pdf_path, file_hash, temp_folder)
            if image_paths:
                md_text = asyncio.run(extract_text_from_images(image_paths, file_hash))
        return md_text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

async def extract_markdown_from_pdf(pdf_path: str, file_hash: str, temp_folder: str) -> str:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        return await loop.run_in_executor(executor, extract_markdown_from_pdf_sync, pdf_path, file_hash, temp_folder)

# Gemini processing
def process_with_gemini_sync(md_text: str, file_hash: str) -> Dict[str, Any]:
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-01-21", generation_config=generation_config)
        prompt = f"""You're an expert in extracting structured data from resume text. Parse the provided text and extract the following fields with a confidence score (0-1) for each:

        1. Full Name
        2. Email Address
        3. Phone Number
        4. LinkedIn Profile URL (if available)
        5. Skills (List, detect skills like 'Python' even in sentences)
        6. Education (List of objects with Degree, Institution, Year)
        7. Work Experience (List of objects with Company Name, Job Title, Duration (Start - End), Brief Description)
        8. Certifications (List, if any)
        9. Projects (List, if any)

        Guidelines:
        - Assign a confidence score (0-1) based on clarity and certainty of extraction.
        - If a field is missing, return null with a confidence score of 0.
        - Normalize dates to 'MMM YYYY' format (e.g., Jan 2020).
        - Extract skills intelligently, e.g., detect 'Python' in 'Experienced in Python development'.
        - Return the result in JSON format, with each field containing 'value' and 'confidence'.

        Input:
        {md_text}

        Output (in JSON format):
        """
        response = model.generate_content(prompt)
        json_text = response.text.strip()
        if json_text.startswith("```json") and json_text.endswith("```"):
            json_text = json_text[len("```json"): -len("```")].strip()
        try:
            structured_data = json.loads(json_text)
            return structured_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse Gemini JSON response: {str(e)}")
            return {field: {"value": None, "confidence": 0} for field in REQUIRED_FIELDS}
    except Exception as e:
        print(f"Error processing with Gemini: {str(e)}")
        return {field: {"value": None, "confidence": 0} for field in REQUIRED_FIELDS}

async def process_with_gemini(md_text: str, file_hash: str) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        return await loop.run_in_executor(executor, process_with_gemini_sync, md_text, file_hash)

# Main processing function
async def process_resume(file_content: bytes, temp_folder: str) -> Dict[str, Any]:
    file_hash = compute_file_hash(file_content)
    temp_path = os.path.join(temp_folder, f"{file_hash}.pdf")
    
    os.makedirs(temp_folder, exist_ok=True)
    async with aiofiles.open(temp_path, "wb") as f:
        await f.write(file_content)
    
    md_text = await extract_markdown_from_pdf(temp_path, file_hash, temp_folder)
    if not is_meaningful_text(md_text):
        print("No meaningful text extracted from the resume.")
        return {field: {"value": None, "confidence": 0} for field in REQUIRED_FIELDS}
    
    structured_data = await process_with_gemini(md_text, file_hash)
    
    # Clean up
    if os.path.exists(temp_path):
        os.remove(temp_path)
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    
    return structured_data

# FastAPI App
app = FastAPI(title="AI Resume Parser API")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Resume Parser API",
        "documentation": "Visit /docs for API documentation and to test the /parse_resume endpoint",
        "endpoint": "POST /parse_resume to upload one or more PDF resumes and get parsed data"
    }

@app.post("/parse_resume")
async def parse_resume(files: List[UploadFile]):
    # Validate that all files are PDFs
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF. Only PDF files are supported.")
    
    results = []
    temp_folder = os.path.abspath("temp_resumes")
    
    try:
        for file in files:
            file_content = await file.read()
            result = await process_resume(file_content, temp_folder)
            results.append({
                "filename": file.filename,
                "parsed_data": result
            })
        return JSONResponse(content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resumes: {str(e)}")