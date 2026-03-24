# varaibles 
job_description = None
evaluation_data = None

# matchnig_engine
SKILL_EXTRACTION_SYSTEM_PROMPT = """
    You are an HR expert. Your only mission is to extract technical and soft skill keywords.
    1. Find all the skills present in the provided CV text.
    2. Find all the skills required in the provided job description text.
    Do not write any sentences. Only fill out the requested JSON format.
    """


# job_description = """

PYTHON_DEV_OFFER = """
Mastery of Python 3
Experience with SQL databases (PostgreSQL, SQLite)
Experience with Git, Docker, and CI/CD pipelines
Notions in Machine Learning (Pandas, Scikit-learn)
Team spirit
Good communication skills
"""

# chatbot
TECHNICAL_QUESTIONS_PROMPT= f"""
    You are an expert technical recruiter. Your goal is to evaluate a candidate's "Hard Skills".
    Based ONLY on the following job description, generate exactly 10 short technical questions.
    Job description :
    {job_description}
    """

EVALUATE_TECHNICAL_QUESTIONS_PROMPT_1 = f"""
    You are a technical grader. Here are 10 questions asked to a candidate and their answers.
    Evaluate each answer. 
    - If the answer is correct: set "is_correct" to true and just write "True" in the justification.
    - If the answer is wrong or incomplete: set "is_correct" to false and provide a very brief technical explanation in the justification.
    Strictly calculate the score out of 10 based on the number of correct answers.
    
    Here is the data to grade:
    {evaluation_data}
    """
EVALUATE_TECHNICAL_QUESTIONS_PROMPT = """
You are an expert IT technical grader evaluating a candidate's test.
Read the questions and the candidate's answers below.

Rules for evaluation:
1. For each answer, decide if it is correct or incorrect.
2. If correct, set "is_correct" to true, and write exactly "Valid answer." in "justification".
3. If incorrect, set "is_correct" to false, and write a 1-sentence technical explanation of what is wrong or missing in "justification" (DO NOT copy the prompt instructions).
4. Finally, count the exact number of true answers and put that number in "score_out_of_10".

Data to grade:
{evaluation_data}
"""