import os
import pymupdf  
from pydantic import BaseModel
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
import torch
import json
from app.api.schemas import SkillsExtraction
from app.core.prompts import SKILL_EXTRACTION_SYSTEM_PROMPT, PYTHON_DEV_OFFER
from app.core.config import cv_me_standard, OLLAMA_URL

# ==============================================================================
# 🧠 1. MODEL INITIALIZATION 
# ==============================================================================
print("⏳ Loading NLP model 'all-MiniLM-L6-v2' into memory...")
nlp_model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to local Ollama instance
client = OpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama" 
)

print("✅ Models ready.")

# ==============================================================================
# 🛠️ 2. PDF TO TEXT EXTRACTION 
# ==============================================================================
def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file was not found: {file_path}")
    
    doc = pymupdf.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    
    return full_text

# ==============================================================================
# 🎯 3. MAIN MATCHING FUNCTION
# ==============================================================================
def analyze_match(cv_file_path: str, job_description: str) -> dict:
    """
    Reads a local PDF CV, extracts skills via LLM, and calculates the match score.
    """
    # --- STEP 0: READ LOCAL FILE ---
    print(f"📄 Reading file: {cv_file_path}...")
    try:
        cv_text = extract_text_from_pdf(cv_file_path)
    except Exception as e:
        return {"status": "error", "message": f"Error reading PDF: {str(e)}"}

    if not cv_text.strip():
        return {"status": "error", "message": "The PDF seems to be empty or unreadable (e.g., scanned image)."}

    # --- STEP 1: SMART EXTRACTION (Qwen) ---
    print("🤖 Extracting skills with Qwen...")
    system_prompt = SKILL_EXTRACTION_SYSTEM_PROMPT
    
    user_prompt = f"--- CV TEXT ---\n{cv_text}\n\n--- JOB DESCRIPTION ---\n{job_description}"
    
    try:
        response = client.beta.chat.completions.parse(
            model="qwen2.5:3b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=SkillsExtraction, 
        )
        extracted_data = response.choices[0].message.parsed
        cv_skills = extracted_data.found_skills
        job_skills = extracted_data.required_skills
    except Exception as e:
        return {"status": "error", "message": f"Error with Qwen LLM: {str(e)}"}

    if not job_skills or not cv_skills:
        return {"status": "error", "message": "Failed to extract skills from the texts."}

    # --- STEP 2: MATH AND VECTOR SCORING ---
    print("🧮 Calculating matching score...")
    cv_embeddings = nlp_model.encode(cv_skills, convert_to_tensor=True)
    job_embeddings = nlp_model.encode(job_skills, convert_to_tensor=True)
    
    total_score = 0
    missing_skills = []
    
    cosine_scores = util.cos_sim(job_embeddings, cv_embeddings)
    
    for i, job_skill in enumerate(job_skills):
        best_match_score = torch.max(cosine_scores[i]).item()
        total_score += best_match_score
        
        # If similarity is < 60%, consider the skill missing
        if best_match_score < 0.6:
            missing_skills.append(job_skill)
    
    final_match_score = round((total_score / len(job_skills)) * 100, 2)
    
    # --- STEP 3: RESULT FORMATTING ---
    return {
        "status": "success",
        "match_score": final_match_score,
        "data": {
            "cv_skills_found": cv_skills,
            "job_skills_required": job_skills,
            "missing_skills": missing_skills
        }
    }

# ==============================================================================
# 🧪 4. TEST BLOCK
# ==============================================================================
if __name__ == "__main__":
    print("\n🚀 Launching local test...")
    
    # Replace with the real path to a CV on your PC!
    TEST_CV_PATH = cv_me_standard 
    
    TEST_JOB_DESC = PYTHON_DEV_OFFER
    
    # Test security: check that the path has been correctly modified
    if os.path.exists(TEST_CV_PATH):
        resultat = analyze_match(TEST_CV_PATH, TEST_JOB_DESC)
        print("\n📊 MATCHING RESULT:")
        print(json.dumps(resultat, indent=4, ensure_ascii=False))
    else:
        print(f"\n⚠️ ERROR: You must first modify the TEST_CV_PATH variable (line {__import__('inspect').currentframe().f_lineno - 13}) to point to a real PDF file on your computer.")