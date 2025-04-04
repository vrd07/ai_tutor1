import os
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models.database import (
    Flashcard,
    InteractiveElement,
    Progress,
    QuestionPaper,
    StudyPlan,
    User,
    get_db,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.ollama_client import OllamaClient

app = FastAPI(title="AI Personal Tutor")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class UserProfile(BaseModel):
    name: str
    email: str
    subjects: dict
    preferences: Optional[dict] = None
    learning_goals: Optional[dict] = None
    study_preferences: Optional[dict] = None


class LessonRequest(BaseModel):
    subject: str
    topic: str
    level: str
    preferences: Optional[dict] = None


class QuizRequest(BaseModel):
    subject: str
    topic: str
    level: str
    num_questions: int = 5
    question_types: List[str] = ["multiple_choice"]


class StudyPlanRequest(BaseModel):
    user_id: int
    goals: dict
    duration: int  # in days


class ProgressUpdate(BaseModel):
    user_id: int
    subject: str
    topic: str
    score: float
    time_spent: int
    difficulty_level: str
    learning_style: Optional[str] = None
    confidence_level: Optional[float] = None
    notes: Optional[str] = None
    feedback: Optional[dict] = None


class QuizResponse(BaseModel):
    questions: List[dict]
    answers: List[str]


class FlashcardRequest(BaseModel):
    user_id: int
    subject: str
    topic: str
    num_cards: int = 10


class InteractiveElementRequest(BaseModel):
    user_id: int
    subject: str
    topic: str
    element_type: str


# Initialize Ollama client
ollama_client = OllamaClient()

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)


# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to AI Personal Tutor"}


@app.post("/api/profile")
async def create_profile(profile: UserProfile, db: Session = Depends(get_db)):
    db_user = User(
        name=profile.name,
        email=profile.email,
        subjects=profile.subjects,
        preferences=profile.preferences,
        learning_goals=profile.learning_goals,
        study_preferences=profile.study_preferences,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Profile created successfully", "user_id": db_user.id}


@app.get("/api/profile/{user_id}")
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/lesson")
async def generate_lesson(request: LessonRequest):
    try:
        response = await ollama_client.generate_lesson(
            request.subject, request.topic, request.level, request.preferences
        )
        return {"content": response["response"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz")
async def generate_quiz(request: QuizRequest):
    try:
        response = await ollama_client.generate_quiz(
            request.subject,
            request.topic,
            request.level,
            request.num_questions,
            request.question_types,
        )
        return {"content": response["response"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/study-plan")
async def create_study_plan(request: StudyPlanRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        response = await ollama_client.generate_study_plan(user.dict(), request.goals)

        study_plan = StudyPlan(
            user_id=request.user_id,
            plan=response["response"],
            duration=request.duration,
            status="Active",
            progress=0.0,
        )
        db.add(study_plan)
        db.commit()
        db.refresh(study_plan)

        return {"message": "Study plan created successfully", "plan_id": study_plan.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/progress")
async def update_progress(progress: ProgressUpdate, db: Session = Depends(get_db)):
    try:
        db_progress = Progress(
            user_id=progress.user_id,
            subject=progress.subject,
            topic=progress.topic,
            score=progress.score,
            time_spent=progress.time_spent,
            difficulty_level=progress.difficulty_level,
            feedback=progress.feedback,
        )
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)

        # Get learning recommendations
        recommendations = await ollama_client.get_learning_recommendations(
            progress.dict()
        )

        return {
            "message": "Progress updated successfully",
            "recommendations": recommendations["response"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-paper")
async def upload_question_paper(
    file: UploadFile = File(...),
    subject: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        # Save the file
        file_path = f"uploads/{user_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Analyze the paper
        with open(file_path, "r") as f:
            content = f.read()

        analysis = await ollama_client.analyze_question_paper(content, subject)

        # Save to database
        paper = QuestionPaper(
            user_id=user_id,
            subject=subject,
            file_path=file_path,
            analysis=analysis["response"],
            paper_metadata={
                "filename": file.filename,
                "upload_date": datetime.utcnow().isoformat(),
            },
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)

        return {
            "message": "Paper uploaded and analyzed successfully",
            "analysis": analysis["response"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/progress/{user_id}")
async def get_progress(user_id: int, db: Session = Depends(get_db)):
    progress = db.query(Progress).filter(Progress.user_id == user_id).all()
    return progress


@app.get("/api/study-plans/{user_id}")
async def get_study_plans(user_id: int, db: Session = Depends(get_db)):
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == user_id).all()
    return plans


@app.get("/api/question-papers/{user_id}")
async def get_question_papers(user_id: int, db: Session = Depends(get_db)):
    papers = db.query(QuestionPaper).filter(QuestionPaper.user_id == user_id).all()
    return papers


@app.post("/api/interactive-element")
async def create_interactive_element(
    request: InteractiveElementRequest, db: Session = Depends(get_db)
):
    try:
        response = await ollama_client.generate_interactive_element(
            request.subject, request.topic, request.element_type
        )

        element = InteractiveElement(
            user_id=request.user_id,
            subject=request.subject,
            topic=request.topic,
            element_type=request.element_type,
            content=response["response"],
            difficulty_level="Moderate",
            learning_objectives=[],
            completion_status=False,
        )
        db.add(element)
        db.commit()
        db.refresh(element)

        return {
            "message": "Interactive element created successfully",
            "element_id": element.id,
            "content": response["response"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/flashcards")
async def generate_flashcards(request: FlashcardRequest, db: Session = Depends(get_db)):
    try:
        response = await ollama_client.generate_flashcards(
            request.subject, request.topic, request.num_cards
        )

        flashcards = []
        for card_data in response["response"].split("\n\n"):
            if card_data.strip():
                card = Flashcard(
                    user_id=request.user_id,
                    subject=request.subject,
                    topic=request.topic,
                    front=card_data.split("\n")[0],
                    back="\n".join(card_data.split("\n")[1:]),
                    difficulty="Medium",
                    category="Concept",
                    review_count=0,
                    mastery_level=0.0,
                )
                db.add(card)
                flashcards.append(card)

        db.commit()
        return {
            "message": f"{len(flashcards)} flashcards created successfully",
            "flashcards": [
                {"id": f.id, "front": f.front, "back": f.back} for f in flashcards
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/flashcards/{user_id}")
async def get_flashcards(user_id: int, db: Session = Depends(get_db)):
    flashcards = db.query(Flashcard).filter(Flashcard.user_id == user_id).all()
    return flashcards


@app.post("/api/flashcards/{flashcard_id}/review")
async def review_flashcard(
    flashcard_id: int, mastery_level: float, db: Session = Depends(get_db)
):
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    flashcard.mastery_level = mastery_level
    flashcard.review_count += 1
    flashcard.last_reviewed = datetime.utcnow()

    db.commit()
    return {"message": "Flashcard reviewed successfully"}


@app.get("/api/interactive-elements/{user_id}")
async def get_interactive_elements(user_id: int, db: Session = Depends(get_db)):
    elements = (
        db.query(InteractiveElement).filter(InteractiveElement.user_id == user_id).all()
    )
    return elements


@app.post("/api/interactive-elements/{element_id}/complete")
async def complete_interactive_element(
    element_id: int, feedback: dict, db: Session = Depends(get_db)
):
    element = (
        db.query(InteractiveElement).filter(InteractiveElement.id == element_id).first()
    )
    if not element:
        raise HTTPException(status_code=404, detail="Interactive element not found")

    element.completion_status = True
    element.feedback = feedback
    element.time_spent = feedback.get("time_spent", 0)

    db.commit()
    return {"message": "Interactive element completed successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
