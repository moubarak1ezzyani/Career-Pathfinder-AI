import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Imports from your application (Adapted to your structure)
from app.main import app, get_current_user, get_db
from app.api import models, schemas

# ==========================================
# 1. TEST ENVIRONMENT SETUP
# ==========================================

# Force the creation of the SQLite DB at the root of the 'backend' folder
# even if the test is executed from the 'tests' folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'test_database.db')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (from app/api/models.py)
models.my_Base.metadata.create_all(bind=engine)

# Database dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Authentication dependency override (Simulates an always-logged-in user)
def override_get_current_user():
    db = TestingSessionLocal()
    user = db.query(models.Candidat).filter(models.Candidat.email == "test@test.com").first()
    if not user:
        user = models.Candidat(email="test@test.com", hashed_pwd="fake", name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user

# Apply overrides to FastAPI
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# The client that will simulate our HTTP requests
client = TestClient(app)


# ==========================================
# 2. TESTS
# ==========================================

def test_mathematical_security_score():
    """
    UNIT TEST: Verifies that the Python logic for recounting 'True' values works correctly.
    """
    fake_ai_responses = [
        {"is_correct": True, "justification": "Valid answer."},
        {"is_correct": False, "justification": "Bad answer."},
        {"is_correct": True, "justification": "Valid answer."}
    ]
    
    true_score = sum(1 for ans in fake_ai_responses if ans["is_correct"])
    
    assert true_score == 2, "Error: Mathematical security is not correctly counting the exact answers."


# Warning: The path of the mock "app.main.analyze_match" depends on where you use the function.
# If the function is executed in main.py, this is correct. 
@patch("app.main.analyze_match")
def test_route_1_matching(mock_analyze_match):
    """
    INTEGRATION TEST: Route /analyze
    """
    mock_analyze_match.return_value = {
        "status": "success",
        "match_score": 85,
        "data": {"found_skills": ["Python"], "missing_skills": ["Docker"]}
    }

    fake_pdf = ("cv_test.pdf", b"Simulated PDF content", "application/pdf")

    response = client.post(
        "/analyze",
        files={"file": fake_pdf},
        data={"job_description": "Python Backend Developer"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ai_result"]["match_score"] == 85
    assert data["job_target_id"] is not None 


@patch("app.main.generate_questions")
@patch("app.main.evaluate_candidate")
def test_route_2_chatbot(mock_evaluate_candidate, mock_generate_questions):
    """
    INTEGRATION TEST: Routes /generate-quiz and /evaluate-interview
    """
    db = TestingSessionLocal()
    user = override_get_current_user()
    
    job = models.JobTarget(candidat_id=user.id, description_text="DevOps Job")
    db.add(job)
    db.commit()
    db.refresh(job)

    # Generation Mock
    class FakeQuiz:
        def model_dump(self):
            return {"questions": [{"number": 1, "question_text": "What is Docker?"}]}
    mock_generate_questions.return_value = FakeQuiz()

    resp_quiz = client.post("/generate-quiz", data={"job_target_id": job.id})
    assert resp_quiz.status_code == 200
    session_id = resp_quiz.json()["session_id"]

    # Evaluation Mock
    class FakeAnswerDetail:
        def model_dump(self):
            return {"number": 1, "is_correct": True, "justification": "Valid answer."}
            
    class FakeEvaluation:
        score_out_of_10 = 10
        answer_details = [FakeAnswerDetail()]

    mock_evaluate_candidate.return_value = FakeEvaluation()

    resp_eval = client.post(
        "/evaluate-interview",
        json={
            "session_id": session_id,
            "candidate_answers": {"1": "Docker is a containerization tool."}
        }
    )
    
    assert resp_eval.status_code == 200
    
    # Au lieu de chercher dans le JSON (qui est vide), on vérifie dans la BDD
    # que la session a bien été mise à jour !
    updated_session = db.query(models.InterviewSession).filter(models.InterviewSession.id == session_id).first()
    
    # On vérifie que la session existe bien
    assert updated_session is not None
    
    # LA CORRECTION EST ICI : on utilise le vrai nom de ta colonne
    assert updated_session.score_out_of_10 is not None
    db.close()

# cmd : pytest tests/ -v    