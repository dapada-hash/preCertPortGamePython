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

QUIZ_DURATION_MINUTES = 23
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
        "question": "Which character left-aligns formatted output in a field?",  # <-- KEY TYPO FIXED HERE
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
        "question": "Match each strftime format code with its correct output.",
        "type": "dropdown_sim",
        "code": """from datetime import datetime
d = datetime(2026, 3, 23)""",
        "dropdowns": [
            {"label": 'strftime("%A")', "options": ["Monday", "March", "20"], "answer": "Monday"},
            {"label": 'strftime("%B")', "options": ["Monday", "March", "20"], "answer": "March"},
            {"label": 'strftime("%C")', "options": ["20", "03", "2026"], "answer": "20"}
        ],
        "answer": ["Monday", "March", "20"],
    },
    {
        "id": 22,
        "question": """What is the output of the following Python code?

from datetime import datetime
d = datetime(2026, 3, 23)
result = d.strftime("%A")
print(result)""",
        "type": "mc",
        "options": ["A. Monday", "B. 03", "C. March", "D. 26"],
        "answer": "A. Monday",
    },
    {
        "id": 23,
        "question": """What is the output of the following Python code?

name = "Alex"
score = 85
result = f"{name} scored {score}%"
print(result)""",
        "type": "mc",
        "options": ["A. Alex scored 85%", "B. Alex scored score%", "C. name scored 85%", "D. Alex scored 85"],
        "answer": "A. Alex scored 85%",
    },
    {
        "id": 24,
        "question": "Complete the Python string formatting to display the number with two decimal places.",
        "type": "dropdown_sim",
        "code": """value = 3.14159
formatted = f"{value:[DROPDOWN]}"
print(formatted)""",
        "dropdowns": [
            {
                "label": "Format specifier",
                "options": [".2f", ".2d", ".2s", ".2%"],
                "answer": ".2f",
            }
        ],
        "answer": [".2f"],
    },
    {
        "id": 25,
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

    requests_resp = requests.post(url, json=payload, timeout=20)
    data = requests_resp.json()

    if requests_resp.status_code != 200:
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
# FIRESTORE DATA LAYERS
# =================================================
def load_student_profiles():
    try:
        docs = db().collection(STUDENT_PROFILES_COLLECTION).stream()
        res = []
        for d in docs:
            v = d.to_dict()
            v["id"] = d.id
            res.append(v)
        return sorted(res, key=lambda x: (x.get("period", ""), x.get("last_name", ""), x.get("first_name", "")))
    except Exception as e:
        st.error(f"Error fetching student profiles: {e}")
        return []


def upsert_student_profile(student_id: str, last_name: str, first_name: str, period: str):
    try:
        doc_ref = db().collection(STUDENT_PROFILES_COLLECTION).document(student_id)
        doc_ref.set({
            "student_id": student_id,
            "last_name": last_name,
            "first_name": first_name,
            "period": period,
            "updated_at": now_utc(),
        }, merge=True)
        return True
    except Exception as e:
        st.error(f"Error writing profile record: {e}")
        return False


def load_all_exam_results():
    try:
        docs = db().collection(RESULTS_COLLECTION).stream()
        res = []
        for d in docs:
            v = d.to_dict()
            v["id"] = d.id
            res.append(v)
        return sorted(res, key=lambda x: x.get("submitted_at", ""), reverse=True)
    except Exception as e:
        st.error(f"Error reading class results: {e}")
        return []


def load_my_exam_results(auth_uid: str):
    try:
        docs = (
            db()
            .collection(RESULTS_COLLECTION)
            .where("auth_uid", "==", auth_uid)
            .stream()
        )
        res = []
        for d in docs:
            v = d.to_dict()
            v["id"] = d.id
            res.append(v)
        return sorted(res, key=lambda x: x.get("submitted_at", ""), reverse=True)
    except Exception:
        return []


def load_exam_attempt(auth_uid: str):
    try:
        doc = db().collection(EXAM_ATTEMPTS_COLLECTION).document(auth_uid).get()
        if doc.exists:
            return doc.to_dict()
    except Exception:
        pass
    return None


def save_exam_attempt(auth_uid: str, attempt_data: dict):
    try:
        db().collection(EXAM_ATTEMPTS_COLLECTION).document(auth_uid).set(attempt_data)
    except Exception as e:
        st.error(f"Error persisting session branch to database: {e}")


def clear_exam_attempt(auth_uid: str):
    try:
        db().collection(EXAM_ATTEMPTS_COLLECTION).document(auth_uid).delete()
    except Exception:
        pass


def save_final_exam_result(auth_uid: str, student_profile: dict, score: int, total: int, timed_out=False):
    try:
        percentage = round((score / total) * 100, 2) if total > 0 else 0.0
        doc_id = f"{auth_uid}_{int(time.time())}"
        payload = {
            "auth_uid": auth_uid,
            "student_id": student_profile.get("student_id", "UNKNOWN"),
            "first_name": student_profile.get("first_name", ""),
            "last_name": student_profile.get("last_name", ""),
            "period": student_profile.get("period", ""),
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "timed_out": timed_out,
            "submitted_at": now_utc(),
        }
        db().collection(RESULTS_COLLECTION).document(doc_id).set(payload)
        return True
    except Exception as e:
        st.error(f"Critical submission failure: {e}")
        return False


def get_student_profile_by_email(email: str):
    try:
        clean_email = email.strip().lower()
        if "@" not in clean_email:
            return None
        parts = clean_email.split("@")[0].split(".")
        if len(parts) >= 2:
            f_candidate = parts[0]
            l_candidate = parts[1]
        else:
            f_candidate = parts[0]
            l_candidate = ""

        docs = db().collection(STUDENT_PROFILES_COLLECTION).stream()
        for d in docs:
            v = d.to_dict()
            sid = str(v.get("student_id", "")).strip()
            fname = str(v.get("first_name", "")).strip().lower()
            lname = str(v.get("last_name", "")).strip().lower()

            if sid and clean_email.startswith(sid.lower()):
                return v
            if fname and lname and (fname in clean_email) and (lname in clean_email):
                return v
            if fname and f_candidate == fname:
                return v
    except Exception:
        pass
    return None

# =================================================
# APPLICATION STATE LIFECYCLE
# =================================================
def init_session_states():
    if "auth_verified" not in st.session_state:
        st.session_state.auth_verified = False
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "is_teacher" not in st.session_state:
        st.session_state.is_teacher = False
    if "student_profile" not in st.session_state:
        st.session_state.student_profile = None

    if "exam_started" not in st.session_state:
        st.session_state.exam_started = False
    if "exam_finished" not in st.session_state:
        st.session_state.exam_finished = False
    if "timed_out" not in st.session_state:
        st.session_state.timed_out = False
    if "start_time_epoch" not in st.session_state:
        st.session_state.start_time_epoch = 0.0
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "warning_shown" not in st.session_state:
        st.session_state.warning_shown = False


def reset_exam_state():
    st.session_state.exam_started = False
    st.session_state.exam_finished = False
    st.session_state.timed_out = False
    st.session_state.start_time_epoch = 0.0
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.feedback = None
    st.session_state.warning_shown = False


def pull_and_sync_session_attempt(auth_uid: str):
    attempt = load_exam_attempt(auth_uid)
    if attempt:
        st.session_state.exam_started = attempt.get("exam_started", False)
        st.session_state.exam_finished = attempt.get("exam_finished", False)
        st.session_state.timed_out = attempt.get("timed_out", False)
        st.session_state.start_time_epoch = float(attempt.get("start_time_epoch", 0.0))
        st.session_state.current_question_index = int(attempt.get("current_question_index", 0))
        st.session_state.score = int(attempt.get("score", 0))
        st.session_state.answers = attempt.get("answers", {})
        st.session_state.feedback = attempt.get("feedback", None)
        st.session_state.warning_shown = attempt.get("warning_shown", False)
        return True
    return False


def push_session_attempt_to_cloud(auth_uid: str):
    if not st.session_state.exam_started:
        return
    payload = {
        "exam_started": st.session_state.exam_started,
        "exam_finished": st.session_state.exam_finished,
        "timed_out": st.session_state.timed_out,
        "start_time_epoch": st.session_state.start_time_epoch,
        "current_question_index": st.session_state.current_question_index,
        "score": st.session_state.score,
        "answers": st.session_state.answers,
        "feedback": st.session_state.feedback,
        "warning_shown": st.session_state.warning_shown,
        "last_updated_at": now_utc(),
    }
    save_exam_attempt(auth_uid, payload)


def get_remaining_seconds():
    if not st.session_state.exam_started or st.session_state.start_time_epoch == 0:
        return QUIZ_DURATION_MINUTES * 60
    elapsed = time.time() - st.session_state.start_time_epoch
    total_allowed = QUIZ_DURATION_MINUTES * 60
    return max(0.0, total_allowed - elapsed)

# =================================================
# CLIENT ASYNC TIMER BRIDGE
# =================================================
def render_js_timer():
    rem_sec = int(get_remaining_seconds())
    if rem_sec <= 0:
        return

    html_code = f"""
    <div id="timer-display" style="font-size: 1.5em; font-weight: bold; color: #dc3545; text-align: right; font-family: sans-serif;">
        00:00
    </div>
    <script>
        var remainingSeconds = {rem_sec};
        var displayEl = document.getElementById("timer-display");

        function updateDisplay() {{
            if (remainingSeconds <= 0) {{
                displayEl.innerHTML = "00:00";
                clearInterval(intervalId);
                setTimeout(function() {{ window.parent.location.reload(); }}, 500);
                return;
            }}
            var mins = Math.floor(remainingSeconds / 60);
            var secs = remainingSeconds % 60;
            var formatMins = mins < 10 ? "0" + mins : mins;
            var formatSecs = secs < 10 ? "0" + secs : secs;
            displayEl.innerHTML = formatMins + ":" + formatSecs;
            remainingSeconds--;
        }}

        updateDisplay();
        var intervalId = setInterval(updateDisplay, 1000);
    </script>
    """
    components.html(html_code, height=45)

# =================================================
# ENGINE LOGIC CORE
# =================================================
def current_question():
    idx = st.session_state.current_question_index
    if 0 <= idx < len(QUIZ_QUESTIONS):
        return QUIZ_QUESTIONS[idx]
    return None


def start_exam():
    st.session_state.exam_started = True
    st.session_state.exam_finished = False
    st.session_state.timed_out = False
    st.session_state.start_time_epoch = time.time()
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.feedback = None
    st.session_state.warning_shown = False
    push_session_attempt_to_cloud(st.session_state.auth_user["uid"])


def finish_exam(timed_out=False):
    st.session_state.exam_started = False
    st.session_state.exam_finished = True
    st.session_state.timed_out = timed_out
    st.session_state.feedback = None

    uid = st.session_state.auth_user["uid"]
    prof = st.session_state.student_profile or {"first_name": "Unknown", "last_name": "Student"}

    save_final_exam_result(
        auth_uid=uid,
        student_profile=prof,
        score=st.session_state.score,
        total=len(QUIZ_QUESTIONS),
        timed_out=timed_out,
    )
    clear_exam_attempt(uid)


def submit_answer():
    q = current_question()
    if not q:
        return

    qid = str(q["id"])
    user_ans = None
    is_correct = False

    if q["type"] == "mc":
        user_ans = st.session_state.get(f"q_{q['id']}_radio")
        if not user_ans:
            st.session_state.feedback = {"type": "missing", "message": "Please select an answer before submitting."}
            return
        is_correct = (user_ans == q["answer"])

    elif q["type"] == "mc_multi":
        selected = []
        for i, opt in enumerate(q["options"]):
            if st.session_state.get(f"q_{q['id']}_check_{i}"):
                selected.append(opt)
        if len(selected) != 2:
            st.session_state.feedback = {"type": "missing", "message": "Please select exactly two answers before submitting."}
            return
        user_ans = selected
        is_correct = (set(selected) == set(q["answer"]))

    elif q["type"] == "sequencing":
        ans_list = []
        missing = False
        for i in range(len(q["options"])):
            val = st.session_state.get(f"q_{q['id']}_order_{i}", "")
            if not val:
                missing = True
            ans_list.append(val)
        if missing:
            st.session_state.feedback = {"type": "missing", "message": "Please assign an item to every sequencing slot."}
            return
        user_ans = ans_list
        is_correct = (ans_list == q["answer"])

    elif q["type"] == "dropdown_sim":
        ans_list = []
        missing = False
        for i in range(len(q["dropdowns"])):
            val = st.session_state.get(f"q_{q['id']}_dd_{i}", "")
            if not val:
                missing = True
            ans_list.append(val)
        if missing:
            st.session_state.feedback = {"type": "missing", "message": "Please select an option for all code matrix fields."}
            return
        user_ans = ans_list
        is_correct = (ans_list == q["answer"])

    if is_correct:
        st.session_state.score += 1
        st.session_state.feedback = {"type": "correct", "message": "🎯 Correct answer saved!"}
    else:
        st.session_state.feedback = {"type": "incorrect", "message": "❌ Answer recorded."}

    st.session_state.answers[qid] = user_ans
    push_session_attempt_to_cloud(st.session_state.auth_user["uid"])


def next_question():
    st.session_state.feedback = None
    if st.session_state.current_question_index >= len(QUIZ_QUESTIONS) - 1:
        finish_exam(timed_out=False)
    else:
        st.session_state.current_question_index += 1
        push_session_attempt_to_cloud(st.session_state.auth_user["uid"])

# =================================================
# MAIN RENDER ENTRYWAY
# =================================================
init_session_states()
restore_auth_from_cookie()

st.title("🐍 Advanced Programming Portal")

if not st.session_state.auth_verified:
    st.subheader("Final Exam Portal Login")
    tab1, tab2 = st.tabs(["Sign In", "Create Student Profile"])

    with tab1:
        with st.form("login_form"):
            email_input = st.text_input("School Email").strip()
            pass_input = st.text_input("Access Password", type="password")
            btn = st.form_submit_button("Authenticate Access", use_container_width=True)

            if btn:
                if not email_input or not pass_input:
                    st.error("Please provide both email and password credentials.")
                else:
                    try:
                        res = firebase_sign_in_email_password(email_input, pass_input)
                        persist_auth_cookie(res["id_token"])
                        st.success("Authorization verified! Syncing environment...")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Login Rejected: {ex}")

    with tab2:
        st.markdown("If you do not have an active database profile ID, create one here.")
        with st.form("register_profile_form"):
            reg_id = st.text_input("Student ID Number (e.g., 100123)").strip()
            reg_first = st.text_input("First Name").strip()
            reg_last = st.text_input("Last Name").strip()
            reg_period = st.selectbox("Class Period Assignment", PERIOD_OPTIONS)
            reg_btn = st.form_submit_button("Register New Student Profile", use_container_width=True)

            if reg_btn:
                if not reg_id or not reg_first or not reg_last:
                    st.error("All identification form values are explicitly mandatory.")
                else:
                    if upsert_student_profile(reg_id, reg_last, reg_first, reg_period):
                        st.success(f"Profile saved! Student ID '{reg_id}' is authorized. Switch tabs to login.")
    st.stop()

# =================================================
# AUTHENTICATED SYSTEM DASHBOARDS
# =================================================
auth_user = st.session_state.auth_user
auth_uid = auth_user["uid"]
user_email = auth_user["email"]

if not st.session_state.is_teacher and st.session_state.student_profile is None:
    st.session_state.student_profile = get_student_profile_by_email(user_email) or {
        "student_id": "STU-" + auth_uid[:6].upper(),
        "first_name": user_email.split("@")[0],
        "last_name": "Profile",
        "period": "Unassigned"
    }

if st.session_state.exam_started and not st.session_state.answers:
    pull_and_sync_session_attempt(auth_uid)

legacy_timeout_check = False
if st.session_state.exam_started and get_remaining_seconds() <= 0:
    legacy_timeout_check = True

col_user, col_logout = st.columns([3, 1])
with col_user:
    st.markdown(f"**Account Active:** `{user_email}`")
with col_logout:
    if st.button("Log Out System", use_container_width=True):
        if cookies is not None:
            cookies["firebase_session"] = ""
            cookies.save()
        st.session_state.auth_verified = False
        st.session_state.auth_user = None
        reset_exam_state()
        st.rerun()

# --- TEACHER VIEW ---
if st.session_state.is_teacher:
    st.markdown("---")
    st.subheader("🛠️ Administrative Instructor Dashboard")
    t_tabs = st.tabs(["Database Records Grid", "Active Exam Logs", "Roster Management Form"])

    with t_tabs[0]:
        st.markdown("### Final Evaluated Submissions Table")
        all_results = load_all_exam_results()
        if all_results:
            st.dataframe(all_results, use_container_width=True)
        else:
            st.info("No completed final exams stored inside collection yet.")

    with t_tabs[1]:
        st.markdown("### Profile Verification Grid")
        profiles = load_student_profiles()
        if profiles:
            st.dataframe(profiles, use_container_width=True)
        else:
            st.info("No valid profile nodes stored inside database instance collections.")

    with t_tabs[2]:
        st.markdown("### Manual Student Registry Updates")
        with st.form("manual_teacher_upsert"):
            m_id = st.text_input("Target Student ID").strip()
            m_first = st.text_input("First Name").strip()
            m_last = st.text_input("Last Name").strip()
            m_period = st.selectbox("Assigned Period Loop", PERIOD_OPTIONS)
            m_btn = st.form_submit_button("Commit Profile Record", use_container_width=True)
            if m_btn:
                if m_id and m_first and m_last:
                    if upsert_student_profile(m_id, m_last, m_first, m_period):
                        st.success(f"Profile {m_id} processed cleanly.")
                        st.rerun()
                else:
                    st.error("Please fill all configuration elements.")

# --- STUDENT VIEW ---
else:
    st.markdown('<div class="quiz-shell">', unsafe_allow_html=True)
    student_profile = st.session_state.student_profile

    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown('<div class="header-title">Python Final Exam</div>', unsafe_allow_html=True)
    with header_right:
        if st.session_state.exam_started and not st.session_state.exam_finished:
            render_js_timer()
        elif st.session_state.exam_finished:
            st.markdown('<div class="timer-box" style="color: #6c757d;">Closed</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="timer-box">{QUIZ_DURATION_MINUTES:02d}:00</div>', unsafe_allow_html=True)

    # 1. CRITICAL PRIORITIZED TIMEOUT HANDLING LAYER
    if legacy_timeout_check or (st.session_state.exam_started and get_remaining_seconds() <= 0):
        finish_exam(timed_out=True)
        st.session_state.exam_finished = True  # Explicitly assert state consistency
        st.rerun()  

    # 2. EXAM EVALUATION COMPLETE SCREEN (AIRTIGHT ROUTING PRIORITY #1)
    if st.session_state.exam_finished:
        percentage = round((st.session_state.score / len(QUIZ_QUESTIONS)) * 100, 2) if QUIZ_QUESTIONS else 0.0

        if percentage == 100:
            message = "🎉 Perfect score! Masterful job!"
        elif percentage >= 82:
            message = "👍 Excellent work! You have passed the certification standard threshold!"
        else:
            message = "📚 Evaluation complete. You did not meet the passing standard threshold."

        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.markdown("<h2>Exam Evaluation Complete</h2>", unsafe_allow_html=True)

        st.write(f"Your calculated score: **{st.session_state.score}** / **{len(QUIZ_QUESTIONS)}**")
        st.write(f"Final Percentage: **{percentage}%**")
        st.markdown(f"### {message}")

        try:
            my_results = load_my_exam_results(auth_uid)
            if my_results:
                latest = my_results[0]
                st.write(f"Cloud verified log score: **{latest.get('score', 0)} / {latest.get('total_questions', 0)}**")
        except Exception:
            pass

        if st.button("Start New Exam Attempt", use_container_width=True):
            clear_exam_attempt(auth_uid)
            reset_exam_state()
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # 3. INTRODUCTORY INSTRUCTIONS BAR LAYER (Only accessible if NOT finished)
    elif not st.session_state.exam_started and not st.session_state.exam_finished:
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
        st.write("If you refresh or close the browser, the timer keeps running in the background.")
        st.write("Your score will be saved automatically when you finish or when time runs out.")
        st.write("You need to score 82% or higher to pass the exam.")
        st.error("⚠️ FINAL EXAM WARNING: Read each question carefully. After you submit an answer, you cannot go back and change it.")

        if st.button("Start Final Exam", use_container_width=True):
            start_exam()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. ACTIVE EVALUATION INTERACTIVE LAYER
    elif st.session_state.exam_started and not st.session_state.exam_finished:
        if not st.session_state.warning_shown and get_remaining_seconds() <= (WARNING_MINUTES * 60):
            st.session_state.warning_shown = True
            push_session_attempt_to_cloud(auth_uid)

        if st.session_state.warning_shown:
            st.warning(f"⏱️ Warning: Only {WARNING_MINUTES} minutes remain in your exam window.")

        st.markdown(
            f'<div class="status-bar">Question {st.session_state.current_question_index + 1} of {len(QUIZ_QUESTIONS)} | Current Score: {st.session_state.score}</div>',
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

    st.markdown("</div>", unsafe_allow_html=True)
