from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from openai import OpenAI
import pymupdf
from sentence_transformers import SentenceTransformer
import torch
from sentence_transformers import util

app = FastAPI(title="Career Pathfinder AI", version="1.0")

# ==========================================
# 1. AI CONFIGURATION & MODELS
# ==========================================
nlp_model = SentenceTransformer('all-MiniLM-L6-v2')

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" 
)
MODEL_NAME = "qwen2.5:3b"

# ==========================================
# 2. PYDANTIC SCHEMAS (Data Molds)
# ==========================================
# Schema for CV Analysis
class SkillsExtraction(BaseModel):
    found_skills: list[str]
    required_skills: list[str]

# Schemas for Interview Generation
class Question(BaseModel):
    number: int
    question_text: str

class QuestionList(BaseModel):
    questions: list[Question]

class JobDescriptionRequest(BaseModel):
    job_description: str

# Schemas for Interview Evaluation
class AnswerEvaluation(BaseModel):
    number: int
    is_correct: bool
    justification: str

class InterviewResult(BaseModel):
    score_out_of_10: int
    answer_details: list[AnswerEvaluation]

class EvaluateInterviewRequest(BaseModel):
    questions: QuestionList
    candidate_answers: dict[int, str]

# ==========================================
# 3. ROUTES (Endpoints)
# ==========================================

# --- Existing CV Analysis Route ---
@app.post("/analyze")
async def analyze_cv(file: UploadFile = File(...), job_description: str = Form(...)):
    pdf_content = await file.read()
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")
    cv_text = "".join([page.get_text() for page in doc])
    
    prompt_systeme = """
    Tu es un expert en recrutement très strict. Ta seule mission est d'extraire les mots-clés de compétences techniques et soft skills.
    1. Trouve toutes les compétences présentes dans le texte du CV fourni.
    2. Trouve toutes les compétences exigées dans le texte de l'offre d'emploi fournie.
    Ne rédige aucune phrase. Remplis uniquement le format JSON demandé.
    """
    prompt_utilisateur = f"--- TEXTE DU CV ---\n{cv_text}\n\n--- TEXTE DE L'OFFRE ---\n{job_description}"

    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt_systeme},
            {"role": "user", "content": prompt_utilisateur}
        ],
        response_format=SkillsExtraction,
    )

    extracted_data = response.choices[0].message.parsed
    cv_skills = extracted_data.found_skills
    job_skills = extracted_data.required_skills

    if not job_skills or not cv_skills:
        return {"status": "error", "message": "Impossible d'extraire les compétences."}

    cv_embeddings = nlp_model.encode(cv_skills, convert_to_tensor=True)
    job_embeddings = nlp_model.encode(job_skills, convert_to_tensor=True)

    total_score = 0
    missing_skills = []
    cosine_scores = util.cos_sim(job_embeddings, cv_embeddings)

    for i, job_skill in enumerate(job_skills):
        best_match_score = torch.max(cosine_scores[i]).item()
        total_score += best_match_score
        if best_match_score < 0.4:
            missing_skills.append(job_skill)

    final_match_score = (total_score / len(job_skills)) * 100

    return {
        "status": "success",
        "match_score": round(final_match_score, 2),
        "data": {
            "cv_skills_found": cv_skills,
            "job_skills_required": job_skills,
            "missing_skills": missing_skills
        }
    }


# --- Generate Interview Questions Route ---
@app.post("/generate-quiz", response_model=QuestionList)
async def generate_quiz(job_description: str = Form(...)): # Changed from request: JobDescriptionRequest to Form(...)
    
    prompt = f"""
    You are an expert technical recruiter. Your goal is to evaluate a candidate's "Hard Skills".
    Based ONLY on the following job description, generate exactly 10 short technical questions.
    Job description :
    {job_description}
    """
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format=QuestionList,
    )
    return response.choices[0].message.parsed


# --- Evaluate Interview Route ---
@app.post("/evaluate-interview", response_model=InterviewResult)
async def evaluate_interview(request: EvaluateInterviewRequest):
    evaluation_data = ""
    for q in request.questions.questions:
        ans = request.candidate_answers.get(q.number, "No answer")
        evaluation_data += f"Q{q.number}: {q.question_text}\nCandidate's answer: {ans}\n\n"
        
    prompt = f"""
    You are a technical grader. Here are 10 questions asked to a candidate and their answers.
    Evaluate each answer. 
    - If the answer is correct: set "is_correct" to true and just write "True" in the justification.
    - If the answer is wrong or incomplete: set "is_correct" to false and provide a very brief technical explanation in the justification.
    Strictly calculate the score out of 10 based on the number of correct answers.
    
    Here is the data to grade:
    {evaluation_data}
    """
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format=InterviewResult,
    )
    return response.choices[0].message.parsed