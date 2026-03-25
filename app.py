import os
import json
import random
import time
from datetime import datetime

import requests
import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

# Optional cookie package
COOKIE_MANAGER_AVAILABLE = True
try:
    from st_cookies_manager import EncryptedCookieManager
except Exception:
    COOKIE_MANAGER_AVAILABLE = False
    EncryptedCookieManager = None


# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Python Final Exam",
    page_icon="📝",
    layout="centered",
)

# =================================================
# SECRETS / ENV
# =================================================
def read_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def read_env(key: str, default=None):
    return os.getenv(key, default)


FIREBASE_SERVICE_ACCOUNT_JSON = read_secret("FIREBASE_SERVICE_ACCOUNT_JSON", None)

FIREBASE_WEB_API_KEY = (
    read_secret("FIREBASE_WEB_API_KEY")
    or read_env("FIREBASE_WEB_API_KEY")
    or ""
)

TEACHER_EMAILS_RAW = (
    read_secret("TEACHER_EMAILS")
    or read_env("TEACHER_EMAILS")
    or ""
)

COOKIE_PASSWORD = (
    read_secret("COOKIE_PASSWORD")
    or read_env("COOKIE_PASSWORD")
    or "change-this-cookie-password"
)

QUIZ_DURATION_MINUTES = 18
WARNING_MINUTES = 5

RESULTS_COLLECTION = "exam_results"
STUDENT_PROFILES_COLLECTION = "student_profiles"
EXAM_ATTEMPTS_COLLECTION = "exam_attempts"

PERIOD_OPTIONS = [
    "Period 1", "Period 2", "Period 3", "Period 4",
    "Period 5", "Period 6", "Period 7", "Period 8", "Other"
]

# =================================================
# QUIZ QUESTIONS (FALLBACK ONLY)
# =================================================
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which of the following checks for value equality between two lists A = [1, 2, 3, 4], and B = ['a', 'b', 'c', 'd']?",
        "type": "mc",
        "options": ["A = B", "A == B", "A is B", "A != B"],
        "answer": "A == B",
    },
    {
        "id": 2,
        "question": "Order the following Python operators from HIGHEST to LOWEST precedence.",
        "type": "sequencing",
        "options": [
            "And",
            "Unary plus & Unary minus",
            "Exponent",
            "Addition & subtraction",
            "Parenthesis",
            "Multiplication & division",
        ],
        "answer": [
            "Parenthesis",
            "Exponent",
            "Unary plus & Unary minus",
            "Multiplication & division",
            "Addition & subtraction",
            "And",
        ],
    },
    {
        "id": 3,
        "question": "Given value1=9, value2=4, what is the data type of A after the expression A = (value1 % value2 * 10) // 2.0** 3.0 + value2?",
        "type": "mc",
        "options": ["18.0", "5.0", "18", "22.0"],
        "answer": "5.0",
    },
    {
        "id": 4,
        "question": "Complete the Python script below by selecting the correct options.",
        "type": "dropdown_sim",
        "code": """import os
file_name = "my_document.txt"
text_to_write = "This line will be added to the end.\\n"

if os.path.[DROPDOWN 1](file_name):
    print(f"File '{file_name}' exists. Append text.")
    file = open(file_name, [DROPDOWN 2])
    [DROPDOWN 3](text_to_write)
    file.close()
else:
    print(f"File '{file_name}' does not exist. No file was opened or written to")""",
        "dropdowns": [
            {
                "label": "DROPDOWN 1 (os.path Method)",
                "options": ["get_status", "exists", "isfile", "check_file"],
                "answer": "exists",
            },
            {
                "label": "DROPDOWN 2 (File Mode)",
                "options": ["'r'", "'w'", "'a'", "'r+'"],
                "answer": "'a'",
            },
            {
                "label": "DROPDOWN 3 (File Object Method)",
                "options": ["file.read", "file.write", "file.append", "file.close"],
                "answer": "file.write",
            },
        ],
        "answer": ["exists", "'a'", "file.write"],
    },
    {
        "id": 5,
        "question": "Select the correct options to make the unittest code valid.",
        "type": "dropdown_sim",
        "code": """import unittest

class [DROPDOWN 1]([DROPDOWN 2]):

    def [DROPDOWN 3](self):
        pass

if __name__ == '__main__':
    unittest.main()""",
        "dropdowns": [
            {
                "label": "DROPDOWN 1 (Class Name)",
                "options": ["TestModule", "TestSuite", "TestMethod", "MyClass"],
                "answer": "TestMethod",
            },
            {
                "label": "DROPDOWN 2 (Inheritance)",
                "options": ["unittest.BaseClass", "unittest.TestRunner", "unittest.TestCase", "TestCase"],
                "answer": "unittest.TestCase",
            },
            {
                "label": "DROPDOWN 3 (Method Name)",
                "options": ["run_method", "test_setup", "execute_test", "test_method"],
                "answer": "test_method",
            },
        ],
        "answer": ["TestMethod", "unittest.TestCase", "test_method"],
    },
    {
        "id": 6,
        "question": """Given the list My_list containing all lowercase letters, what is the correct output sequence for new_slice_3_to_6 followed by new_slice_to_6?

My_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', ... 'z']
new_slice_3_to_6 = My_list[3:6]
new_slice_to_6 = My_list[:6]""",
        "type": "mc",
        "options": [
            "['c', 'd', 'e'] and ['a', 'b', 'c', 'd', 'e']",
            "['d', 'e', 'f'] and ['a', 'b', 'c', 'd', 'e', 'f']",
            "['c', 'd', 'e', 'f'] and ['a', 'b', 'c', 'd', 'e']",
            "['d', 'e', 'f'] and ['b', 'c', 'd', 'e', 'f']",
        ],
        "answer": "['d', 'e', 'f'] and ['a', 'b', 'c', 'd', 'e', 'f']",
    },
    {
        "id": 7,
        "question": "Match each Python value with its corresponding data type.",
        "type": "dropdown_sim",
        "code": None,
        "dropdowns": [
            {"label": 'Value: "false"', "options": ["Float", "Int", "String", "Boolean"], "answer": "String"},
            {"label": "Value: 1.0", "options": ["Float", "Int", "String", "Boolean"], "answer": "Float"},
            {"label": "Value: False", "options": ["Float", "Int", "String", "Boolean"], "answer": "Boolean"},
            {"label": "Value: 1", "options": ["Float", "Int", "String", "Boolean"], "answer": "Int"},
        ],
        "answer": ["String", "Float", "Boolean", "Int"],
    },
    {
        "id": 8,
        "question": "Given the command 'main.py this beautiful nature', which value is stored at index position 2 in the sys.argv list?",
        "type": "mc",
        "options": ["main.py", "this", "beautiful", "nature"],
        "answer": "beautiful",
    },
    {
        "id": 9,
        "question": """Given grade=76 and rank=3, what is the output?

if grade >= 80 and rank == 2:
    print("your grade is B")
elif grade < 70 and rank == 2:
    print("your grade is C")
else:
    print("your grade is F")""",
        "type": "mc",
        "options": ["your grade is B", "your grade is C", "your grade is F", "SyntaxError"],
        "answer": "your grade is F",
    },
    {
        "id": 10,
        "question": "Analyze the following nested loop output.",
        "type": "mc",
        "options": [
            "Only prints 'Outer Loop (Row) # 1:' and 'Inner Loop Value: 1 2 3'",
            "Prints three rows, each followed by three inner loop values (1, 2, and 3).",
            "The code produces an infinite loop.",
            "Prints 'Outer Loop (Row) # 3:' and 'Inner Loop Value: 1 2 3' only.",
        ],
        "answer": "Prints three rows, each followed by three inner loop values (1, 2, and 3).",
    },
    {
        "id": 11,
        "question": "If a player starts a new game and scores on their very first turn, what value must be passed to increment_score(current_score) first?",
        "type": "mc",
        "options": ["1", "2", "0", "None"],
        "answer": "0",
    },
    {
        "id": 12,
        "question": "What is the output of the try/except/else/finally structure when 10 / 2 succeeds?",
        "type": "mc",
        "options": [
            "Operation succeeded. Execution finished. Final value calculated was 5.0.",
            "Exception occurred. Execution finished. Final value calculated was 0.",
            "Operation succeeded.",
            "Execution finished. Final value calculated was 5.0.",
        ],
        "answer": "Operation succeeded. Execution finished. Final value calculated was 5.0.",
    },
    {
        "id": 13,
        "question": "What happens if an except block is placed after finally?",
        "type": "mc",
        "options": [
            "The code runs, but the 'except' block is ignored.",
            "Python will raise a SyntaxError because 'finally' must terminate the block.",
            "Python will raise an IndentationError because the 'except' block is not inside the 'try' block.",
            "The code produces an infinite loop.",
        ],
        "answer": "Python will raise a SyntaxError because 'finally' must terminate the block.",
    },
    {
        "id": 14,
        "question": "Could you add multiple except blocks within a single try structure in Python?",
        "type": "mc",
        "options": ["True", "False"],
        "answer": "True",
    },
    {
        "id": 15,
        "question": "Which option correctly creates a docstring and comments out the print line?",
        "type": "mc",
        "options": [
            "DROPDOWN 1: Triple Single Quotes | DROPDOWN 2: Double Slash (//)",
            "DROPDOWN 1: Double Quotes | DROPDOWN 2: Hash (#)",
            "DROPDOWN 1: Triple Double Quotes | DROPDOWN 2: Hash (#)",
            "DROPDOWN 1: Triple Double Quotes | DROPDOWN 2: Double Slash (//)",
        ],
        "answer": "DROPDOWN 1: Triple Double Quotes | DROPDOWN 2: Hash (#)",
    },
    {
        "id": 16,
        "question": "Which method reads only the first line of a file?",
        "type": "mc",
        "options": ["read()", "readlines()", "readline()", "get_line(0)"],
        "answer": "readline()",
    },
    {
        "id": 17,
        "question": "Which is the correct syntax for raising a ValueError with a message?",
        "type": "mc",
        "options": [
            "exception ValueError('Custom error message')",
            "throw ValueError, 'Custom error message'",
            "raise ValueError('Custom error message')",
            "raise 'Custom error message' as ValueError",
        ],
        "answer": "raise ValueError('Custom error message')",
    },
    {
        "id": 18,
        "question": "Which character left-aligns formatted output in a field?",
        "type": "mc",
        "options": [
            "^ (The Caret)",
            "< (The Less-Than Sign)",
            "= (The Equal Sign)",
            "> (The Greater-Than Sign)",
        ],
        "answer": "< (The Less-Than Sign)",
    },
    {
        "id": 19,
        "question": "Match each visual output with the correct format specifier.",
        "type": "dropdown_sim",
        "code": None,
        "dropdowns": [
            {"label": "Value: Visual: 0000000042", "options": ["{0:10}", "{0:^10}", "{0:0<10}"], "answer": "{0:10}"},
            {"label": "Value: Visual: 4200000000", "options": ["{0:10}", "{0:^10}", "{0:0<10}"], "answer": "{0:0<10}"},
            {"label": "Value: Visual: 0000420000", "options": ["{0:10}", "{0:^10}", "{0:0<10}"], "answer": "{0:^10}"},
        ],
        "answer": ["{0:10}", "{0:0<10}", "{0:^10}"],
    },
    {
        "id": 20,
        "question": "What happens if outer_count += 1 is removed from the while loop?",
        "type": "mc",
        "options": [
            "The code produces an error because the 'for' loop cannot exit the 'while' loop.",
            "The 'while' loop executes only once, as Python automatically breaks loops without a counter.",
            "An infinite loop occurs, continuously printing the row header and the inner loop values.",
            "The code completes successfully but only prints the header for Row #1.",
        ],
        "answer": "An infinite loop occurs, continuously printing the row header and the inner loop values.",
    },
    {
        "id": 21,
        "question": """You are writing code that generates a random integer with a minimum value of 5 and a maximum value of 11.
Which two functions should you use? Each correct answer presents a complete solution. (Choose two.)""",
        "type": "mc_multi",
        "options": [
            "A. random.randint(5, 12)",
            "B. random.randint(5, 11)",
            "C. random.randrange(5, 12, 1)",
            "D. random.randrange(5, 11, 1)",
        ],
        "answer": [
            "B. random.randint(5, 11)",
            "C. random.randrange(5, 12, 1)",
        ],
    },
]

# =================================================
# CSS / LOOK
# =================================================
st.markdown(
    """
    <style>
    :root {
        --primary-color: #343a40;
        --secondary-color: #6c757d;
        --correct-color: #28a745;
        --incorrect-color: #dc3545;
        --background-color: #f8f9fa;
        --card-background: #ffffff;
    }

    .stApp {
        background-color: var(--background-color);
    }

    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .quiz-shell {
        background-color: var(--card-background);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        padding: 30px;
        margin: 20px 0;
    }

    .header-title {
        color: var(--primary-color);
        margin: 0;
        font-size: 1.8em;
        font-weight: 700;
    }

    .timer-box {
        font-size: 1.5em;
        font-weight: bold;
        color: var(--incorrect-color);
        text-align: right;
    }

    .status-bar {
        background-color: var(--secondary-color);
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 25px;
        font-size: 0.9em;
        text-align: center;
    }

    .question-box {
        margin-bottom: 20px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #f1f3f5;
    }

    .question-title {
        font-size: 1.2em;
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 15px;
    }

    .code-box {
        background-color: #e9ecef;
        padding: 10px;
        border-radius: 4px;
        overflow-x: auto;
        font-size: 0.9em;
        color: #495057;
        border-left: 3px solid #007bff;
        margin: 15px 0;
        white-space: pre-wrap;
        font-family: monospace;
    }

    .feedback-good {
        background-color: #d4edda;
        color: var(--correct-color);
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 10px;
    }

    .feedback-bad {
        background-color: #f8d7da;
        color: var(--incorrect-color);
        border: 1px solid #f5c6cb;
        padding: 15px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 10px;
    }

    .result-box {
        text-align: center;
        padding: 40px 20px;
        background-color: #e9ecef;
        border-radius: 8px;
        margin-top: 30px;
    }

    .teacher-box {
        margin-top: 20px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background-color: #f1f3f5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =================================================
# COOKIE SETUP
# =================================================
cookies = None
if COOKIE_MANAGER_AVAILABLE:
    try:
        cookies = EncryptedCookieManager(
            prefix="final_exam_",
            password=COOKIE_PASSWORD,
        )
        if not cookies.ready():
            st.stop()
    except Exception:
        cookies = None

# =================================================
# FIREBASE HELPERS
# =================================================
def now_utc():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def parse_service_account(raw_value):
    if not raw_value:
        return None
    if isinstance(raw_value, dict):
        return raw_value
    if isinstance(raw_value, str):
        cleaned = raw_value.strip()
        if cleaned.startswith("'''") and cleaned.endswith("'''"):
            cleaned = cleaned[3:-3].strip()
        elif cleaned.startswith('"""') and cleaned.endswith('"""'):
            cleaned = cleaned[3:-3].strip()
        return json.loads(cleaned)
    raise ValueError("FIREBASE_SERVICE_ACCOUNT_JSON must be a JSON string or dict.")


@st.cache_resource
def get_firestore_client():
    creds_dict = parse_service_account(FIREBASE_SERVICE_ACCOUNT_JSON)
    if not creds_dict:
        raise ValueError("Missing FIREBASE_SERVICE_ACCOUNT_JSON in secrets.")

    if not firebase_admin._apps:
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)

    return firestore.client()


def db():
    return get_firestore_client()


def get_teacher_emails():
    raw = str(TEACHER_EMAILS_RAW or "").strip()
    if not raw:
        return set()
    return {x.strip().lower() for x in raw.split(",") if x.strip()}


def firebase_sign_in_email_password(email: str, password: str):
    get_firestore_client()

    if not FIREBASE_WEB_API_KEY.strip():
        raise ValueError("Missing FIREBASE_WEB_API_KEY in secrets.")

    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={FIREBASE_WEB_API_KEY}"
    )
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }

    resp = requests.post(url, json=payload, timeout=20)
    data = resp.json()

    if resp.status_code != 200:
        err_msg = data.get("error", {}).get("message", "Authentication failed.")
        raise ValueError(err_msg)

    id_token = data.get("idToken", "")
    refresh_token = data.get("refreshToken", "")
    local_id = data.get("localId", "")

    if not id_token:
        raise ValueError("No Firebase ID token returned.")

    return {
        "id_token": id_token,
        "refresh_token": refresh_token,
        "local_id": local_id,
    }


def verify_firebase_id_token(id_token: str):
    get_firestore_client()
    return firebase_auth.verify_id_token(id_token)


def create_firebase_session_cookie(id_token: str, expires_days: int = 5):
    get_firestore_client()
    expires_in_seconds = expires_days * 24 * 60 * 60
    return firebase_auth.create_session_cookie(
        id_token,
        expires_in=expires_in_seconds
    )


def verify_firebase_session_cookie(session_cookie: str):
    get_firestore_client()
    return firebase_auth.verify_session_cookie(session_cookie, check_revoked=True)


def persist_auth_cookie(id_token: str):
    if cookies is None:
        return
    session_cookie = create_firebase_session_cookie(id_token, expires_days=5)
    cookies["firebase_session"] = session_cookie
    cookies.save()


def restore_auth_from_cookie():
    if cookies is None:
        return False

    session_cookie = cookies.get("firebase_session", "")
    if not session_cookie:
        return False

    try:
        decoded = verify_firebase_session_cookie(session_cookie)
        email = str(decoded.get("email", "")).strip().lower()
        teacher_emails = get_teacher_emails()

        st.session_state.auth_verified = True
        st.session_state.auth_user = {
            "uid": decoded.get("uid", ""),
            "email": email,
            "email_verified": bool(decoded.get("email_verified", False)),
            "is_teacher": email in teacher_emails,
        }
        st.session_state.is_teacher = email in teacher_emails
        return True
    except Exception:
        try:
            cookies["firebase_session"] = ""
            cookies.save()
        except Exception:
            pass
        return False

# =================================================
# DATA HELPERS
# =================================================
def get_student_profile(uid: str):
    if not uid:
        return None

    snap = db().collection(STUDENT_PROFILES_COLLECTION).document(uid).get()
    if not snap.exists:
        return None

    data = snap.to_dict() or {}
    if not data.get("active", True):
        return None

    data["uid"] = snap.id
    return data


def load_student_profiles():
    docs = db().collection(STUDENT_PROFILES_COLLECTION).stream()
    rows = []
    for doc in docs:
        data = doc.to_dict() or {}
        data["uid"] = doc.id
        rows.append(data)
    return rows


def create_student_account_and_profile(
    email: str,
    password: str,
    first_name: str,
    student_id: str,
    period: str,
    active: bool = True,
):
    get_firestore_client()

    email = email.strip().lower()
    first_name = first_name.strip()
    student_id = str(student_id).strip()
    period = period.strip()

    if not email:
        raise ValueError("Student email is required.")
    if not password or len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")
    if not first_name:
        raise ValueError("First name is required.")
    if not student_id.isdigit():
        raise ValueError("Student ID must be numeric.")
    if not period:
        raise ValueError("Period is required.")

    existing_profiles = db().collection(STUDENT_PROFILES_COLLECTION).where("student_id", "==", student_id).limit(1).stream()
    if any(True for _ in existing_profiles):
        raise ValueError(f"Student ID {student_id} already exists.")

    existing_email_profiles = db().collection(STUDENT_PROFILES_COLLECTION).where("email", "==", email).limit(1).stream()
    if any(True for _ in existing_email_profiles):
        raise ValueError(f"Email {email} already exists in student profiles.")

    user = firebase_auth.create_user(
        email=email,
        password=password,
        display_name=first_name,
    )
    uid = user.uid

    db().collection(STUDENT_PROFILES_COLLECTION).document(uid).set({
        "uid": uid,
        "email": email,
        "first_name": first_name,
        "student_id": student_id,
        "period": period,
        "display_name": f"{first_name}-{student_id}",
        "active": bool(active),
        "created_utc": now_utc(),
    })

    return {
        "uid": uid,
        "email": email,
        "display_name": f"{first_name}-{student_id}",
    }


def save_exam_result(student_profile: dict, score: int, total_questions: int, timed_out: bool):
    if not student_profile:
        raise ValueError("Missing student profile.")

    percentage = round((score / total_questions) * 100, 2) if total_questions else 0.0

    db().collection(RESULTS_COLLECTION).add({
        "uid": student_profile.get("uid", ""),
        "student_name": student_profile.get("first_name", ""),
        "student_id": student_profile.get("student_id", ""),
        "period": student_profile.get("period", ""),
        "email": student_profile.get("email", ""),
        "score": int(score),
        "total_questions": int(total_questions),
        "percentage": percentage,
        "timed_out": bool(timed_out),
        "submitted_utc": now_utc(),
        "quiz_title": "Python Final Exam",
    })


def load_exam_results():
    docs = (
        db()
        .collection(RESULTS_COLLECTION)
        .order_by("submitted_utc", direction=firestore.Query.DESCENDING)
        .stream()
    )
    rows = []
    for doc in docs:
        rows.append(doc.to_dict() or {})
    return rows


def load_my_exam_results(uid: str):
    docs = db().collection(RESULTS_COLLECTION).where("uid", "==", uid).stream()
    rows = [doc.to_dict() or {} for doc in docs]
    rows.sort(key=lambda x: x.get("submitted_utc", ""), reverse=True)
    return rows

# =================================================
# ATTEMPT PERSISTENCE
# =================================================
def attempt_ref(uid: str):
    return db().collection(EXAM_ATTEMPTS_COLLECTION).document(uid)


def load_exam_attempt(uid: str):
    snap = attempt_ref(uid).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data["uid"] = snap.id
    return data


def save_exam_attempt(uid: str, payload: dict):
    attempt_ref(uid).set(payload, merge=True)


def clear_exam_attempt(uid: str):
    try:
        attempt_ref(uid).delete()
    except Exception:
        pass

# =================================================
# SESSION STATE
# =================================================
def reset_exam_state():
    st.session_state.exam_started = False
    st.session_state.exam_finished = False
    st.session_state.started_at = None
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.question_order = []
    st.session_state.answers = {}
    st.session_state.feedback = None
    st.session_state.saved_result = False
    st.session_state.warning_shown = False


def sign_out():
    st.session_state.auth_verified = False
    st.session_state.auth_user = None
    st.session_state.is_teacher = False
    st.session_state.student_profile = None
    reset_exam_state()

    if cookies is not None:
        try:
            cookies["firebase_session"] = ""
            cookies.save()
        except Exception:
            pass


st.session_state.setdefault("auth_verified", False)
st.session_state.setdefault("auth_user", None)
st.session_state.setdefault("is_teacher", False)
st.session_state.setdefault("student_profile", None)

st.session_state.setdefault("exam_started", False)
st.session_state.setdefault("exam_finished", False)
st.session_state.setdefault("started_at", None)
st.session_state.setdefault("current_question_index", 0)
st.session_state.setdefault("score", 0)
st.session_state.setdefault("question_order", [])
st.session_state.setdefault("answers", {})
st.session_state.setdefault("feedback", None)
st.session_state.setdefault("saved_result", False)
st.session_state.setdefault("warning_shown", False)

if not st.session_state.auth_verified:
    restore_auth_from_cookie()

# =================================================
# AUTH SIDEBAR
# =================================================
with st.sidebar:
    st.header("Firebase Sign In")

    if cookies is None:
        st.caption("Persistent cookies unavailable. Login will work for the current session only.")

    if not st.session_state.auth_verified:
        with st.form("firebase_login_form"):
            login_email = st.text_input("Email")
            login_password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")

        if login_submit:
            try:
                sign_in_result = firebase_sign_in_email_password(
                    login_email.strip(),
                    login_password
                )
                decoded = verify_firebase_id_token(sign_in_result["id_token"])

                email = str(decoded.get("email", "")).strip().lower()
                teacher_emails = get_teacher_emails()

                st.session_state.auth_verified = True
                st.session_state.auth_user = {
                    "uid": decoded.get("uid", ""),
                    "email": email,
                    "email_verified": bool(decoded.get("email_verified", False)),
                    "is_teacher": email in teacher_emails,
                }
                st.session_state.is_teacher = email in teacher_emails

                persist_auth_cookie(sign_in_result["id_token"])
                st.success("Signed in successfully.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

        st.stop()

    auth_user = st.session_state.auth_user or {}
    st.success(f"Signed in as: {auth_user.get('email', 'unknown')}")
    st.caption("Teacher" if auth_user.get("is_teacher") else "Student")

    if st.button("Sign Out"):
        sign_out()
        st.rerun()

# =================================================
# LOAD STUDENT PROFILE / RESTORE ATTEMPT
# =================================================
auth_user = st.session_state.auth_user or {}
auth_uid = str(auth_user.get("uid", "")).strip()
is_teacher_user = bool(auth_user.get("is_teacher", False))

if not is_teacher_user:
    profile = get_student_profile(auth_uid)
    if not profile:
        st.error("No active student profile found for this account.")
        st.stop()
    st.session_state.student_profile = profile

    # restore persisted attempt on login/refresh
    existing_attempt = load_exam_attempt(auth_uid)
    if existing_attempt:
        st.session_state.exam_started = not bool(existing_attempt.get("finished", False))
        st.session_state.exam_finished = bool(existing_attempt.get("finished", False))
        st.session_state.started_at = existing_attempt.get("started_at_epoch")
        st.session_state.current_question_index = int(existing_attempt.get("current_question_index", 0))
        st.session_state.score = int(existing_attempt.get("score", 0))
        st.session_state.question_order = existing_attempt.get("question_order", [])
        st.session_state.answers = existing_attempt.get("answers", {}) or {}
        st.session_state.saved_result = bool(existing_attempt.get("saved_result", False))
        st.session_state.warning_shown = bool(existing_attempt.get("warning_shown", False))
        st.session_state.feedback = None

# =================================================
# HELPERS
# =================================================
def start_exam():
    order = list(range(len(QUIZ_QUESTIONS)))
    random.shuffle(order)
    st.session_state.question_order = order
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.feedback = None
    st.session_state.exam_started = True
    st.session_state.exam_finished = False
    st.session_state.saved_result = False
    st.session_state.warning_shown = False
    st.session_state.started_at = time.time()

    save_exam_attempt(auth_uid, {
        "uid": auth_uid,
        "started_utc": now_utc(),
        "started_at_epoch": st.session_state.started_at,
        "question_order": st.session_state.question_order,
        "current_question_index": 0,
        "score": 0,
        "answers": {},
        "finished": False,
        "saved_result": False,
        "warning_shown": False,
    })


def finish_exam(timed_out: bool = False):
    st.session_state.exam_started = False
    st.session_state.exam_finished = True

    if not st.session_state.saved_result and st.session_state.student_profile:
        save_exam_result(
            st.session_state.student_profile,
            st.session_state.score,
            len(QUIZ_QUESTIONS),
            timed_out,
        )
        st.session_state.saved_result = True

    save_exam_attempt(auth_uid, {
        "finished": True,
        "saved_result": True,
        "timed_out": bool(timed_out),
        "score": st.session_state.score,
        "current_question_index": st.session_state.current_question_index,
        "answers": st.session_state.answers,
        "warning_shown": st.session_state.warning_shown,
    })


def get_remaining_seconds():
    if not st.session_state.started_at:
        return QUIZ_DURATION_MINUTES * 60
    elapsed = int(time.time() - float(st.session_state.started_at))
    remaining = (QUIZ_DURATION_MINUTES * 60) - elapsed
    return max(0, remaining)


def render_js_timer():
    remaining = get_remaining_seconds()

    if remaining <= WARNING_MINUTES * 60 and not st.session_state.warning_shown and st.session_state.exam_started:
        st.session_state.warning_shown = True
        save_exam_attempt(auth_uid, {"warning_shown": True})

    html = f"""
    <div id="timer-root" style="
        font-size: 1.5em;
        font-weight: bold;
        color: #dc3545;
        text-align: right;
    ">00:00</div>

    <script>
    let remaining = {remaining};
    const root = document.getElementById("timer-root");

    function formatTime(total) {{
        const minutes = Math.floor(total / 60);
        const seconds = total % 60;
        return String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
    }}

    function tick() {{
        root.textContent = formatTime(Math.max(remaining, 0));
        if (remaining > 0) {{
            remaining -= 1;
            setTimeout(tick, 1000);
        }} else {{
            root.textContent = "00:00";
        }}
    }}

    tick();
    </script>
    """
    components.html(html, height=40)


def current_question():
    idx = st.session_state.current_question_index
    q_index = st.session_state.question_order[idx]
    return QUIZ_QUESTIONS[q_index]


def check_current_answer(question):
    qid = question["id"]

    if question["type"] == "mc":
        user_answer = st.session_state.get(f"q_{qid}_radio")
        if not user_answer:
            return None, "Please select an answer."
        is_correct = user_answer == question["answer"]
        return is_correct, user_answer

    if question["type"] == "mc_multi":
        selected = []
        for i, option in enumerate(question["options"]):
            if st.session_state.get(f"q_{qid}_check_{i}", False):
                selected.append(option)

        if not selected:
            return None, "Please select at least one answer."

        correct_answers = question["answer"]
        is_correct = len(selected) == len(correct_answers) and all(ans in selected for ans in correct_answers)
        return is_correct, selected

    if question["type"] == "sequencing":
        user_order = []
        used = set()
        for i in range(len(question["options"])):
            value = st.session_state.get(f"q_{qid}_order_{i}")
            if not value:
                return None, "Please complete all order positions."
            user_order.append(value)
            used.add(value)

        if len(used) != len(question["options"]):
            return None, "Each item can only be used once."

        is_correct = user_order == question["answer"]
        return is_correct, user_order

    if question["type"] == "dropdown_sim":
        selections = []
        for i, dd in enumerate(question["dropdowns"]):
            value = st.session_state.get(f"q_{qid}_dd_{i}")
            if not value:
                return None, "Please complete all dropdowns."
            selections.append(value)

        is_correct = selections == question["answer"]
        return is_correct, selections

    return None, "Unsupported question type."


def submit_answer():
    question = current_question()
    result, payload = check_current_answer(question)

    if result is None:
        st.session_state.feedback = {
            "type": "missing",
            "message": payload,
        }
        return

    if result:
        st.session_state.score += 1
        st.session_state.feedback = {
            "type": "correct",
            "message": "✅ Correct! Well done.",
        }
    else:
        if question["type"] == "mc":
            msg = f"❌ Incorrect. The correct answer was: {question['answer']}"
        else:
            msg = f"❌ Incorrect. The correct answer(s) were: {question['answer']}"
        st.session_state.feedback = {
            "type": "incorrect",
            "message": msg,
        }

    st.session_state.answers[str(question["id"])] = {
        "submitted": True,
        "correct": bool(result),
    }

    save_exam_attempt(auth_uid, {
        "score": st.session_state.score,
        "answers": st.session_state.answers,
        "current_question_index": st.session_state.current_question_index,
        "warning_shown": st.session_state.warning_shown,
        "finished": False,
    })


def next_question():
    if st.session_state.current_question_index >= len(QUIZ_QUESTIONS) - 1:
        finish_exam(timed_out=False)
    else:
        st.session_state.current_question_index += 1
        st.session_state.feedback = None
        save_exam_attempt(auth_uid, {
            "current_question_index": st.session_state.current_question_index,
            "score": st.session_state.score,
            "answers": st.session_state.answers,
            "warning_shown": st.session_state.warning_shown,
            "finished": False,
        })

# =================================================
# MAIN LAYOUT
# =================================================
st.markdown('<div class="quiz-shell">', unsafe_allow_html=True)

if is_teacher_user:
    left_col, right_col = st.columns([3, 1])
    with left_col:
        st.markdown('<div class="header-title">Python Final Exam - Teacher Dashboard</div>', unsafe_allow_html=True)
    with right_col:
        st.markdown('<div class="timer-box">Teacher</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="status-bar">Teacher access enabled. Create student accounts and review final exam scores.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="teacher-box">', unsafe_allow_html=True)
    st.subheader("Create Student Login")

    with st.form("create_student_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_student_email = st.text_input("Student Email")
            new_student_password = st.text_input("Temporary Password", type="password")
            new_first_name = st.text_input("First Name")
        with c2:
            new_student_id = st.text_input("Student ID")
            new_period = st.selectbox("Class / Period", PERIOD_OPTIONS)
            new_active = st.checkbox("Active", value=True)

        create_submit = st.form_submit_button("Create Student Account")

    if create_submit:
        try:
            create_student_account_and_profile(
                email=new_student_email,
                password=new_student_password,
                first_name=new_first_name,
                student_id=new_student_id,
                period=new_period,
                active=new_active,
            )
            st.success("Student account created successfully.")
        except Exception as e:
            st.error(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="teacher-box">', unsafe_allow_html=True)
    st.subheader("Student Profiles")
    try:
        profiles = load_student_profiles()
        if profiles:
            rows = []
            for p in sorted(profiles, key=lambda x: (str(x.get("period", "")), str(x.get("first_name", "")))):
                rows.append({
                    "First Name": p.get("first_name", ""),
                    "Student ID": p.get("student_id", ""),
                    "Period": p.get("period", ""),
                    "Email": p.get("email", ""),
                    "Active": bool(p.get("active", True)),
                })
            st.dataframe(rows, use_container_width=True, height=260)
        else:
            st.info("No student profiles found.")
    except Exception as e:
        st.error(str(e))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="teacher-box">', unsafe_allow_html=True)
    st.subheader("Saved Final Exam Scores")
    try:
        results = load_exam_results()
        if results:
            rows = []
            for r in results:
                rows.append({
                    "Student Name": r.get("student_name", ""),
                    "Student ID": r.get("student_id", ""),
                    "Period": r.get("period", ""),
                    "Score": r.get("score", 0),
                    "Total": r.get("total_questions", 0),
                    "Percentage": r.get("percentage", 0),
                    "Submitted UTC": r.get("submitted_utc", ""),
                    "Timed Out": r.get("timed_out", False),
                })
            st.dataframe(rows, use_container_width=True, height=320)
        else:
            st.info("No exam results saved yet.")
    except Exception as e:
        st.error(str(e))
    st.markdown("</div>", unsafe_allow_html=True)

else:
    student_profile = st.session_state.student_profile

    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown('<div class="header-title">Python Final Exam</div>', unsafe_allow_html=True)
    with header_right:
        if st.session_state.exam_started:
            render_js_timer()
        else:
            st.markdown(
                f'<div class="timer-box">{QUIZ_DURATION_MINUTES:02d}:00</div>',
                unsafe_allow_html=True,
            )

    # force timeout check on every rerun
    if st.session_state.exam_started and get_remaining_seconds() <= 0:
        finish_exam(timed_out=True)
        st.rerun()

    if not st.session_state.exam_started and not st.session_state.exam_finished:
        st.markdown(
            f'<div class="status-bar">{student_profile.get("first_name", "")} | ID: {student_profile.get("student_id", "")} | {student_profile.get("period", "")}</div>',
            unsafe_allow_html=True,
        )

        try:
            my_results = load_my_exam_results(auth_uid)
            if my_results:
                latest = my_results[0]
                st.info(
                    f"Previous saved score: {latest.get('score', 0)} / {latest.get('total_questions', 0)} "
                    f"({latest.get('percentage', 0)}%)"
                )
        except Exception:
            pass

        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown('<div class="question-title">Final Exam Instructions</div>', unsafe_allow_html=True)
        st.write("You will answer one question at a time.")
        st.write(f"You have **{QUIZ_DURATION_MINUTES} minutes** to complete the exam.")
        st.write("If you refresh or close the browser, the timer keeps running.")
        st.write("Your score will be saved automatically when you finish or when time runs out.")

        st.error("⚠️ FINAL EXAM WARNING: Read each question carefully. After you submit an answer, you cannot go back and change it.")

        if st.button("Start Final Exam", use_container_width=True):
            start_exam()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.exam_started and not st.session_state.exam_finished:
        if st.session_state.warning_shown:
            st.warning("⏱️ Only 5 minutes remain in the exam.")

        st.markdown(
            f'<div class="status-bar">Question {st.session_state.current_question_index + 1} of {len(QUIZ_QUESTIONS)} | Score: {st.session_state.score}</div>',
            unsafe_allow_html=True,
        )

        question = current_question()
        qid = question["id"]

        st.markdown('<div class="question-box">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="question-title">Q{st.session_state.current_question_index + 1}. {question["question"]}</div>',
            unsafe_allow_html=True
        )

        if question["type"] == "mc":
            st.radio(
                "Select one answer",
                question["options"],
                key=f"q_{qid}_radio",
                index=None,
                label_visibility="collapsed",
            )

        elif question["type"] == "mc_multi":
            st.write("Select two answers:")
            for i, option in enumerate(question["options"]):
                st.checkbox(option, key=f"q_{qid}_check_{i}")

        elif question["type"] == "sequencing":
            st.markdown(
                '<div class="code-box">Arrange from top to bottom by selecting one item for each position.</div>',
                unsafe_allow_html=True
            )
            options = [""] + question["options"]
            for i in range(len(question["options"])):
                st.selectbox(
                    f"Position {i + 1}",
                    options,
                    key=f"q_{qid}_order_{i}",
                )

        elif question["type"] == "dropdown_sim":
            if question.get("code"):
                st.markdown(f'<div class="code-box">{question["code"]}</div>', unsafe_allow_html=True)

            for i, dd in enumerate(question["dropdowns"]):
                st.selectbox(
                    dd["label"],
                    [""] + dd["options"],
                    key=f"q_{qid}_dd_{i}",
                )

        feedback = st.session_state.feedback
        answered_this_question = str(question["id"]) in st.session_state.answers

        if feedback:
            if feedback["type"] == "correct":
                st.markdown(f'<div class="feedback-good">{feedback["message"]}</div>', unsafe_allow_html=True)
            elif feedback["type"] == "incorrect":
                st.markdown(f'<div class="feedback-bad">{feedback["message"]}</div>', unsafe_allow_html=True)
            elif feedback["type"] == "missing":
                st.warning(feedback["message"])

        if not answered_this_question:
            if st.button("Submit Answer", use_container_width=True):
                submit_answer()
                st.rerun()
        else:
            button_text = "View Results" if st.session_state.current_question_index == len(QUIZ_QUESTIONS) - 1 else "Continue to Next Question"
            if st.button(button_text, use_container_width=True):
                next_question()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.exam_finished:
        percentage = round((st.session_state.score / len(QUIZ_QUESTIONS)) * 100, 2) if QUIZ_QUESTIONS else 0.0

        if percentage == 100:
            message = "🎉 Perfect score!"
        elif percentage >= 70:
            message = "👍 Great job!"
        else:
            message = "📚 Exam complete."

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("<h2>Exam Finished!</h2>", unsafe_allow_html=True)
        st.write(f"Your final score is: **{st.session_state.score}** out of **{len(QUIZ_QUESTIONS)}**.")
        st.write(f"Percentage: **{percentage}%**")
        st.write(message)

        try:
            my_results = load_my_exam_results(auth_uid)
            if my_results:
                latest = my_results[0]
                st.write(f"Saved score record: **{latest.get('score', 0)} / {latest.get('total_questions', 0)}**")
        except Exception:
            pass

        if st.button("Start New Exam", use_container_width=True):
            clear_exam_attempt(auth_uid)
            reset_exam_state()
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
