# Resume Parser

A dual-mode application that can parse resumes using either a Streamlit interface or a FastAPI backend. The application uses both a custom parser and the Gemini API for enhanced information extraction.

## Features

- Extracts personal information (name, email, phone, LinkedIn)
- Identifies skills
- Extracts education details
- Extracts work experience
- Handles both text-based and image-based PDFs using PaddleOCR
- Provides confidence scores for each extracted field
- Normalizes date formats
- Intelligent skill detection
- Dual interface options (Streamlit UI or FastAPI)
- Gemini API integration for enhanced parsing

## Prerequisites

Before setting up the project, you'll need:
1. Python 3.7 or higher
2. A Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Step-by-Step Setup and Running Instructions

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd resume-parser
```

### Step 2: Set Up the Environment

#### Windows
1. Run the setup script:
```bash
setup_venv.bat
```

#### Linux/Mac
1. Make the setup script executable:
```bash
chmod +x setup_venv.sh
```

2. Run the setup script:
```bash
./setup_venv.sh
```

### Step 3: Configure the Gemini API Key

1. Open the `.env` file in a text editor
2. Replace `your_gemini_api_key_here` with your actual Gemini API key
3. Save the file

Example `.env` file:
```
# Gemini API Configuration
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Application Configuration
TEMP_FILES_DIR=./temp_files
```

### Step 4: Run the Application

You can run the application in either Streamlit mode (for UI) or FastAPI mode (for API access).

#### Option 1: Streamlit Mode (UI)
1. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to http://localhost:8501
4. Upload a resume PDF file
5. View the extracted information with confidence scores

#### Option 2: FastAPI Mode (API)
1. Activate the virtual environment (if not already activated):
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. Run the FastAPI server:
```bash
python api.py
```

3. The API will be available at http://localhost:8000
4. Use the following endpoints:
   - POST `/parse-resume`: Upload and parse a resume PDF
   - GET `/health`: Check the API health status

5. Example API usage:
```bash
curl -X POST "http://localhost:8000/parse-resume" -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@resume.pdf"
```

### Step 5: Deactivate the Virtual Environment (When Done)

When you're finished working with the project:
```bash
deactivate
```

## Troubleshooting

### PyMuPDF Installation Issues (Windows)

If you encounter errors while installing PyMuPDF, follow these steps:

1. Install Visual Studio Build Tools:
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Select "Desktop development with C++"
   - Include Windows 10 SDK
   - Complete the installation

2. Try installing PyMuPDF using a pre-built wheel:
```bash
pip install --only-binary :all: PyMuPDF
```

3. If the above doesn't work, try installing a specific version:
```bash
pip install PyMuPDF==1.23.8
```

### Other Common Issues

1. If you encounter any issues with the setup scripts:
   - Make sure Python 3.7+ is installed
   - Check if you have write permissions in the project directory
   - Verify your Gemini API key is correct

2. If the application fails to start:
   - Ensure the virtual environment is activated
   - Check if all dependencies are installed correctly
   - Verify the `.env` file exists and contains the correct API key

3. If you get API-related errors:
   - Verify your Gemini API key is valid
   - Check your internet connection
   - Ensure you're not exceeding API rate limits

## Requirements

- Python 3.7+
- See requirements.txt for Python package dependencies
- PaddleOCR for image-based PDF support
- Gemini API key for enhanced parsing

## Notes

- The parser works best with well-formatted resumes
- Confidence scores range from 0 to 1, with 1 being the most confident
- Missing fields will be marked as "Not found"
- The app supports both text-based and image-based PDFs
- Gemini API provides enhanced parsing capabilities
- Results are returned in JSON format when using the API 