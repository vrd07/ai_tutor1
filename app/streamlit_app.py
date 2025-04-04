from typing import Dict

import httpx
import streamlit as st

# Constants
API_URL = "http://localhost:8000"
SUBJECTS = ["Mathematics", "Science", "History", "Basic Programming", "Geography"]
LEVELS = ["Beginner", "Moderate", "Advanced"]
QUESTION_TYPES = ["multiple_choice", "true_false", "short_answer", "essay"]

# Page config
st.set_page_config(page_title="AI Personal Tutor", page_icon="📚", layout="wide")

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}


def show_profile_page():
    st.title("Student Profile")

    with st.form("profile_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")

        st.subheader("Subject Levels")
        subjects = {}
        for subject in SUBJECTS:
            subjects[subject] = st.selectbox(
                f"{subject} Level", LEVELS, key=f"level_{subject}"
            )

        st.subheader("Learning Preferences")
        preferences = {
            "learning_style": st.selectbox(
                "Preferred Learning Style",
                ["Visual", "Auditory", "Reading/Writing", "Kinesthetic"],
            ),
            "study_time": st.selectbox(
                "Preferred Study Time", ["Morning", "Afternoon", "Evening", "Night"]
            ),
            "difficulty_preference": st.selectbox(
                "Difficulty Preference", ["Gradual", "Challenging", "Mixed"]
            ),
        }

        if st.form_submit_button("Save Profile"):
            try:
                response = httpx.post(
                    f"{API_URL}/api/profile",
                    json={
                        "name": name,
                        "email": email,
                        "subjects": subjects,
                        "preferences": preferences,
                    },
                )
                if response.status_code == 200:
                    st.session_state.user_id = response.json()["user_id"]
                    st.success("Profile created successfully!")
                else:
                    st.error("Error creating profile")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_lessons_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Generate Lesson")

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic")
        level = st.selectbox("Level", LEVELS)

    with col2:
        st.subheader("Lesson Preferences")
        preferences = {
            "include_examples": st.checkbox("Include Examples", value=True),
            "include_practice": st.checkbox("Include Practice Problems", value=True),
            "include_resources": st.checkbox(
                "Include Additional Resources", value=True
            ),
        }

    if st.button("Generate Lesson"):
        with st.spinner("Generating lesson..."):
            try:
                response = httpx.post(
                    f"{API_URL}/api/lesson",
                    json={
                        "subject": subject,
                        "topic": topic,
                        "level": level,
                        "preferences": preferences,
                    },
                )
                if response.status_code == 200:
                    lesson = response.json()
                    st.markdown(lesson["content"])

                    # Save progress
                    httpx.post(
                        f"{API_URL}/api/progress",
                        json={
                            "user_id": st.session_state.user_id,
                            "subject": subject,
                            "topic": topic,
                            "score": 100,  # Lesson completion
                            "time_spent": 30,  # Estimated time
                            "difficulty_level": level,
                            "feedback": {"completion": True},
                        },
                    )
                else:
                    st.error("Error generating lesson")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_quizzes_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Generate Quiz")

    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic")
        level = st.selectbox("Level", LEVELS)
        num_questions = st.slider("Number of Questions", 1, 20, 5)

    with col2:
        st.subheader("Question Types")
        question_types = st.multiselect(
            "Select Question Types", QUESTION_TYPES, default=["multiple_choice"]
        )

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            try:
                response = httpx.post(
                    f"{API_URL}/api/quiz",
                    json={
                        "subject": subject,
                        "topic": topic,
                        "level": level,
                        "num_questions": num_questions,
                        "question_types": question_types,
                    },
                )
                if response.status_code == 200:
                    quiz = response.json()
                    st.session_state.current_quiz = quiz
                    show_quiz_interface(quiz, subject, topic)
                else:
                    st.error("Error generating quiz")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_quiz_interface(quiz: Dict, subject: str, topic: str):
    st.subheader("Quiz")

    questions = quiz["content"].split("\n\n")
    score = 0
    total_questions = len(questions)

    for i, question in enumerate(questions, 1):
        st.write(f"**Question {i}:**")
        st.write(question)

        if "multiple_choice" in st.session_state.current_quiz.get("question_types", []):
            options = question.split("\n")[1:5]
            answer = st.radio("Select your answer:", options, key=f"q_{i}")
            st.session_state.quiz_answers[f"q_{i}"] = answer
        else:
            answer = st.text_area("Your answer:", key=f"q_{i}")
            st.session_state.quiz_answers[f"q_{i}"] = answer

    if st.button("Submit Quiz"):
        # Calculate score (simplified for demo)
        score = len([a for a in st.session_state.quiz_answers.values() if a])
        percentage = (score / total_questions) * 100

        # Save progress
        httpx.post(
            f"{API_URL}/api/progress",
            json={
                "user_id": st.session_state.user_id,
                "subject": subject,
                "topic": topic,
                "score": percentage,
                "time_spent": 15,  # Estimated time
                "difficulty_level": "Moderate",
                "feedback": {"score": percentage},
            },
        )

        st.success(f"Quiz completed! Score: {percentage:.1f}%")


def show_study_plan_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Study Plan")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Learning Goals")
        goals = {
            "target_subjects": st.multiselect("Target Subjects", SUBJECTS),
            "timeframe": st.selectbox(
                "Timeframe", ["1 week", "2 weeks", "1 month", "3 months"]
            ),
            "focus_areas": st.text_area("Specific Focus Areas"),
            "target_score": st.slider("Target Score (%)", 0, 100, 80),
        }

    with col2:
        st.subheader("Study Plan Preferences")
        duration = st.number_input("Duration (days)", 1, 90, 30)
        include_practice = st.checkbox("Include Practice Sessions", value=True)
        include_revision = st.checkbox("Include Revision Time", value=True)

    if st.button("Generate Study Plan"):
        with st.spinner("Generating study plan..."):
            try:
                response = httpx.post(
                    f"{API_URL}/api/study-plan",
                    json={
                        "user_id": st.session_state.user_id,
                        "goals": goals,
                        "duration": duration,
                    },
                )
                if response.status_code == 200:
                    plan = response.json()
                    st.success("Study plan created successfully!")
                    st.json(plan)
                else:
                    st.error("Error generating study plan")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Display existing study plans
    st.subheader("Your Study Plans")
    try:
        response = httpx.get(f"{API_URL}/api/study-plans/{st.session_state.user_id}")
        if response.status_code == 200:
            plans = response.json()
            for plan in plans:
                with st.expander(f"Plan {plan['id']} - {plan['status']}"):
                    st.json(plan["plan"])
        else:
            st.info("No study plans found")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_progress_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Progress Tracking")

    try:
        response = httpx.get(f"{API_URL}/api/progress/{st.session_state.user_id}")
        if response.status_code == 200:
            progress = response.json()

            # Group progress by subject
            subject_progress = {}
            for p in progress:
                if p["subject"] not in subject_progress:
                    subject_progress[p["subject"]] = []
                subject_progress[p["subject"]].append(p)

            # Display progress for each subject
            for subject, progress_list in subject_progress.items():
                st.subheader(subject)

                # Calculate average score
                avg_score = sum(p["score"] for p in progress_list) / len(progress_list)
                st.metric("Average Score", f"{avg_score:.1f}%")

                # Display progress details
                for p in progress_list:
                    with st.expander(f"Topic: {p['topic']} - Score: {p['score']}%"):
                        st.write(f"Date: {p['completed_at']}")
                        st.write(f"Time Spent: {p['time_spent']} minutes")
                        st.write(f"Difficulty: {p['difficulty_level']}")
                        if p.get("feedback"):
                            st.write("Feedback:", p["feedback"])
        else:
            st.info("No progress data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_question_papers_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Question Papers")

    # Upload new paper
    st.subheader("Upload New Paper")
    col1, col2 = st.columns(2)

    with col1:
        subject = st.selectbox("Subject", SUBJECTS)
        uploaded_file = st.file_uploader("Choose a question paper", type=["pdf", "txt"])

    if uploaded_file and subject:
        if st.button("Upload and Analyze"):
            with st.spinner("Analyzing paper..."):
                try:
                    files = {
                        "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
                    }
                    response = httpx.post(
                        f"{API_URL}/api/upload-paper",
                        params={
                            "subject": subject,
                            "user_id": st.session_state.user_id,
                        },
                        files=files,
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Paper analyzed successfully!")
                        st.json(result["analysis"])
                    else:
                        st.error("Error analyzing paper")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Display existing papers
    st.subheader("Your Question Papers")
    try:
        response = httpx.get(
            f"{API_URL}/api/question-papers/{st.session_state.user_id}"
        )
        if response.status_code == 200:
            papers = response.json()
            for paper in papers:
                with st.expander(
                    f"{paper['subject']} - {paper['metadata']['filename']}"
                ):
                    st.write(f"Uploaded: {paper['metadata']['upload_date']}")
                    st.json(paper["analysis"])
        else:
            st.info("No question papers found")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_flashcards_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Flashcards")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Generate New Flashcards")
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic")
        num_cards = st.slider("Number of Cards", 1, 50, 10)

        if st.button("Generate Flashcards"):
            with st.spinner("Generating flashcards..."):
                try:
                    response = httpx.post(
                        f"{API_URL}/api/flashcards",
                        json={
                            "user_id": st.session_state.user_id,
                            "subject": subject,
                            "topic": topic,
                            "num_cards": num_cards,
                        },
                    )
                    if response.status_code == 200:
                        st.success("Flashcards generated successfully!")
                        st.session_state.current_flashcards = response.json()[
                            "flashcards"
                        ]
                    else:
                        st.error("Error generating flashcards")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col2:
        st.subheader("Your Flashcards")
        try:
            response = httpx.get(f"{API_URL}/api/flashcards/{st.session_state.user_id}")
            if response.status_code == 200:
                flashcards = response.json()
                if flashcards:
                    for card in flashcards:
                        with st.expander(f"Card {card['id']} - {card['subject']}"):
                            st.write("**Front:**")
                            st.write(card["front"])
                            st.write("**Back:**")
                            st.write(card["back"])
                            mastery = st.slider(
                                "Mastery Level",
                                0.0,
                                1.0,
                                card.get("mastery_level", 0.0),
                                key=f"mastery_{card['id']}",
                            )
                            if st.button("Save Review", key=f"review_{card['id']}"):
                                httpx.post(
                                    f"{API_URL}/api/flashcards/{card['id']}/review",
                                    json={"mastery_level": mastery},
                                )
                                st.success("Review saved!")
                else:
                    st.info("No flashcards found. Generate some to get started!")
            else:
                st.info("No flashcards found")
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_interactive_elements_page():
    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    st.title("Interactive Learning")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Create New Interactive Element")
        subject = st.selectbox("Subject", SUBJECTS)
        topic = st.text_input("Topic")
        element_type = st.selectbox(
            "Element Type", ["Quiz", "Simulation", "Exercise", "Visualization"]
        )

        if st.button("Generate Element"):
            with st.spinner("Generating interactive element..."):
                try:
                    response = httpx.post(
                        f"{API_URL}/api/interactive-element",
                        json={
                            "user_id": st.session_state.user_id,
                            "subject": subject,
                            "topic": topic,
                            "element_type": element_type,
                        },
                    )
                    if response.status_code == 200:
                        st.success("Interactive element created successfully!")
                        st.session_state.current_element = response.json()
                    else:
                        st.error("Error generating interactive element")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col2:
        st.subheader("Your Interactive Elements")
        try:
            response = httpx.get(
                f"{API_URL}/api/interactive-elements/{st.session_state.user_id}"
            )
            if response.status_code == 200:
                elements = response.json()
                if elements:
                    for element in elements:
                        with st.expander(
                            f"{element['element_type']} - {element['subject']}"
                        ):
                            st.write("**Topic:**", element["topic"])
                            st.write("**Content:**")
                            st.json(element["content"])
                            if not element["completion_status"]:
                                time_spent = st.number_input(
                                    "Time Spent (minutes)",
                                    1,
                                    120,
                                    30,
                                    key=f"time_{element['id']}",
                                )
                                feedback = st.text_area(
                                    "Feedback", key=f"feedback_{element['id']}"
                                )
                                if st.button(
                                    "Mark as Complete", key=f"complete_{element['id']}"
                                ):
                                    httpx.post(
                                        f"{API_URL}/api/interactive-elements/{element['id']}/complete",
                                        json={
                                            "time_spent": time_spent * 60,
                                            "feedback": feedback,
                                        },
                                    )
                                    st.success("Element completed!")
                else:
                    st.info(
                        "No interactive elements found. Create some to get started!"
                    )
            else:
                st.info("No interactive elements found")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# Main app
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        [
            "Profile",
            "Lessons",
            "Quizzes",
            "Study Plan",
            "Progress",
            "Question Papers",
            "Flashcards",
            "Interactive Learning",
        ],
    )

    if page == "Profile":
        show_profile_page()
    elif page == "Lessons":
        show_lessons_page()
    elif page == "Quizzes":
        show_quizzes_page()
    elif page == "Study Plan":
        show_study_plan_page()
    elif page == "Progress":
        show_progress_page()
    elif page == "Question Papers":
        show_question_papers_page()
    elif page == "Flashcards":
        show_flashcards_page()
    elif page == "Interactive Learning":
        show_interactive_elements_page()


if __name__ == "__main__":
    main()
