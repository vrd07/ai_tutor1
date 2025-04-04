from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    subjects = Column(JSON)  # Dictionary of subject:level pairs
    preferences = Column(JSON)  # User preferences like learning style, time preferences
    is_active = Column(Boolean, default=True)
    learning_goals = Column(JSON)  # User's learning goals and targets
    study_preferences = Column(JSON)  # Detailed study preferences

    # Relationships
    progress = relationship("Progress", back_populates="user")
    question_papers = relationship("QuestionPaper", back_populates="user")
    study_plans = relationship("StudyPlan", back_populates="user")
    flashcards = relationship("Flashcard", back_populates="user")
    interactive_elements = relationship("InteractiveElement", back_populates="user")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    score = Column(Float)  # Quiz score or completion percentage
    completed_at = Column(DateTime, default=datetime.utcnow)
    time_spent = Column(Integer)  # Time spent in seconds
    difficulty_level = Column(String)  # Easy, Medium, Hard
    feedback = Column(JSON)  # User feedback and AI suggestions
    learning_style = Column(String)  # Visual, Auditory, Reading/Writing, Kinesthetic
    confidence_level = Column(Float)  # User's confidence in the topic
    notes = Column(Text)  # User's personal notes

    # Relationships
    user = relationship("User", back_populates="progress")


class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    file_path = Column(String)
    analysis = Column(JSON)
    paper_metadata = Column(JSON)  # Changed from metadata to paper_metadata
    tags = Column(JSON)
    difficulty_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="question_papers")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    plan = Column(JSON)  # Study plan details
    duration = Column(Integer)  # Duration in days
    status = Column(String)  # Active, Completed, Archived
    progress = Column(Float)  # Completion percentage
    goals = Column(JSON)  # Specific learning goals
    schedule = Column(JSON)  # Detailed study schedule
    resources = Column(JSON)  # Recommended resources
    milestones = Column(JSON)  # Progress milestones

    # Relationships
    user = relationship("User", back_populates="study_plans")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    front = Column(Text, nullable=False)  # Question or concept
    back = Column(Text, nullable=False)  # Answer or explanation
    created_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime)
    difficulty = Column(String)  # Easy, Medium, Hard
    category = Column(String)  # Concept, Formula, Definition, etc.
    tags = Column(JSON)  # Tags for organization
    review_count = Column(Integer, default=0)
    mastery_level = Column(Float)  # 0-1 scale

    # Relationships
    user = relationship("User", back_populates="flashcards")


class InteractiveElement(Base):
    __tablename__ = "interactive_elements"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    element_type = Column(String)  # Quiz, Simulation, Exercise, etc.
    content = Column(JSON)  # Interactive content
    created_at = Column(DateTime, default=datetime.utcnow)
    difficulty_level = Column(String)
    learning_objectives = Column(JSON)
    feedback = Column(JSON)
    completion_status = Column(Boolean, default=False)
    time_spent = Column(Integer)  # Time spent in seconds

    # Relationships
    user = relationship("User", back_populates="interactive_elements")


# Create database engine
engine = create_engine("sqlite:///ai_tutor.db")
Base.metadata.create_all(engine)

# Create session
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
