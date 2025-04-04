# AI Personal Tutor

An intelligent tutoring system that provides personalized learning experiences using AI.

## Features

- User profile management
- Interactive lessons and quizzes
- Personalized study plans
- Progress tracking
- Question paper analysis
- Flashcards
- Interactive learning elements

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Database: SQLite with SQLAlchemy
- AI: Ollama API
- Authentication: JWT

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-tutor.git
cd ai-tutor
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```env
OLLAMA_API_URL=http://localhost:11434
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
python -c "from models.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Running the Application

1. Start the FastAPI backend:
```bash
cd ai_tutor
PYTHONPATH=$PYTHONPATH:. uvicorn app.main:app --reload
```

2. Start the Streamlit frontend:
```bash
cd ai_tutor
streamlit run app/streamlit_app.py
```

3. Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:8501

## Project Structure

```
ai_tutor/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI backend
│   └── streamlit_app.py # Streamlit frontend
├── models/
│   ├── __init__.py
│   ├── database.py      # Database models
│   └── ollama_client.py # Ollama API client
├── utils/
│   ├── __init__.py
│   └── ollama_client.py # Ollama API utilities
├── requirements.txt     # Project dependencies
├── .env                # Environment variables
└── README.md           # Project documentation
```

## API Documentation

Once the backend is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 