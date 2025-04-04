import json
from typing import Dict, List, Optional

import httpx


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def generate_lesson(
        self, subject: str, topic: str, level: str, preferences: Optional[Dict] = None
    ) -> Dict:
        """Generate a personalized lesson based on user preferences and learning style."""
        prompt = f"""Generate a comprehensive lesson on {topic} for {subject} at {level} level.
        Consider the following preferences: {json.dumps(preferences) if preferences else 'None'}
        Include:
        1. Introduction and learning objectives
        2. Key concepts with examples
        3. Interactive elements (quizzes, exercises, simulations)
        4. Practice problems with solutions
        5. Summary and key takeaways
        6. Additional resources for further learning
        7. Real-world applications
        8. Common misconceptions and how to avoid them"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def generate_interactive_element(
        self, subject: str, topic: str, element_type: str
    ) -> Dict:
        """Generate interactive learning elements like simulations, exercises, or visualizations."""
        prompt = f"""Generate an interactive {element_type} for {topic} in {subject}.
        Include:
        1. Clear instructions
        2. Interactive components
        3. Expected outcomes
        4. Learning objectives
        5. Assessment criteria
        6. Feedback mechanism"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def generate_quiz(
        self,
        subject: str,
        topic: str,
        level: str,
        num_questions: int = 5,
        question_types: List[str] = ["multiple_choice"],
    ) -> Dict:
        """Generate a quiz with various question types and difficulty levels."""
        prompt = f"""Generate a {num_questions}-question quiz on {topic} for {subject} at {level} level.
        Include the following question types: {', '.join(question_types)}
        For each question:
        1. Question text
        2. Options (if applicable)
        3. Correct answer
        4. Detailed explanation
        5. Difficulty level
        6. Time estimate for answering
        7. Hints (if applicable)
        8. Common mistakes to watch out for"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "deepseek-r1", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def generate_study_plan(self, user_profile: Dict, goals: Dict) -> Dict:
        """Generate a personalized study plan based on user profile and goals."""
        prompt = f"""Create a personalized study plan based on:
        User Profile: {json.dumps(user_profile)}
        Learning Goals: {json.dumps(goals)}
        Include:
        1. Weekly schedule with time slots
        2. Topic priorities and dependencies
        3. Practice recommendations
        4. Progress milestones
        5. Resource recommendations
        6. Revision strategy
        7. Break and rest periods
        8. Motivation techniques
        9. Progress tracking methods"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def analyze_question_paper(self, content: str, subject: str) -> Dict:
        """Analyze a question paper and provide insights."""
        prompt = f"""Analyze this {subject} question paper:
        {content}
        Provide:
        1. Topic distribution and weightage
        2. Difficulty levels and patterns
        3. Key concepts covered
        4. Question types and their distribution
        5. Suggested study areas
        6. Common mistakes to avoid
        7. Time management tips
        8. Scoring strategy
        9. Important formulas/theorems to remember
        10. Practice recommendations"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def get_learning_recommendations(self, progress_data: Dict) -> Dict:
        """Generate personalized learning recommendations based on progress."""
        prompt = f"""Analyze this learning progress data and provide recommendations:
        {json.dumps(progress_data)}
        Include:
        1. Strengths and weaknesses
        2. Suggested focus areas
        3. Learning resources
        4. Practice strategies
        5. Time management tips
        6. Motivation strategies
        7. Study techniques
        8. Revision schedule
        9. Practice test recommendations
        10. Mindset and attitude tips"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def generate_flashcards(
        self, subject: str, topic: str, num_cards: int = 10
    ) -> Dict:
        """Generate flashcards for quick revision."""
        prompt = f"""Generate {num_cards} flashcards for {topic} in {subject}.
        For each flashcard:
        1. Front: Key concept or question
        2. Back: Detailed explanation or answer
        3. Category: Easy/Medium/Hard
        4. Related concepts
        5. Memory aids or mnemonics"""

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={"model": "mixtral", "prompt": prompt, "stream": False},
        )
        return response.json()

    async def close(self):
        await self.client.aclose()
