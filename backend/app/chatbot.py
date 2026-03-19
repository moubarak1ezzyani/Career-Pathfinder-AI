from pydantic import BaseModel
from openai import OpenAI
import json

# --- 1. LOCAL AI CONFIGURATION ---
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)
MODEL_NAME = "qwen2.5:3b"

# --- 2. JSON SCHEMAS (Pydantic) ---
# For generating questions
class Question(BaseModel):
    number: int
    question_text: str

class QuestionList(BaseModel):
    questions: list[Question]

# For the final evaluation
class AnswerEvaluation(BaseModel):
    number: int
    is_correct: bool
    justification: str

class InterviewResult(BaseModel):
    score_out_of_10: int
    answer_details: list[AnswerEvaluation]

# --- 3. MAIN FUNCTIONS ---
def generate_questions(job_description: str) -> QuestionList:
    print("⏳ The AI is analyzing the job description and preparing 10 technical questions (Hard Skills)...")
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

def evaluate_candidate(questions: QuestionList, candidate_answers: dict) -> InterviewResult:
    print("\n⏳ The AI is grading your test, please wait...")
    
    # Prepare the text containing the questions and the candidate's answers
    evaluation_data = ""
    for q in questions.questions:
        ans = candidate_answers.get(q.number, "No answer")
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

# --- 4. INTERACTIVE SCRIPT (The Chatbot) ---
if __name__ == "__main__":
    
    job_description_text = """
Mastery of Python 3
Experience with SQL databases (PostgreSQL, SQLite)
Experience with Git, Docker, and CI/CD pipelines
Notions in Machine Learning (Pandas, Scikit-learn)
Team spirit
Good communication skills
"""
    
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
    
    # model_dump() converts the Pydantic object into a dictionary for pretty printing
    print(json.dumps(final_result.model_dump(), indent=4, ensure_ascii=False))