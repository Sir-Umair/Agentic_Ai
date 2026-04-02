import os
import io
import json
import requests
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import PyPDF2
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Load Environment Variables initially
load_dotenv()

def configure_gemini():
    """Helper to configure Gemini with the current API Key and select a valid model"""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    
    print(f"\n--- Gemini Diagnostic Check ---")
    if not api_key:
        print("RESULT: GEMINI_API_KEY not found in .env")
        return None, "gemini-1.5-flash"

    api_key = api_key.strip("'\"")
    genai.configure(api_key=api_key)
    
    # Try to find available models to ensure we pick one the user has access to
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"Available models: {models}")
        # Prefer flash, then others
        for m in ["models/gemini-1.5-flash", "models/gemini-1.5-flash-latest", "models/gemini-pro"]:
            if m in models:
                print(f"Selected model: {m}")
                return api_key, m
        if models:
            return api_key, models[0]
    except Exception as e:
        print(f"Error listing models (might be API key issue): {e}")
    
    return api_key, "gemini-1.5-flash"

# Initial configuration
_, ACTIVE_MODEL = configure_gemini()


# -------------------------
# FastAPI App
# -------------------------
app = FastAPI(title="Student Document Processing Agent")

# -------------------------
# Models
# -------------------------
class ExtractionResult(BaseModel):
    name: str
    roll_number: str
    page_count: int
    marks: int
    status: str
    error: Optional[str] = None

# This model tells Gemini exactly what JSON structure to return
class StudentInfo(BaseModel):
    name: str
    roll_number: str

# -------------------------
# Ensure static folder exists
# -------------------------
if not os.path.exists("static"):
    os.makedirs("static")

# -------------------------
# Document Processing API
# -------------------------
@app.post("/process")
async def process_document(file: UploadFile = File(...)):
    global ACTIVE_MODEL
    content = await file.read()
    filename = file.filename.lower()
    
    # Check/Reload API Key
    api_key, detected_model = configure_gemini()
    if api_key:
        ACTIVE_MODEL = detected_model
    else:
        return ExtractionResult(
            name="Error", roll_number="Error", page_count=0, marks=0,
            status="Failed", error="API Key Missing: Please add GEMINI_API_KEY to your .env file."
        )


    # 1. Count Pages
    page_count = 1
    if filename.endswith(".pdf"):
        # ... logic remains same ...

        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            page_count = len(pdf_reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {str(e)}")

    # 2. Calculate Marks
    marks = 1 if page_count <= 3 else 3

    # 3. Extract Name + Roll Number using Structured Output
    try:
        model = genai.GenerativeModel(
            model_name=ACTIVE_MODEL,
            generation_config={"response_mime_type": "application/json"}
        )

        prompt = """
Extract the student's Full Name and Roll Number from this document.
- Be precise.
- Look for labels like "Name", "Student Name", "Roll No", "ID Number".
- If multiple names exist, pick the one that looks like the primary student.
- Return ONLY valid JSON with keys "name" and "roll_number".
- Use "Unknown" if you absolutely cannot find a value.
"""



        
        mime_type = "application/pdf" if filename.endswith(".pdf") else file.content_type

        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": content}
        ])

        # Directly parse JSON without manual string slicing
        extracted_data = json.loads(response.text)
        name = extracted_data.get("name", "Unknown")
        roll_number = extracted_data.get("roll_number", "Unknown")
        extraction_error = None

    except Exception as e:
        error_msg = str(e)
        print(f"Gemini Error: {error_msg}")
        
        # Diagnostic: List models if 404
        if "404" in error_msg:
            print("--- Available Models ---")
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        print(m.name)
            except:
                pass
                
        name, roll_number = "Extraction Error", "Error"
        extraction_error = f"Gemini Error: {error_msg}"


    # 4. Send Data to Google Sheets
    sync_status = "Not Configured"
    apps_script_url = os.getenv("APPS_SCRIPT_URL")
    
    if apps_script_url:
        try:
            payload = {
                "name": name,
                "roll_number": roll_number,
                "page_count": page_count,
                "marks": marks
            }
            resp = requests.post(apps_script_url, json=payload, timeout=10)
            sync_status = "Synced" if resp.status_code == 200 else f"Failed ({resp.status_code})"
        except Exception as e:
            sync_status = f"Sync Error: {str(e)}"

    return ExtractionResult(
        name=name,
        roll_number=roll_number,
        page_count=page_count,
        marks=marks,
        status=sync_status,
        error=extraction_error
    )

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h2>Frontend not found. Please add index.html inside static folder.</h2>"

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Server starting at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)