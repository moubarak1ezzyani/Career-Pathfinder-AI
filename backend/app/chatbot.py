from pydantic import BaseModel
from openai import OpenAI
import json
from app.api.schemas import Question, QuestionList, AnswerEvaluation, InterviewResult
from app.core.config import LLM_MODEL_NAME, OLLAMA_URL
from app.core.prompts import TECHNICAL_QUESTIONS_PROMPT, PYTHON_DEV_OFFER, EVALUATE_TECHNICAL_QUESTIONS_PROMPT


# --- 1. LOCAL AI CONFIGURATION ---
client = OpenAI(
    base_url=OLLAMA_URL,
    api_key="ollama"
)
MODEL_NAME = LLM_MODEL_NAME


# --- 3. MAIN FUNCTIONS ---
def generate_questions(job_description: str) -> QuestionList:
    print("⏳ The AI is analyzing the job description and preparing 10 technical questions (Hard Skills)...")
    prompt = TECHNICAL_QUESTIONS_PROMPT
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format=QuestionList,
    )
    return response.choices[0].message.parsed

def evaluate_candidate(questions: QuestionList, candidate_answers: dict) -> InterviewResult:
    print("\n⏳ The AI is grading your test, please wait...")
    
    evaluation_data = ""
    for q in questions.questions:
        ans = candidate_answers.get(str(q.number), "No answer") # str() par sécurité si les clés JSON sont en string
        evaluation_data += f"Q{q.number}: {q.question_text}\nCandidate's answer: {ans}\n\n"
        
    prompt = EVALUATE_TECHNICAL_QUESTIONS_PROMPT.format(evaluation_data=evaluation_data)
    
    response = client.beta.chat.completions.parse(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        response_format=InterviewResult,
    )
    
    # On récupère le résultat brut de l'IA
    result = response.choices[0].message.parsed
    
    # 🔒 SÉCURITÉ MATHÉMATIQUE (Plan B)
    # On recompte nous-mêmes le nombre exact de réponses "True"
    vrai_score = sum(1 for ans in result.answer_details if ans.is_correct)
    
    # On écrase le mauvais calcul de l'IA par notre calcul parfait
    result.score_out_of_10 = vrai_score
    
    return result

# --- 4. INTERACTIVE SCRIPT (The Chatbot) ---
if __name__ == "__main__":
    
    job_description_text = PYTHON_DEV_OFFER
    
    # Step 1: Create the test
    quiz = generate_questions(job_description_text)
    
    # Step 2: The interview
    print("\n" + "="*50)
    print("🎯 START OF TECHNICAL INTERVIEW (10 Questions)")
    print("="*50 + "\n")
    
    user_answers = {}
    
    for q in quiz.questions:
        print(f"Question {q.number}/10 : {q.question_text}")
        ans = input("👉 Your answer : ")
        user_answers[q.number] = ans
        print("-" * 30)
        
    # Step 3: Grading
    final_result = evaluate_candidate(quiz, user_answers)
    
    # Step 4: Display the final requested JSON
    print("\n" + "="*50)
    print("📊 FINAL RESULT (JSON)")
    print("="*50)
    
    # model_dump() : Pydantic object => dictionary (pretty printing)
    print(json.dumps(final_result.model_dump(), indent=4, ensure_ascii=False))