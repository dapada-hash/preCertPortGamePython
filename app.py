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

QUIZ_DURATION_MINUTES = 27
WARNING_MINUTES = 5

RESULTS_COLLECTION = "exam_results"
STUDENT_PROFILES_COLLECTION = "student_profiles"
EXAM_ATTEMPTS_COLLECTION = "exam_attempts"

PERIOD_OPTIONS = [
    "Period 1", "Period 2", "Period 3", "Period 4",
    "Period 5", "Period 6", "Period 7", "Period 8", "Other"
]

# =================================================
# QUIZ QUESTIONS
# =================================================
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Which of the following checks for value equality between two lists <br>&nbsp;&nbsp;&nbsp;&nbsp;A = [1, 2, 3, 4], <br>&nbsp;&nbsp;&nbsp;&nbsp;B = ['a', 'b', 'c', 'd']?",
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
    "question": "Given <br>&nbsp;&nbsp;&nbsp;&nbsp;value1 = 9, <br>&nbsp;&nbsp;&nbsp;&nbsp;value2 = 4, <br>what is the data type of A after the expression, <br>&nbsp;&nbsp;&nbsp;&nbsp;A = (value1 % value2 * 10) // 2.0** 3.0 + value2?",
    "type": "mc",
    "options": ["18.0", "5.0", "18", "22.0"],
    "answer": "5.0"
},
   {
    "id": 4,
    "question": "Complete the Python script below by selecting the correct options directly from the drop-down menus:",
    "type": "dropdown_sim",
    "code": """import os
file_name = "my_document.txt"
text_to_write = "This line will be added to the end.\\n"

if os.path.<u>DROPDOWN 1</u>(file_name):
    print(f"File '{file_name}' exists. Append text.")
    file = open(file_name, <u>DROPDOWN 2</u>)
    <u>DROPDOWN 3</u>(text_to_write)
    file.close()
else:
    print(f"File '{file_name}' does not exist. No file was opened or written to")""",
    "dropdowns": [
        {
            "id": "DD1",
            "label": "DROPDOWN 1 (os.path Method)",
            "options": ["get_status", "exists", "isfile", "check_file"],
            "answer": "exists",
        },
        {
            "id": "DD2",
            "label": "DROPDOWN 2 (File Mode)",
            "options": ["'r'", "'w'", "'a'", "'r+'"],
            "answer": "'a'",
        },
        {
            "id": "DD3",
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

My_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', ... 'z']<br>
new_slice_3_to_6 = My_list[3:6]<br>
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
        "question": "Given the command 'main.py this beautiful nature', which value is stored at index position 1 in the sys.argv list?",
        "type": "mc",
        "options": ["main.py", "Jesus", "is", "love"],
        "answer": "Jesus",
    },
    {
        "id": 9,
        "question": """Given grade=76 and rank=3, what is the output?

if grade >= 80 and rank == 2:
    <br>&nbsp;&nbsp;&nbsp;print("your grade is B")<br>
elif grade < 70 and rank == 2:  
    <br>&nbsp;&nbsp;&nbsp;print("your grade is C") <br>
else:
    <br>&nbsp;&nbsp;&nbsp;print("your grade is F")""",
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
result = d.strftime("%Y-%m-%d")
print(result)""",
        "type": "mc",
        "options": ["A. 2026-03-23", "B. 2026-23-03", "C. 03-23-2026", "D. 23-03-2026"],
        "answer": "A. 2026-03-23",
    },
    {
        "id": 23,
        "question": """What is the output of the following Python code?

<br>&nbsp;&nbsp;&nbsp;&nbsp;name = "Alex"
<br>&nbsp;&nbsp;&nbsp;&nbsp;score = 85
<br>&nbsp;&nbsp;&nbsp;&nbsp;result = f"{name} scored {score}%"
<br>&nbsp;&nbsp;&nbsp;&nbsp;print(result)""",
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
    {
    "id": 26,
    "question": "What is the output of the following Python code?<br><br>&nbsp;&nbsp;&nbsp;&nbsp;items = ['apple', 'banana', 'cherry']<br>&nbsp;&nbsp;&nbsp;&nbsp;items.append('date')<br>&nbsp;&nbsp;&nbsp;&nbsp;items.insert(1, 'blueberry')<br>&nbsp;&nbsp;&nbsp;&nbsp;print(items[2])",
    "type": "mc",
    "options": [
        "A. blueberry",
        "B. banana",
        "C. cherry",
        "D. apple"
    ],
    "answer": "B. banana"
    },
    {
    "id": 27,
    "question": """What is the output of the following Python code?

<br>&nbsp;&nbsp;&nbsp;&nbsp;total = 0
<br>&nbsp;&nbsp;&nbsp;&nbsp;for i in range(1, 4):
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;total += i
<br>&nbsp;&nbsp;&nbsp;&nbsp;print(total)""",
    "type": "mc",
    "options": ["A. 3", "B. 6", "C. 10", "D. 0"],
    "answer": "B. 6",
},
{
        "id": 28,
        "question": """What is the output of the following Python code?

<br>&nbsp;&nbsp;&nbsp;&nbsp;def calculate_total(price, tax=0.05):
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return price + (price * tax)
<br>&nbsp;&nbsp;&nbsp;&nbsp;
<br>&nbsp;&nbsp;&nbsp;&nbsp;result = calculate_total(100)
<br>&nbsp;&nbsp;&nbsp;&nbsp;print(result)""",
        "type": "mc",
        "options": ["A. 100", "B. 105.0", "C. 5.0", "D. TypeError: missing 1 required positional argument"],
        "answer": "B. 105.0",
    },
    {
    "id": 29,
    "question": """What is the output of the following Python code?

<br>&nbsp;&nbsp;&nbsp;&nbsp;def greet(name, uppercase=False):
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if uppercase:
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f"HELLO {name.upper()}"
<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;return f"Hello {name}"
<br>&nbsp;&nbsp;&nbsp;&nbsp;
<br>&nbsp;&nbsp;&nbsp;&nbsp;result = greet("Sam", True)
<br>&nbsp;&nbsp;&nbsp;&nbsp;print(result)""",
    "type": "mc",
    "options": ["A. Hello Sam", "B. HELLO SAM", "C. HELLO Sam", "D. Hello SAM"],
    "answer": "B. HELLO SAM",
},
]

# =================================================
# CSS CUSTOM RENDERING
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
        background-color: #5a6268;
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 25px;
        font-size: 0.95em;
        text-align: center;
        font-weight: 600;
        letter-spacing: 0.5px;
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

    .result-box {
        text-align: center;
        padding: 40px 20px;
        background-color: #e9ecef;
        border-radius: 8px;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =================================================
# COOKIE MANAGEMENT
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

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    requests_resp = requests.post(url, json=payload, timeout=20)
    data = requests_resp.json()

    if requests_resp.status_code != 200:
        err_msg = data.get("error", {}).get("message", "Authentication failed.")
        raise ValueError(err_msg)

    return {
        "id_token": data.get("idToken", ""),
        "refresh_token": data.get("refreshToken", ""),
        "local_id": data.get("localId", ""),
    }


def verify_firebase_session_cookie(session_cookie: str):
    get_firestore_client()
    return firebase_auth.verify_session_cookie(session_cookie, check_revoked=True)


def persist_auth_cookie(id_token: str):
    if cookies is None:
        return
    get_firestore_client()
    session_cookie = firebase_auth.create_session_cookie(id_token, expires_in=5 * 24 * 60 * 60)
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
        return False
# =================================================
# DATA PERSISTENCE COMPONENT LAYER
# =================================================
def load_student_profiles():
    try:
        docs = db().collection(STUDENT_PROFILES_COLLECTION).stream()
        res = [dict(d.to_dict(), id=d.id) for d in docs]
        return sorted(res, key=lambda x: (x.get("period", ""), x.get("last_name", ""), x.get("first_name", "")))
    except Exception:
        return []


def upsert_student_profile(student_id: str, last_name: str, first_name: str, period: str, email: str, password: str = None):
    try:
        clean_email = email.strip().lower()
        # 1. Save profile details securely inside Firestore
        db().collection(STUDENT_PROFILES_COLLECTION).document(student_id).set({
            "student_id": student_id,
            "last_name": last_name,
            "first_name": first_name,
            "period": period,
            "email": clean_email,
            "updated_at": now_utc(),
        }, merge=True)

        # 2. Provision Auth credentials inside Firebase Auth database
        try:
            user = firebase_auth.get_user_by_email(clean_email)
            if password and password.strip():
                firebase_auth.update_user(user.uid, password=password)
        except firebase_auth.UserNotFoundError:
            create_args = {
                "email": clean_email,
                "display_name": f"{first_name} {last_name}".strip(),
            }
            if password and password.strip():
                create_args["password"] = password
            
            try:
                # Use sanitized student_id as UID for relational simplicity
                firebase_auth.create_user(uid=student_id, **create_args)
            except Exception:
                # Fallback to random UID if student_id contains Auth-incompatible characters
                firebase_auth.create_user(**create_args)
        return True
    except Exception as e:
        st.error(f"Failed to register authentication credentials: {e}")
        return False


def load_all_exam_results():
    try:
        docs = db().collection(RESULTS_COLLECTION).stream()
        res = []
        for d in docs:
            v = d.to_dict()
            if "student_name" not in v:
                first = v.get("first_name", "").strip()
                last = v.get("last_name", "").strip()
                v["student_name"] = first if first else last
            res.append(v)
        return sorted(res, key=lambda x: x.get("submitted_at", ""), reverse=True)
    except Exception:
        return []


def load_my_exam_results(auth_uid: str):
    try:
        docs = db().collection(RESULTS_COLLECTION).where("auth_uid", "==", auth_uid).stream()
        res = [dict(d.to_dict(), id=d.id) for d in docs]
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
    except Exception:
        pass


def clear_exam_attempt(auth_uid: str):
    try:
        db().collection(EXAM_ATTEMPTS_COLLECTION).document(auth_uid).delete()
    except Exception:
        pass


def save_final_exam_result(auth_uid: str, student_profile: dict, score: int, total: int, timed_out=False):
    try:
        percentage = round((score / total) * 100, 1) if total > 0 else 0.0
        doc_id = f"{auth_uid}_{int(time.time())}"
        
        first_name = student_profile.get("first_name", "").strip()
        last_name = student_profile.get("last_name", "").strip()
        
        # Formats the name cleanly as a single real name string (e.g., "Darly")
        full_name = first_name if first_name else (last_name if last_name else "Student")
        student_email = st.session_state.auth_user.get("email", "No Email Logged")

        payload = {
            "auth_uid": auth_uid,
            "student_id": student_profile.get("student_id", "UNKNOWN"),
            "student_name": full_name,
            "student_email": student_email,
            "first_name": first_name,
            "last_name": last_name,
            "period": student_profile.get("period", ""),
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "timed_out": timed_out,
            "submitted_at": now_utc(),
        }
        db().collection(RESULTS_COLLECTION).document(doc_id).set(payload)
        return True
    except Exception:
        return False


def get_student_profile_by_email(email: str):
    try:
        clean_email = email.strip().lower()
        # Direct email lookups
        docs = db().collection(STUDENT_PROFILES_COLLECTION).where("email", "==", clean_email).stream()
        for d in docs:
            return d.to_dict()

        # Fallback profile lookup matching engine
        docs = db().collection(STUDENT_PROFILES_COLLECTION).stream()
        for d in docs:
            v = d.to_dict()
            if str(v.get("student_id", "")).strip() and clean_email.startswith(str(v.get("student_id", "")).strip().lower()):
                return v
    except Exception:
        pass
    return None


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


def push_session_attempt_to_cloud(auth_uid: str):
    if not st.session_state.exam_started:
        return
    db().collection(EXAM_ATTEMPTS_COLLECTION).document(auth_uid).set({
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
    })


def get_remaining_seconds():
    if not st.session_state.exam_started or st.session_state.start_time_epoch == 0:
        return QUIZ_DURATION_MINUTES * 60
    elapsed = time.time() - st.session_state.start_time_epoch
    return max(0.0, (QUIZ_DURATION_MINUTES * 60) - elapsed)


def render_js_timer():
    rem_sec = int(get_remaining_seconds())
    if rem_sec <= 0:
        return
    components.html(f"""
    <div id="t" style="font-size:1.5em; font-weight:bold; color:#dc3545; text-align:right; font-family:sans-serif;">00:00</div>
    <script>
        var s = {rem_sec};
        function u() {{
            if(s <= 0) {{
                document.getElementById("t").innerHTML = "00:00";
                setTimeout(function() {{ window.parent.location.reload(); }}, 300);
                return;
            }}
            var m = Math.floor(s / 60), sec = s % 60;
            document.getElementById("t").innerHTML = (m<10?"0":"")+m+":"+(sec<10?"0":"")+sec;
            s--;
        }}
        u(); setInterval(u, 1000);
    </script>
    """, height=45)


def current_question():
    idx = st.session_state.get("current_question_index", 0)
    if 0 <= idx < len(QUIZ_QUESTIONS):
        return QUIZ_QUESTIONS[idx]
    return None

# =================================================
# ENGINE LOGIC ACTIONS
# =================================================
def start_exam():
    st.session_state.exam_started = True
    st.session_state.exam_finished = False
    st.session_state.start_time_epoch = time.time()
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.answers = {}
    st.session_state.feedback = None
    push_session_attempt_to_cloud(st.session_state.auth_user["uid"])


def finish_exam(timed_out=False):
    st.session_state.exam_started = False
    st.session_state.exam_finished = True
    st.session_state.timed_out = timed_out

    uid = st.session_state.auth_user["uid"]
    prof = st.session_state.student_profile or {"first_name": "Student", "last_name": ""}

    save_final_exam_result(
        auth_uid=uid,
        student_profile=prof,
        score=st.session_state.score,
        total=len(QUIZ_QUESTIONS),
        timed_out=timed_out
    )
    clear_exam_attempt(uid)


def submit_answer():
    q = current_question()
    if not q: return
    qid = str(q["id"])
    is_correct = False
    user_ans = None

    if q["type"] == "mc":
        user_ans = st.session_state.get(f"q_{q['id']}_radio")
        if not user_ans:
            st.session_state.feedback = {"type": "missing", "message": "⚠️ Please select an answer before submitting."}
            return
        is_correct = (user_ans == q["answer"])
    elif q["type"] == "mc_multi":
        selected = [opt for i, opt in enumerate(q["options"]) if st.session_state.get(f"q_{q['id']}_check_{i}")]
        if len(selected) != 2:
            st.session_state.feedback = {"type": "missing", "message": "⚠️ Select exactly two choices."}
            return
        user_ans = selected
        is_correct = (set(selected) == set(q["answer"]))
    elif q["type"] == "sequencing":
        ans_list = [st.session_state.get(f"q_{q['id']}_order_{i}", "") for i in range(len(q["options"]))]
        if "" in ans_list:
            st.session_state.feedback = {"type": "missing", "message": "⚠️ Complete all positioning items."}
            return
        user_ans = ans_list
        is_correct = (ans_list == q["answer"])
    elif q["type"] == "dropdown_sim":
        ans_list = [st.session_state.get(f"q_{q['id']}_dd_{i}", "") for i in range(len(q["dropdowns"]))]
        if "" in ans_list:
            st.session_state.feedback = {"type": "missing", "message": "⚠️ Complete all selections."}
            return
        user_ans = ans_list
        is_correct = (ans_list == q["answer"])

    if is_correct:
        st.session_state.score += 1
        st.session_state.feedback = {"type": "correct", "message": "🎯 Correct! Your response has been logged and locked."}
    else:
        st.session_state.feedback = {"type": "incorrect", "message": f"❌ Response locked. (Submitted choice: {user_ans})"}

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
# MAIN APPLICATION ENGINE RE-ROUTER
# =================================================
if "auth_verified" not in st.session_state: st.session_state.auth_verified = False
if "auth_user" not in st.session_state: st.session_state.auth_user = None
if "is_teacher" not in st.session_state: st.session_state.is_teacher = False
if "student_profile" not in st.session_state: st.session_state.student_profile = None
if "exam_started" not in st.session_state: st.session_state.exam_started = False
if "exam_finished" not in st.session_state: st.session_state.exam_finished = False

restore_auth_from_cookie()

if st.session_state.auth_verified and st.session_state.auth_user and not st.session_state.is_teacher:
    uid = st.session_state.auth_user["uid"]
    my_results = load_my_exam_results(uid)
    if my_results:
        st.session_state.exam_finished = True
        st.session_state.exam_started = False
        st.session_state.score = int(my_results[0].get("score", 0))

if "timed_out" not in st.session_state: st.session_state.timed_out = False
if "start_time_epoch" not in st.session_state: st.session_state.start_time_epoch = 0.0
if "current_question_index" not in st.session_state: st.session_state.current_question_index = 0
if "score" not in st.session_state: st.session_state.score = 0
if "answers" not in st.session_state: st.session_state.answers = {}
if "feedback" not in st.session_state: st.session_state.feedback = None
if "warning_shown" not in st.session_state: st.session_state.warning_shown = False

st.title("🐍 Advanced Programming Portal")

if not st.session_state.auth_verified:
    st.subheader("Final Exam Portal Login")
    # Clean Sign-In Form interface. Register Profile form moved to teacher dashboard.
    with st.form("login_form"):
        email_input = st.text_input("School Email").strip()
        pass_input = st.text_input("Access Password", type="password")
        if st.form_submit_button("Authenticate Access", use_container_width=True):
            try:
                res = firebase_sign_in_email_password(email_input, pass_input)
                persist_auth_cookie(res["id_token"])
                st.rerun()
            except Exception as ex:
                st.error(f"Login Rejected: {ex}")
    st.stop()

auth_user = st.session_state.auth_user
auth_uid = auth_user["uid"]
user_email = auth_user["email"]

if not st.session_state.is_teacher and st.session_state.student_profile is None:
    st.session_state.student_profile = get_student_profile_by_email(user_email) or {
        "student_id": "STU-" + auth_uid[:6].upper(), "first_name": user_email.split("@")[0], "last_name": "", "period": "Unassigned"
    }

if st.session_state.auth_verified and not st.session_state.is_teacher and not st.session_state.exam_finished:
    attempt = load_exam_attempt(auth_uid)
    if attempt:
        start_epoch = float(attempt.get("start_time_epoch", 0.0))
        elapsed = time.time() - start_epoch
        allowed_seconds = QUIZ_DURATION_MINUTES * 60
        
        if elapsed < allowed_seconds:
            st.session_state.exam_started = True
            st.session_state.start_time_epoch = start_epoch
            st.session_state.current_question_index = int(attempt.get("current_question_index", 0))
            st.session_state.score = int(attempt.get("score", 0))
            st.session_state.answers = attempt.get("answers", {})
            st.session_state.warning_shown = attempt.get("warning_shown", False)
            st.session_state.feedback = attempt.get("feedback", None)
        else:
            st.session_state.score = int(attempt.get("score", 0))
            finish_exam(timed_out=True)
            st.rerun()

if st.session_state.exam_started and get_remaining_seconds() <= 0:
    finish_exam(timed_out=True)
    st.rerun()

col_user, col_logout = st.columns([3, 1])
with col_user: st.markdown(f"**Account Active:** `{user_email}`")
with col_logout:
    if st.button("Log Out System", use_container_width=True):
        if cookies is not None: cookies["firebase_session"] = ""
        reset_exam_state()
        st.session_state.auth_verified = False
        st.rerun()

# --- ADMINISTRATIVE INSTRUCTOR VIEW ---
if st.session_state.is_teacher:
    st.markdown("---")
    t_tabs = st.tabs(["Database Records Grid", "Active Exam Logs", "Roster Management Form"])
    with t_tabs[0]:
        import pandas as pd
        raw_results = load_all_exam_results()
        if raw_results:
            df = pd.DataFrame(raw_results)
            preferred_cols = [
                "period", "student_id", "student_name", "student_email", 
                "percentage", "score"
            ]
            existing_cols = [c for c in preferred_cols if c in df.columns]
            other_cols = [c for c in df.columns if c not in preferred_cols]
            df = df[existing_cols + other_cols]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No exam submissions recorded yet.")
            
    with t_tabs[1]:
        st.dataframe(load_student_profiles(), use_container_width=True)

    with t_tabs[2]:
        st.subheader("Roster Management Form")
        st.write("Add new student profiles and credential pairings to the secure database roster:")
        with st.form("register_profile_form"):
            reg_id = st.text_input("Student ID Number").strip()
            reg_first = st.text_input("First Name").strip()
            reg_last = st.text_input("Last Name").strip()
            reg_email = st.text_input("Student Email Address").strip()
            reg_password = st.text_input("Set Access Password (Min. 6 chars)", type="password").strip()
            reg_period = st.selectbox("Class Period", PERIOD_OPTIONS)
            
            if st.form_submit_button("Register Student Profile", use_container_width=True):
                if reg_id and reg_first and reg_last and reg_email and reg_password:
                    if len(reg_password) < 6:
                        st.error("⚠️ Authentication security requires a password at least 6 characters long.")
                    else:
                        if upsert_student_profile(reg_id, reg_last, reg_first, reg_period, reg_email, reg_password):
                            st.success(f"🎉 Successfully provisioned secure access profile for **{reg_first} {reg_last}**!")
                            st.rerun()
                else:
                    st.error("⚠️ Please fill out all required fields (ID, First Name, Last Name, Email, and Password).")

# --- STUDENT ASSESSMENT INTERFACE WORKFLOW ---
else:
    st.markdown('<div class="quiz-shell">', unsafe_allow_html=True)
    student_profile = st.session_state.student_profile

    h_left, h_right = st.columns([3, 1])
    with h_left: 
        st.markdown('<div class="header-title">Python Final Exam</div>', unsafe_allow_html=True)
    with h_right:
        if st.session_state.exam_started and not st.session_state.exam_finished:
            render_js_timer()
        else:
            st.markdown('<div class="timer-box" style="color:#6c757d;">Closed</div>' if st.session_state.exam_finished else f'<div class="timer-box">{QUIZ_DURATION_MINUTES:02d}:00</div>', unsafe_allow_html=True)

    if st.session_state.exam_finished:
        display_score = st.session_state.score
        try:
            my_results = load_my_exam_results(auth_uid)
            if my_results:
                display_score = int(my_results[0].get("score", display_score))
        except Exception:
            pass

        percentage = round((display_score / len(QUIZ_QUESTIONS)) * 100, 1) if QUIZ_QUESTIONS else 0.0
        msg = "🎉 Perfect score! Masterful job!" if percentage == 100 else ("👍 Excellent work! You have passed the certification standard threshold!" if percentage >= 84 else "📚 Evaluation complete. You did not meet the passing standard threshold.")

        st.markdown('<div class="result-box"><h2>Exam Evaluation Complete</h2>', unsafe_allow_html=True)
        st.write(f"Your calculated score: **{display_score}** / **{len(QUIZ_QUESTIONS)}**")
        st.write(f"Final Percentage: **{percentage}%**")
        st.markdown(f"### {msg}")

        if st.button("Start New Exam Attempt", use_container_width=True):
            try:
                clear_exam_attempt(auth_uid)
                for d in db().collection(RESULTS_COLLECTION).where("auth_uid", "==", auth_uid).stream():
                    db().collection(RESULTS_COLLECTION).document(d.id).delete()
            except Exception: pass
            reset_exam_state()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif not st.session_state.exam_started:
        st.markdown(f'<div class="status-bar">{student_profile.get("first_name", "")} | ID: {student_profile.get("student_id", "")} | {student_profile.get("period", "")}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="question-box"><div class="question-title">Final Exam Instructions</div>', unsafe_allow_html=True)
        st.write("You will answer one question at a time.")
        st.write(f"You have **{QUIZ_DURATION_MINUTES} minutes** to complete the exam.")
        st.write("If you refresh or close the browser, the timer keeps running in the background.")
        st.write("Your score will be saved automatically when you finish each question.")
        st.write("You need to score 84% or higher to pass the exam.")
        st.write("After you submit an answer, you will receive immediate feedback and your answer will be locked in for that question.")
        st.write("You can start the exam at any time, but once you begin, the timer will start and cannot be paused.")
        st.write("Make sure you submit your answers before the timer runs out. If time expires, the exam will end.")
        st.error("⚠️ FINAL EXAM WARNING: Read each question carefully. After you submit an answer, you cannot go back and change it.")
        
        if st.button("Start Final Exam", use_container_width=True):
            start_exam()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        if not st.session_state.warning_shown and get_remaining_seconds() <= (WARNING_MINUTES * 60):
            st.session_state.warning_shown = True
            push_session_attempt_to_cloud(auth_uid)
        if st.session_state.warning_shown:
            st.warning(f"⏱️ Warning: Only {WARNING_MINUTES} minutes remain in your exam window.")

        st.markdown(
            f'<div class="status-bar">Question {st.session_state.current_question_index + 1} of {len(QUIZ_QUESTIONS)} | Current Score: {st.session_state.score}</div>', 
            unsafe_allow_html=True
        )
        
        question = current_question()
        if question:
            # HTML format support enabled
            st.markdown(f'<div class="question-box"><div class="question-title">Q{st.session_state.current_question_index + 1}. {question["question"]}</div>', unsafe_allow_html=True)

            if question["type"] == "mc":
                st.radio("Select one answer", question["options"], key=f"q_{question['id']}_radio", index=None, label_visibility="collapsed")
            elif question["type"] == "mc_multi":
                for i, opt in enumerate(question["options"]): 
                    st.checkbox(opt, key=f"q_{question['id']}_check_{i}")
            elif question["type"] == "sequencing":
                for i in range(len(question["options"])): 
                    st.selectbox(f"Position {i + 1}", [""] + question["options"], key=f"q_{question['id']}_order_{i}")
            elif question["type"] == "dropdown_sim":
                if question.get("code"): 
                    st.markdown(f'<div class="code-box">{question["code"]}</div>', unsafe_allow_html=True)
                
                for i, dd in enumerate(question["dropdowns"]):
                    visual_label = dd.get("label", dd.get("id", f"Dropdown {i + 1}"))
                    st.selectbox(visual_label, [""] + dd["options"], key=f"q_{question['id']}_dd_{i}")

            if st.session_state.feedback:
                fb = st.session_state.feedback
                if fb["type"] == "correct":
                    st.success(fb["message"])
                elif fb["type"] == "incorrect":
                    st.error(fb["message"])
                else:
                    st.warning(fb["message"])

            if str(question["id"]) not in st.session_state.answers:
                if st.button("Submit Answer", use_container_width=True):
                    submit_answer()
                    st.rerun()
            else:
                lbl = "View Results" if st.session_state.current_question_index == len(QUIZ_QUESTIONS) - 1 else "Continue to Next Question"
                if st.button(lbl, use_container_width=True):
                    next_question()
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
