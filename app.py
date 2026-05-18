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
        var warned = false;
        function u() {{
            if(s <= 0) {{
                document.getElementById("t").innerHTML = "00:00";
                setTimeout(function() {{ window.parent.location.reload(); }}, 300);
                return;
            }}
            // Force an automatic page reload at exactly 5:00 (300s) remaining to display the warning banner natively
            if (s === 300 && !warned) {{
                warned = true;
                setTimeout(function() {{ window.parent.location.reload(); }}, 500);
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
