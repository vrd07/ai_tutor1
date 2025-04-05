import time

import httpx
import streamlit as st

# Constants
API_URL = "http://localhost:8000"
SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science"]
LEVELS = ["Beginner", "Moderate", "Advanced"]
QUESTION_TYPES = ["multiple_choice", "true_false", "short_answer", "essay"]

# Page config
st.set_page_config(
    page_title="AI Personal Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    /* Main background and text colors */
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50;
    }
    p, div {
        color: #34495e;
    }

    /* Button styling */
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #bdc3c7;
        background-color: white;
    }
    .stSelectbox>div>div>select {
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #bdc3c7;
        background-color: white;
    }

    /* Cards and containers */
    .css-1d391kg {
        padding: 1.5rem;
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #ecf0f1;
    }
    .css-1d391kg:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: #2c3e50;
    }
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white;
    }
    .css-1d391kg p, .css-1d391kg div {
        color: #ecf0f1;
    }

    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #3498db;
    }

    /* Expander headers */
    .streamlit-expanderHeader {
        background-color: #ecf0f1;
        border-radius: 8px;
        padding: 8px 16px;
    }

    /* Radio buttons */
    .stRadio > div {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #ecf0f1;
    }

    /* Success messages */
    .stSuccess {
        background-color: #2ecc71;
        color: white;
    }

    /* Warning messages */
    .stWarning {
        background-color: #f39c12;
        color: white;
    }

    /* Error messages */
    .stError {
        background-color: #e74c3c;
        color: white;
    }

    /* Info messages */
    .stInfo {
        background-color: #3498db;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}


def show_profile_page():
    st.title("👤 User Profile")

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Create Your Profile")
            name = st.text_input("Your Name", placeholder="Enter your name")

            st.subheader("Subject Levels")
            subject_levels = {}
            for subject in SUBJECTS:
                subject_levels[subject] = st.select_slider(
                    f"{subject} Level",
                    options=["Beginner", "Intermediate", "Advanced"],
                    value="Beginner",
                )

            if st.button("Save Profile", key="save_profile"):
                with st.spinner("Saving profile..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/api/profiles",
                            json={"name": name, "subject_levels": subject_levels},
                        )
                        if response.status_code == 200:
                            st.session_state.user_id = response.json()["id"]
                            st.success("Profile created successfully!")
                            time.sleep(1)
                            st.experimental_rerun()
                        else:
                            st.error("Error creating profile")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            st.subheader("Profile Preview")
            if name:
                st.markdown(f"### {name}")
                for subject, level in subject_levels.items():
                    st.markdown(f"**{subject}**: {level}")
            else:
                st.info("Complete the form to see your profile preview")


def show_lessons_page():
    st.title("📚 Lessons")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Generate New Lesson")
            subject = st.selectbox("Subject", SUBJECTS)
            topic = st.text_input("Topic", placeholder="Enter a topic")
            difficulty = st.select_slider(
                "Difficulty Level",
                options=["Beginner", "Intermediate", "Advanced"],
                value="Beginner",
            )

            if st.button("Generate Lesson"):
                with st.spinner("Generating lesson..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/api/lessons",
                            json={
                                "user_id": st.session_state.user_id,
                                "subject": subject,
                                "topic": topic,
                                "difficulty": difficulty,
                            },
                        )
                        if response.status_code == 200:
                            lesson = response.json()
                            st.session_state.current_lesson = lesson
                            st.success("Lesson generated successfully!")
                        else:
                            st.error("Error generating lesson")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            st.subheader("Recent Lessons")
            try:
                response = httpx.get(
                    f"{API_URL}/api/progress/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    progress = response.json()
                    if progress:
                        for subject, data in progress.items():
                            with st.expander(f"{subject} Progress"):
                                st.markdown(
                                    f"**Completed Lessons**: {data['completed_lessons']}"
                                )
                                st.markdown(f"**Quiz Score**: {data['quiz_score']}%")
                    else:
                        st.info("No lessons completed yet")
                else:
                    st.info("No progress data available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "current_lesson" in st.session_state:
        st.markdown("---")
        st.subheader("Current Lesson")
        lesson = st.session_state.current_lesson
        st.markdown(f"### {lesson['topic']}")
        st.markdown(lesson["content"])

        if st.button("Mark as Complete"):
            try:
                response = httpx.post(
                    f"{API_URL}/api/progress",
                    json={
                        "user_id": st.session_state.user_id,
                        "subject": lesson["subject"],
                        "topic": lesson["topic"],
                        "completed": True,
                    },
                )
                if response.status_code == 200:
                    st.success("Progress saved!")
                    del st.session_state.current_lesson
                    time.sleep(1)
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_quizzes_page():
    st.title("📝 Quizzes")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Generate New Quiz")
            subject = st.selectbox("Subject", SUBJECTS)
            topic = st.text_input("Topic", placeholder="Enter a topic")
            num_questions = st.slider("Number of Questions", 1, 20, 5)

            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/api/quizzes",
                            json={
                                "user_id": st.session_state.user_id,
                                "subject": subject,
                                "topic": topic,
                                "num_questions": num_questions,
                            },
                        )
                        if response.status_code == 200:
                            quiz = response.json()
                            st.session_state.current_quiz = quiz
                            st.success("Quiz generated successfully!")
                        else:
                            st.error("Error generating quiz")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            st.subheader("Quiz History")
            try:
                response = httpx.get(
                    f"{API_URL}/api/progress/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    progress = response.json()
                    if progress:
                        for subject, data in progress.items():
                            with st.expander(f"{subject} Quiz History"):
                                st.markdown(f"**Average Score**: {data['quiz_score']}%")
                                st.markdown(
                                    f"**Quizzes Taken**: {data.get('quizzes_taken', 0)}"
                                )
                    else:
                        st.info("No quiz history available")
                else:
                    st.info("No progress data available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "current_quiz" in st.session_state:
        show_quiz_interface()


def show_quiz_interface():
    quiz = st.session_state.current_quiz
    st.markdown("---")
    st.subheader(f"Quiz: {quiz['topic']}")

    if "answers" not in st.session_state:
        st.session_state.answers = {}
        st.session_state.score = 0

    for i, question in enumerate(quiz["questions"]):
        st.markdown(f"### Question {i+1}")
        st.markdown(question["question"])

        options = question["options"]
        selected_option = st.radio(
            "Select your answer:", options, key=f"q_{i}", index=None
        )

        if selected_option:
            st.session_state.answers[i] = selected_option

    if st.button("Submit Quiz"):
        score = 0
        for i, question in enumerate(quiz["questions"]):
            if st.session_state.answers.get(i) == question["correct_answer"]:
                score += 1

        st.session_state.score = (score / len(quiz["questions"])) * 100
        st.success(f"Quiz completed! Your score: {st.session_state.score:.1f}%")

        try:
            response = httpx.post(
                f"{API_URL}/api/progress",
                json={
                    "user_id": st.session_state.user_id,
                    "subject": quiz["subject"],
                    "topic": quiz["topic"],
                    "quiz_score": st.session_state.score,
                },
            )
            if response.status_code == 200:
                st.success("Progress saved!")
                del st.session_state.current_quiz
                del st.session_state.answers
                time.sleep(1)
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {str(e)}")


def show_study_plan_page():
    st.title("📅 Study Plan")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Generate Study Plan")
            time_frame = st.selectbox(
                "Time Frame", ["1 Week", "2 Weeks", "1 Month", "3 Months"]
            )

            if st.button("Generate Plan"):
                with st.spinner("Generating study plan..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/api/study-plan",
                            json={
                                "user_id": st.session_state.user_id,
                                "time_frame": time_frame,
                            },
                        )
                        if response.status_code == 200:
                            plan = response.json()
                            st.session_state.current_plan = plan
                            st.success("Study plan generated successfully!")
                        else:
                            st.error("Error generating study plan")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            st.subheader("Study Goals")
            try:
                response = httpx.get(
                    f"{API_URL}/api/profiles/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    profile = response.json()
                    st.markdown("### Current Levels")
                    for subject, level in profile["subject_levels"].items():
                        st.markdown(f"**{subject}**: {level}")
                else:
                    st.info("No profile data available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "current_plan" in st.session_state:
        st.markdown("---")
        st.subheader("Your Study Plan")
        plan = st.session_state.current_plan
        st.markdown(plan["plan"])


def show_progress_page():
    st.title("📊 Progress")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    try:
        response = httpx.get(f"{API_URL}/api/progress/{st.session_state.user_id}")
        if response.status_code == 200:
            progress = response.json()
            if progress:
                for subject, data in progress.items():
                    with st.expander(f"{subject} Progress", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Completed Lessons", data["completed_lessons"])
                        with col2:
                            st.metric("Quiz Score", f"{data['quiz_score']}%")
                        with col3:
                            st.metric(
                                "Time Spent", f"{data.get('time_spent', 0)} minutes"
                            )

                        st.progress(data["quiz_score"] / 100)
            else:
                st.info("No progress data available")
        else:
            st.info("No progress data available")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_question_papers_page():
    st.title("📄 Question Papers")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Upload Question Paper")
            subject = st.selectbox("Subject", SUBJECTS)
            file = st.file_uploader(
                "Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"]
            )

            if file and st.button("Upload"):
                with st.spinner("Uploading and analyzing..."):
                    try:
                        files = {"file": (file.name, file, file.type)}
                        response = httpx.post(
                            f"{API_URL}/api/upload-paper",
                            files=files,
                            data={
                                "subject": subject,
                                "user_id": str(st.session_state.user_id),
                            },
                        )
                        if response.status_code == 200:
                            result = response.json()
                            st.success("Paper uploaded and analyzed successfully!")
                            st.markdown("### Analysis Results")
                            st.markdown(result["analysis"])
                        else:
                            st.error("Error uploading paper")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            st.subheader("Uploaded Papers")
            try:
                response = httpx.get(
                    f"{API_URL}/api/question-papers/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    papers = response.json()
                    if papers:
                        for paper in papers:
                            with st.expander(paper["subject"]):
                                st.markdown(f"**Uploaded**: {paper['created_at']}")
                                st.markdown(f"**Analysis**: {paper['analysis']}")
                    else:
                        st.info("No papers uploaded yet")
                else:
                    st.info("No papers available")
            except Exception as e:
                st.error(f"Error: {str(e)}")


def show_flashcards_page():
    st.title("🎴 Flashcards")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Generate New Flashcards")
            subject = st.selectbox("Subject", SUBJECTS)
            topic = st.text_input("Topic", placeholder="Enter a topic")
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
            st.subheader("Flashcard Stats")
            try:
                response = httpx.get(
                    f"{API_URL}/api/flashcards/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    flashcards = response.json()
                    if flashcards:
                        total_cards = len(flashcards)
                        mastered_cards = sum(
                            1
                            for card in flashcards
                            if card.get("mastery_level", 0) >= 0.8
                        )
                        st.metric("Total Cards", total_cards)
                        st.metric("Mastered Cards", mastered_cards)
                        st.progress(
                            mastered_cards / total_cards if total_cards > 0 else 0
                        )
                    else:
                        st.info("No flashcards available")
                else:
                    st.info("No flashcards available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "current_flashcards" in st.session_state:
        st.markdown("---")
        st.subheader("Current Flashcards")
        for i, card in enumerate(st.session_state.current_flashcards):
            with st.expander(f"Card {i+1} - {card['subject']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Front")
                    st.markdown(card["front"])
                with col2:
                    st.markdown("### Back")
                    st.markdown(card["back"])
                mastery = st.slider(
                    "Mastery Level",
                    0.0,
                    1.0,
                    card.get("mastery_level", 0.0),
                    key=f"mastery_{card['id']}",
                )
                if st.button("Save Review", key=f"review_{card['id']}"):
                    try:
                        response = httpx.post(
                            f"{API_URL}/api/flashcards/{card['id']}/review",
                            json={"mastery_level": mastery},
                        )
                        if response.status_code == 200:
                            st.success("Review saved!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


def show_interactive_elements_page():
    st.title("🎮 Interactive Learning")

    if not st.session_state.user_id:
        st.warning("Please create a profile first!")
        return

    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Create New Interactive Element")
            subject = st.selectbox("Subject", SUBJECTS)
            topic = st.text_input("Topic", placeholder="Enter a topic")
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
            st.subheader("Interactive Elements Stats")
            try:
                response = httpx.get(
                    f"{API_URL}/api/interactive-elements/{st.session_state.user_id}"
                )
                if response.status_code == 200:
                    elements = response.json()
                    if elements:
                        total_elements = len(elements)
                        completed_elements = sum(
                            1 for e in elements if e["completion_status"]
                        )
                        st.metric("Total Elements", total_elements)
                        st.metric("Completed Elements", completed_elements)
                        st.progress(
                            completed_elements / total_elements
                            if total_elements > 0
                            else 0
                        )
                    else:
                        st.info("No interactive elements available")
                else:
                    st.info("No interactive elements available")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    if "current_element" in st.session_state:
        st.markdown("---")
        st.subheader("Current Interactive Element")
        element = st.session_state.current_element
        st.markdown(f"### {element['element_type']} - {element['topic']}")
        st.markdown("#### Content")
        st.json(element["content"])

        if not element["completion_status"]:
            time_spent = st.number_input(
                "Time Spent (minutes)", 1, 120, 30, key=f"time_{element['id']}"
            )
            feedback = st.text_area("Feedback", key=f"feedback_{element['id']}")
            if st.button("Mark as Complete", key=f"complete_{element['id']}"):
                try:
                    response = httpx.post(
                        f"{API_URL}/api/interactive-elements/{element['id']}/complete",
                        json={"time_spent": time_spent * 60, "feedback": feedback},
                    )
                    if response.status_code == 200:
                        st.success("Element completed!")
                        del st.session_state.current_element
                        time.sleep(1)
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")


# Main app
def main():
    # Sidebar navigation
    st.sidebar.title("🎓 AI Personal Tutor")
    st.sidebar.markdown("---")

    if st.session_state.user_id:
        st.sidebar.success(f"Logged in as User #{st.session_state.user_id}")
    else:
        st.sidebar.info("Please create a profile to get started")

    page = st.sidebar.radio(
        "Navigation",
        [
            "👤 Profile",
            "📚 Lessons",
            "📝 Quizzes",
            "📅 Study Plan",
            "📊 Progress",
            "📄 Question Papers",
            "🎴 Flashcards",
            "🎮 Interactive Learning",
        ],
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "AI Personal Tutor is an intelligent learning platform that provides "
        "personalized educational experiences using artificial intelligence."
    )

    # Page routing
    if page == "👤 Profile":
        show_profile_page()
    elif page == "📚 Lessons":
        show_lessons_page()
    elif page == "📝 Quizzes":
        show_quizzes_page()
    elif page == "📅 Study Plan":
        show_study_plan_page()
    elif page == "📊 Progress":
        show_progress_page()
    elif page == "📄 Question Papers":
        show_question_papers_page()
    elif page == "🎴 Flashcards":
        show_flashcards_page()
    elif page == "🎮 Interactive Learning":
        show_interactive_elements_page()


if __name__ == "__main__":
    main()
