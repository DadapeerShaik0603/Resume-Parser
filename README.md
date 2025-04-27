Resume Parser Project
Overview
The Resume Parser project is designed to extract structured information from PDF resumes, whether they are text-based or image-based. It provides two interfaces for interaction: a web-based UI using Streamlit for manual uploads and a REST API using FastAPI for programmatic access. The project leverages advanced text extraction, OCR (Optical Character Recognition), and AI-based parsing to convert unstructured resume data into a structured JSON format, including fields such as Full Name, Email Address, Skills, Education, Work Experience, and more.
Approach of the Project
The project follows a modular architecture to process resumes efficiently:

File Handling and Preprocessing:

Resumes are accepted as PDF files through either the Streamlit UI (streamlit_app.py) or the FastAPI endpoint (api.py).
Temporary storage is used to save the uploaded PDF for processing, with cleanup performed afterward.


Text Extraction:

For text-based PDFs, the pymupdf and pymupdf4llm libraries are used to extract text and convert it to Markdown format.
For image-based PDFs or when text extraction fails, the PDF is converted to images (PNG) using pymupdf, and OCR is performed using paddleocr to extract text from these images.


AI-Powered Parsing:

The extracted text is processed by the Google Gemini API (google-generativeai) to parse structured data.
The Gemini model is prompted to extract specific fields (e.g., Full Name, Skills, Education) with confidence scores, normalizing dates and detecting skills intelligently (e.g., identifying "Python" in "Experienced in Python development").
The result is returned as a JSON object with field values and confidence scores.


Dual Interface:

Streamlit UI: A user-friendly interface (streamlit_app.py) allows users to upload a PDF and view the extracted information in a formatted display, along with the raw JSON output.
FastAPI Endpoint: A REST API (api.py) provides a /parse_resume POST endpoint for programmatic access, accepting a PDF file and returning the parsed JSON.


Modular Design:

Shared logic for resume parsing is encapsulated in resume_parser.py, which both streamlit_app.py and api.py import, ensuring code reusability and maintainability.
The project avoids running both Streamlit and FastAPI in the same script to prevent runtime conflicts (e.g., port binding or signal handling issues).



Libraries/Tools Used
The project relies on several Python libraries and tools to achieve its functionality:

pymupdf: For opening and processing PDF files, including text extraction and conversion to images.
pymupdf4llm: Converts PDF content to Markdown format for easier parsing.
paddleocr: Performs OCR on image-based PDFs to extract text from images.
paddlepaddle: Backend for paddleocr, providing the OCR engine.
google-generativeai: Interfaces with the Google Gemini API for AI-powered structured data extraction.
streamlit: Creates the web-based UI for uploading and displaying parsed resume data.
fastapi: Implements the REST API for programmatic access to the resume parsing functionality.
uvicorn: An ASGI server to run the FastAPI application.
aiofiles: For asynchronous file I/O operations, improving performance when handling uploads.
Pillow (PIL): For image processing, particularly when handling PNG conversions.
python-dotenv: Loads environment variables (e.g., Gemini API key) from a .env file.
python-dateutil: Parses and normalizes dates in the extracted data.
asyncio and concurrent.futures: For asynchronous processing to improve performance during text extraction and OCR.
hashlib: Computes file hashes to uniquely identify uploaded files.
json and re: For JSON parsing and regular expression-based text cleaning.

Assumptions and Limitations
Assumptions

PDF Format: The project assumes that resumes are provided in PDF format. Other formats (e.g., Word, images) are not supported.
Gemini API Access: A valid Google Gemini API key is required and must be provided in a .env file as GEMINI_API_KEY.
English Language: The OCR and parsing logic assume that the resume is primarily in English, as paddleocr is configured for English (lang='en').
Internet Connectivity: The Gemini API requires an active internet connection to process the extracted text.
System Resources: The system has sufficient memory and CPU resources to handle PDF-to-image conversion and OCR, which can be resource-intensive.

Limitations

OCR Accuracy: The accuracy of text extraction from image-based PDFs depends on the quality of the PDF and the performance of paddleocr. Poor-quality scans or complex layouts may lead to errors.
Gemini API Dependency: The structured data extraction relies on the Gemini API, which may have rate limits, costs, or availability issues. Additionally, the model's accuracy in parsing fields depends on the clarity and structure of the input text.
Language Support: Currently, the project is optimized for English resumes. Non-English resumes may not be parsed accurately without adjusting the OCR language settings.
Performance: Processing large PDFs or resumes with many pages can be slow due to the need for image conversion and OCR. The ProcessPoolExecutor is used to parallelize some tasks, but performance may still be a bottleneck on low-spec systems.
File System Issues: Running the project in cloud-synced directories (e.g., OneDrive) can cause file-watching issues with Streamlit or Uvicorn's --reload option. It’s recommended to run the project in a local directory to avoid such problems.
Error Handling: While the project includes basic error handling, unexpected PDF formats or corrupted files may still cause crashes. Users should ensure PDFs are well-formed.
Security: The API does not implement authentication or rate limiting, making it potentially vulnerable if exposed publicly. For production use, additional security measures should be added.

Setup Instructions

Clone the Repository:
git clone <repository-url>
cd Resume Parser


Set Up Virtual Environment:
python -m venv resume_parser_env
.\resume_parser_env\Scripts\activate  # On Windows
source resume_parser_env/bin/activate  # On macOS/Linux


Install Dependencies:
pip install -r requirements.txt


Configure Environment:

Create a .env file in the project root and add your Gemini API key:GEMINI_API_KEY=your-api-key-here




Run the Streamlit UI:
streamlit run streamlit_app.py


Open the provided URL (e.g., http://localhost:8501) in your browser to upload a resume.


Run the FastAPI Server:

In a separate terminal, activate the virtual environment and run:uvicorn api:app --reload


Access the API at http://127.0.0.1:8000/docs to test the /parse_resume endpoint.



Usage

Streamlit UI: Upload a PDF resume to view extracted fields and raw JSON output.
FastAPI Endpoint: Send a POST request to /parse_resume with a PDF file to get parsed data in JSON format. Example using cURL:curl -X POST -F "file=@path/to/resume.pdf" http://127.0.0.1:8000/parse_resume



Troubleshooting

Port Conflicts: Ensure no other processes are using ports 8501 (Streamlit) or 8000 (FastAPI). Use netstat -aon | findstr :port to check and taskkill /PID <pid> /F to terminate conflicting processes.
OneDrive Issues: Move the project to a local directory (e.g., C:\Users\peer1\Documents\Guvi_Projects\Resume Parser) to avoid file-watching issues with Streamlit or Uvicorn.
Gemini API Errors: Verify your API key and internet connection. Check for rate limits or quota issues with the Gemini API.

Future Improvements

Add support for additional languages by configuring paddleocr for other languages.
Implement authentication and rate limiting for the FastAPI endpoint.
Optimize performance for large PDFs by caching intermediate results.
Enhance error handling for malformed PDFs or unexpected API responses.

