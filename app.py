<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pre-check: Modern Multi-Format HTML Quiz</title>
    <style>
        /* CSS Styles */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            /* DARK MODE: Deep Black Background */
            background-color: #121212; 
            margin: 0;
            color: #ffffff; /* Default text color is white */
        }

        #quiz-container {
            /* DARK MODE: Dark Gray Container */
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); /* Stronger shadow for depth */
            text-align: left; /* Left for neat instructional lists */
            width: 90%;
            max-width: 850px; /* Widened slightly to support dual-column landing screen */
            border: 1px solid #333333;
        }

        h1 {
            /* Highlight Color */
            color: #00bcd4; 
            margin-bottom: 25px;
            border-bottom: 2px solid #333333;
            padding-bottom: 10px;
            font-size: 1.8em;
            text-align: center;
        }
        
        /* Styles for the Timer and Header Info */
        #header-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        #score-display {
            font-size: 1.2em;
            font-weight: bold;
            color: #4caf50; /* Green score */
        }
        
        #timer-display {
            font-size: 1.2em;
            font-weight: bold;
            color: #ff5252; /* Default Red color */
            border: 2px solid #ff5252;
            padding: 5px 10px;
            border-radius: 5px;
            min-width: 90px;
            text-align: center;
            background-color: #2b1f1f;
            transition: all 0.5s ease; /* Smooth color transition */
        }
        
        /* Time Warning Style (5 minutes or less) */
        .time-warning {
            background-color: #ffc107 !important; /* Bright Yellow */
            color: #121212 !important; /* Black text for contrast */
            border-color: #ff9800 !important;
        }

        #question-text {
            font-size: 1.3em;
            margin: 25px 0;
            min-height: 60px;
            font-weight: 500;
            color: #e0e0e0; /* Off-white for question text */
            line-height: 1.5;
        }

        #answer-buttons {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
            min-height: 200px;
        }

        .btn {
            /* DARK MODE: Answer button style */
            background-color: #2a2a2a; 
            color: #ffffff;
            border: 2px solid #555555;
            padding: 14px 20px;
            text-align: left;
            text-decoration: none;
            display: block;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s, border-color 0.3s, transform 0.1s;
            line-height: 1.4;
        }

        .btn:hover:not(.disabled) {
            background-color: #3a3a3a;
            border-color: #00bcd4; /* Hover highlight */
        }

        .btn:active:not(.disabled) {
            transform: scale(0.99);
        }

        /* Feedback colors */
        .correct {
            background-color: #4caf50 !important; /* Brighter Green */
            color: white !important;
            border-color: #388e3c !important; 
        }

        .wrong {
            background-color: #f44336 !important; /* Brighter Red */
            color: white !important;
            border-color: #d32f2f !important;
        }

        .disabled {
            pointer-events: none;
            opacity: 0.6;
            cursor: default !important;
        }
        
        .dragging {
            opacity: 0.3;
        }

        /* ORDER Question Styles (Dark Grid) */
        .order-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 10px;
            border: 2px dashed #555555;
            border-radius: 8px;
            min-height: 180px; 
            background-color: #282828; /* Darker grid background */
        }

        .order-item {
            cursor: grab;
            background-color: #383838;
            border-color: #555555;
            padding: 12px;
            text-align: left;
        }
        
        /* DRAG-DROP Question Styles (Dark Grid) */
        #drag-drop-area {
            display: grid;
            grid-template-columns: 1fr;
            gap: 15px;
            padding: 15px;
            border: 2px dashed #555555;
            border-radius: 8px;
            background-color: #282828;
        }

        @media(min-width: 600px) {
            #drag-drop-area {
                grid-template-columns: 1fr 1fr;
            }
        }

        .drag-item {
            cursor: grab;
            background-color: #ff9800; /* Orange/Gold drag items */
            color: black;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            font-weight: bold;
            text-align: center;
        }
        
        .drop-target {
            background-color: #303030; /* Drop target background */
            border: 2px solid #00bcd4; /* Highlight border */
            color: #cccccc;
            padding: 14px 20px;
            border-radius: 8px;
            text-align: center;
            min-height: 50px; 
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: drop;
            font-size: 0.9em;
        }

        .drop-target .drag-item {
            margin-top: 5px;
            width: 100%;
        }
        
        .drag-item:hover, .order-item:hover {
            box-shadow: 0 0 8px rgba(0, 188, 212, 0.7);
        }

        /* Navigation & Final Score */
        #quiz-navigation {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            margin-top: 30px;
        }

        #next-button, #skip-button, #start-exam-button {
            padding: 12px 28px;
            font-size: 1.1em;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
            font-weight: 600;
        }
        
        #next-button, #start-exam-button {
            background-color: #00bcd4; /* Highlight Color */
        }
        
        #next-button:hover, #start-exam-button:hover {
            background-color: #008ba3;
        }

        #skip-button {
            background-color: #757575; /* Muted gray for skip */
        }

        #skip-button:hover {
            background-color: #616161;
        }
        
        /* Review Screen Styles */
        #review-buttons-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            padding: 10px;
        }

        .review-button {
            background-color: #455a64; /* Darker Blue-Gray base */
            color: white;
            border: 2px solid #607d8b;
            padding: 8px;
            font-size: 1em;
            width: 45px; 
            height: 45px;
            border-radius: 8px;
            cursor: pointer;
            transition: opacity 0.3s;
        }

        .review-button:hover {
            opacity: 0.8;
        }
        
        /* Status Colors for Review Buttons (High Contrast) */
        .status-answered {
            background-color: #4caf50; /* Green */
            border-color: #388e3c;
        }

        .status-skipped {
            background-color: #ffeb3b; /* Yellow */
            color: #121212;
            border-color: #fbc02d;
        }
        
        .status-unanswered {
            background-color: #f44336; /* Red */
            border-color: #d32f2f;
        }

        .hide {
            display: none !important;
        }

        .final-score {
            font-size: 1.8em;
            color: #4caf50;
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
        }

        #email-status-message {
            text-align: center;
            font-size: 1.1em;
            margin: 10px 0;
            font-weight: 500;
        }

        /* --- LANDING INSTRUCTION SCREEN STYLES (DUAL-COLUMN) --- */
        #instructions-container {
            padding: 10px 0;
        }

        .landing-layout {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }

        @media(min-width: 720px) {
            .landing-layout {
                flex-direction: row;
                align-items: stretch;
            }
            .landing-sidebar {
                flex: 1.1;
                border-right: 1px solid #333333;
                padding-right: 30px;
            }
            .landing-main {
                flex: 0.9;
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding-left: 10px;
            }
        }

        .instruction-box {
            background-color: #f1f3f5;
            color: #333333;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 20px;
            border-left: 5px solid #00bcd4;
        }

        .instruction-box h2 {
            margin: 0;
            font-size: 1.25em;
            color: #1e1e1e;
        }

        .instruction-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .instruction-list li {
            position: relative;
            padding-left: 20px;
            margin-bottom: 12px;
            font-size: 0.98em;
            color: #e0e0e0;
            line-height: 1.45;
        }

        .instruction-list li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #00bcd4;
            font-size: 1.4em;
            line-height: 1;
        }

        .warning-box {
            background-color: #ffeef0;
            border: 1px solid #ffa3b1;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }

        .warning-icon {
            font-size: 1.3em;
            color: #f44336;
        }

        .warning-text {
            color: #ff334b;
            font-weight: bold;
            font-size: 0.95em;
            line-height: 1.4;
            margin: 0;
        }

        #start-exam-button-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 10px;
        }

        #start-exam-button {
            width: 100%;
            padding: 15px;
            font-size: 1.2em;
        }

        .student-input-field {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #555;
            background-color: #222;
            color: white;
            font-size: 1.1em;
            box-sizing: border-box;
        }

        .student-input-field::placeholder {
            color: #888;
        }
    </style>
</head>
<body>

    <div id="quiz-container">
        <h1>HTML & CSS FINAL EXAM</h1>
        
        <!-- --- LANDING / INSTRUCTIONS CONTAINER (DUAL-COLUMN LAYOUT) --- -->
        <div id="instructions-container">
            <div class="landing-layout">
                
                <!-- Left Sidebar: Guidelines -->
                <div class="landing-sidebar">
                    <div class="instruction-box">
                        <h2>Exam Guidelines</h2>
                    </div>
                    
                    <ul class="instruction-list">
                        <li>You will answer one question at a time.</li>
                        <li>You have <strong>40 minutes</strong> to complete the exam.</li>
                        <li>If you refresh or close the browser, the timer keeps running in the background.</li>
                        <li>Your score will be saved automatically when you finish each question.</li>
                        <li><strong>If accidentally you select the wrong answer, you cannot change it after clicking</strong></li>
                        <li>You can skip questions if you're unsure about the answer.</li>
                        <li>You need to score 84% or higher to pass the exam.</li>
                        <li>After you submit an answer, you will receive immediate feedback and your answer will be locked in for that question.</li>
                        <li>You can start the exam at any time, but once you begin, the timer will start and cannot be paused.</li>
                        <li>Make sure you submit your answers before the timer runs out. If time expires, the exam will end.</li>
                    </ul>
                </div>
                
                <!-- Right Main Column: Warnings, Registration, and Start -->
                <div class="landing-main">
                    <div class="warning-box">
                        <span class="warning-icon">⚠️</span>
                        <p class="warning-text">FINAL EXAM WARNING: Read each question carefully. After you submit an answer, you cannot go back and change it.</p>
                    </div>

                    <!-- Student Metadata Collection Fields -->
                    <div style="margin-bottom: 25px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: bold; color: #00bcd4;">Please enter your name to start:</label>
                        <input type="text" id="student-name-input" class="student-input-field" placeholder="First and Last Name" required>
                    </div>

                    <div id="start-exam-button-container">
                        <button id="start-exam-button">Start Final Exam</button>
                    </div>
                </div>
                
            </div>
        </div>

        <!-- --- ACTIVE QUIZ BODY (HIDDEN BY DEFAULT) --- -->
        <div id="quiz-active-body" class="hide">
            <div id="header-info">
                <div id="score-display">Score: 0 / 0</div>
                <div id="timer-display">40:00</div>
            </div>

            <div id="question-area">
                <div id="question-text">Quiz loading...</div>
                <div id="answer-buttons"></div>
            </div>
            
            <div id="review-area" class="hide">
                <h2>Quiz Status Review</h2>
                <p style="color: #cccccc;">Click any question to return and update your answer.</p>
                <div id="review-buttons-container"></div>
            </div>

            <div id="quiz-navigation">
                <button id="skip-button">Skip Question</button>
                <button id="next-button" class="hide">Next Question</button>
            </div>
        </div>
    </div>

    <script>
        // Global Constants
        const QUIZ_PROGRESS_KEY = "certiport_html_progress";
        const TIMER_TIME_KEY = "certiport_html_timer_val";
        const TIMER_START_KEY = "certiport_html_timer_start";
        const STUDENT_NAME_KEY = "certiport_student_name";

        // =============================================================
        // FORMSPREE CONFIGURATION: Replace with your free Formspree ID
        // =============================================================
        const FORMSPREE_FORM_ID = "YOUR_FORMSPREE_FORM_ID_HERE"; // Put your Formspree ID key here!

        const initialTime = 40 * 60; // 40 minutes in seconds
        const WARNING_TIME = 5 * 60; // 5 minutes warning in seconds

        let questions = [];
        let currentQuestionIndex = 0;
        let score = 0;
        let timeLeft = initialTime;
        let timerInterval = null;
        let isTimerStarted = false;
        let isReviewMode = false;
        let draggedItem = null;
        let studentName = "";

        // DOM Element Selectors
        const instructionsContainer = document.getElementById('instructions-container');
        const quizActiveBody = document.getElementById('quiz-active-body');
        const scoreDisplay = document.getElementById('score-display');
        const timerDisplay = document.getElementById('timer-display');
        const questionArea = document.getElementById('question-area');
        const questionText = document.getElementById('question-text');
        const answerButtons = document.getElementById('answer-buttons');
        const reviewArea = document.getElementById('review-area');
        const reviewButtonsContainer = document.getElementById('review-buttons-container');
        const skipButton = document.getElementById('skip-button');
        const nextButton = document.getElementById('next-button');
        const startExamButton = document.getElementById('start-exam-button');
        const studentNameInput = document.getElementById('student-name-input');
        const quizContainer = document.getElementById('quiz-container');

        // Questions pool compiled ONLY from your provided library:
        const initialQuestions = [
            {
                type: "multiple-choice",
                question: "A website developer is creating two separate forms: Form A is for a user to log in with a username and password. Form B is for searching the site's database for products based on a simple keyword. Which method is most appropriate for each form, and why?",
                answers: [
                    { text: "Form A: POST, Form B: GET. Form A uses POST because it sends sensitive, non-idempotent data (password) in the request body, not the URL. Form B uses GET because the search action is safe and bookmarkable.", correct: true },
                    { text: "Form A: GET, Form B: POST. Because search results are long, and login data is short.", correct: false },
                    { text: "Form A: POST, Form B: POST. Because all form submissions should use POST for consistency.", correct: false },
                    { text: "Form A: GET, Form B: GET. Because both actions involve passing information to the server.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A team wants to create a custom video player with a unique brand style. They successfully use JavaScript's play() and pause() methods on the video element, but the video does not display the default controls (play/pause button, volume, seeking bar). What is the most likely and necessary HTML attribute adjustment required to achieve this customization?",
                answers: [
                    { text: "The src attribute must be replaced with the <source> element.", correct: false },
                    { text: "The preload attribute must be set to none to prevent control display.", correct: false },
                    { text: "The controls attribute must be omitted from the <video> tag.", correct: true },
                    { text: "The src attribute must be replaced with the <source> element.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A global company is launching a product video and needs to provide captions in English, Spanish, and French. The developer has created three separate WebVTT files: en.vtt, es.vtt, and fr.vtt. Which is the correct and most effective HTML structure to implement all three language options for the video?",
                answers: [
                    { text: 'Using a single <track> element with a comma-separated srclang list: <track src="all.vtt" srclang="en,es,fr" kind="captions">', correct: false },
                    { text: 'Using three separate <source> elements, each with a srclang attribute: <source src="en.vtt" type="text/vtt" srclang="en">', correct: false },
                    { text: "Using one <track> element for each language, all nested within the <video> tag, each with its appropriate srclang and label.", correct: true },
                    { text: 'Setting the srclang attribute on the main <video> tag: <video srclang="en,es,fr">...<track src="en.vtt">', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A web developer embeds an audio clip, but wants to ensure users with very old or unsupported browsers can still access the file. Where should the developer place the text link to the MP3 file?",
                answers: [
                    { text: "Immediately after the closing </audio> tag, as the browser will skip content it can't render.", correct: false },
                    { text: "Between the <source> tags, but only if the type attribute is omitted from the <source>.", correct: false },
                    { text: "Between the opening <audio> tag and the closing </audio> tag, after the <source> elements.", correct: true },
                    { text: 'Inside the <source> tag, as an attribute: <source src="jingle.mp3" fallback-link="..." type="audio/mpeg">', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A content editor needs a way to style book titles on an e-commerce site to appear in a Small-Caps style. Crucially, they want the text to retain the original mixed-case (Title Case) version of the title when copied and pasted by the user. The original HTML text is The Hitchhiker's Guide to the Galaxy. Which CSS declaration should the developer use to style the titles?",
                answers: [
                    { text: "text-transform: uppercase;", correct: false },
                    { text: "text-transform: capitalize;", correct: false },
                    { text: "font-variant: small-caps;", correct: true },
                    { text: "text-decoration: none;", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A development team launches a new global website. Users in regions outside the US report that special characters (like 'ñ', 'é', 'ü', and '€') are showing up as scrambled symbols or question marks ('?')—a phenomenon known as 'mojibake.' The current HTML document is missing any character set declaration. What is the single best and most necessary HTML declaration the developer should add, and where should it be placed, to immediately fix this character rendering issue?",
                answers: [
                    { text: "Change the file's save format to ASCII and set <meta charset='ASCII'>.", correct: false },
                    { text: 'Set the encoding attribute on the <html> tag to encoding="UTF-8".', correct: false },
                    { text: 'Add <meta charset="UTF-8"> as one of the first elements inside the <head> tag.', correct: true },
                    { text: 'Add <meta name="charset" content="UTF-8"> inside the <body> tag.', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: 'A developer wants to set the site s main search engine description but mistakenly uses the keywords name attribute, resulting in the following:<meta name="keywords" content="This is the full, descriptive, 150-character summary of the entire page content.">What is the correct way to format this tag if the developer s primary goal is to provide the 150-character snippet that appears below the title link in search results?" ',
                answers: [
                    { text: '<meta name="description" content="summary, with, only, keywords, here">', correct: false },
                    { text: '<meta name="author" content="This is the full, descriptive, 150-character summary of the entire page content.">', correct: false },
                    { text: '<meta name="description" content="This is the full, descriptive, 150-character summary of the entire page content.">', correct: true },
                    { text: '<meta name="keywords" content="only, one, or, two, words, here">', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A developer is structuring an image using the <picture> element for art direction and needs to provide the source URLs. Which of the following is the correct and necessary attribute for specifying the primary image file(s) on the child elements (the <source> and <img> tags), and which attribute is completely irrelevant to images?",
                answers: [
                    { text: "srclang should be used instead of src for responsive images.", correct: false },
                    { text: "src and srclang are both correct for the <source> tag.", correct: false },
                    { text: "The primary attributes for specifying image files are src and srcset; srclang is for video/audio text tracks.", correct: true },
                    { text: "srcset is required on the <img> tag, and src is optional.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A developer is adding a chart to an article about population trends. The chart (<img> element) is essential for context, and it requires a descriptive caption. Which HTML structure correctly wraps the chart and its caption to be semantically correct according to modern HTML standards?",
                answers: [
                    { text: '<figure><img src="chart.png"><img>Chart Caption</img></figure>', correct: false },
                    { text: '<figcaption><img src="chart.png"><figure>Chart Caption</figure></figcaption>', correct: false },
                    { text: '<figure><img src="chart.png"><figcaption>Chart Caption</figcaption></figure>', correct: true },
                    { text: '<figcaption><img src="chart.png"><img>Chart Caption</img></figcaption>', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: 'A developer adds a large comment box to a form: <textarea cols="50" rows="10"></textarea>. What does the cols="50" attribute value specifically control?',
                answers: [
                    { text: "The maximum number of characters the user can type into the box.", correct: false },
                    { text: "The horizontal padding inside the text area in pixels.", correct: false },
                    { text: "The visible width of the text area, approximately equal to 50 average-width characters.", correct: true },
                    { text: "The minimum number of characters that must be entered to submit the form.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A news website displays a main story, user comments on that story, and related trending articles. Which of these pieces of content should most appropriately be marked up using the <article> element?",
                answers: [
                    { text: "The entire website header and navigation bar.", correct: false },
                    { text: "The main story, and each individual user comment on the main story.", correct: true },
                    { text: "Only the main story's byline and date.", correct: false },
                    { text: "The list of related trending articles, but not the main story itself.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "The core characteristic of content within an <article> tag is its self-contained nature. Which of the following best describes what 'self-contained' means in this context?",
                answers: [
                    { text: "The content must not contain any images or links.", correct: false },
                    { text: "The content makes sense on its own, and could theoretically be taken out of the document and read in an RSS feed or on a different website without losing its meaning.", correct: true },
                    { text: "The content must have been published within the last 24 hours.", correct: false },
                    { text: "The content must be shorter than 500 words.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A developer is creating a single-page news digest. Which structure is generally the most appropriate semantic grouping for organizing the overall page content?",
                answers: [
                    { text: "Using nested <article> tags for every level of content hierarchy.", correct: false },
                    { text: "Using one primary <section> to contain a group of related news stories, with each individual news story marked up using its own separate <article> tag.", correct: true },
                    { text: "Using only <div> tags and skipping both <section> and <article>.", correct: false },
                    { text: "Using one large <article> to wrap the entire page content, then using <section> for each news story.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which CSS property is most used to change the vertical layering (stacking order) of elements, but has absolutely no effect on a position: static element?",
                answers: [
                    { text: "opacity", correct: false },
                    { text: "z-index", correct: true },
                    { text: "display", correct: false },
                    { text: "margin", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "What is the default value for the CSS position property?",
                answers: [
                    { text: "Static", correct: true },
                    { text: "relative", correct: false },
                    { text: "absolute", correct: false },
                    { text: "fixed", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which two CSS units are designed to scale directly and independently with the size of the user's viewport, unlike the % unit, which scales indirectly?",
                answers: [
                    { text: "Root Element Font Size (rem) and Element Font Size (em).", correct: false },
                    { text: "Pixel (px) and Element Font Size (em).", correct: false },
                    { text: "Percentage (%) and Root Element Font Size (rem).", correct: false },
                    { text: "Viewport Width (vw) and Viewport Height (vh).", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "What is the standard, unstyled default color assigned to an unvisited hyperlink (using the a:link pseudo-class) by most modern web browsers (user agent stylesheets)?",
                answers: [
                    { text: "blue", correct: true },
                    { text: "purple", correct: false },
                    { text: "red", correct: false },
                    { text: "yellow", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "A developer needs to horizontally center a block-level <div> container that has a fixed width of 960px within its 100% wide parent container. Which is the standard and most direct CSS rule used to achieve this horizontal centering in the normal document flow?",
                answers: [
                    { text: "text-align: center;", correct: false },
                    { text: "align-items: center;", correct: false },
                    { text: "position: absolute; left: 50%;", correct: false },
                    { text: "margin: 0 auto;", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "If a user clicks on the following link: <a href='https://www.yahoo.com' target='_blank'>Yahoo</a>, what best describes the link's type and resulting action?",
                answers: [
                    { text: "It is an internal link that opens in the same tab, ignoring _blank.", correct: false },
                    { text: "It is an absolute URL (external link) that opens the Yahoo website in a new tab.", correct: true },
                    { text: "It is a relative link that opens in a new tab, loading the local file https://www.yahoo.com.", correct: false },
                    { text: "It is a relative link that opens the local file nature.html in the current tab.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which box-sizing value is considered the modern standard for responsive design because it calculates the defined width and height to include the element's content, padding, and border?",
                answers: [
                    { text: "border-box", correct: true },
                    { text: "inherit", correct: false },
                    { text: "padding-box", correct: false },
                    { text: "content-box", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "To create a destination point (the actual 'bookmark') within a long HTML document that a link can jump to, which attribute is used on the target element (e.g., a heading tag)?",
                answers: [
                    { text: 'rel="bookmark"', correct: false },
                    { text: 'target="_self"', correct: false },
                    { text: "id", correct: true },
                    { text: 'class="anchor"', correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "By technical definition, what is the primary 'usage' of the <select> tag in an HTML form?",
                answers: [
                    { text: "To create a multi-line text area for user comments.", correct: false },
                    { text: "To provide a container for a dropdown menu that allows users to pick from a set list of options.", correct: true },
                    { text: "To link the form to an external database.", correct: false },
                    { text: "To style a group of radio buttons with CSS.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "What does an element with position: fixed; use as its containing block (the reference point for its coordinates)?",
                answers: [
                    { text: "The viewport (the browser window).", correct: true },
                    { text: "The previous sibling element.", correct: false },
                    { text: "The <body> element.", correct: false },
                    { text: "Its nearest positioned ancestor.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "In CSS, what does the em unit use as its reference size?",
                answers: [
                    { text: "The width of the viewport.", correct: false },
                    { text: "The default browser font size only.", correct: false },
                    { text: "The font size of the parent element.", correct: true },
                    { text: "The height of the current element.", correct: false }
                ]
            },
            {
                type: "multiple-choice",
                question: "Which overflow property value instructs the browser to act intelligently by displaying scrollbars only when the content is too large for the container, thereby preventing unnecessary empty scrollbars from appearing?",
                answers: [
                    { text: "hidden", correct: false },
                    { text: "auto", correct: true },
                    { text: "visible", correct: false },
                    { text: "scroll", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which HTML table cell attribute is used to merge a single cell across multiple columns (horizontally), effectively making the cell wider than a standard cell?",
                answers: [
                    { text: "rowspan", correct: false },
                    { text: "span", correct: false },
                    { text: "cellmerge", correct: false },
                    { text: "colspan", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: 'Which HTML element is commonly used to provide a title or description for a table?',
                answers: [
                    { text: "<caption>", correct: true },
                    { text: "<summary>", correct: false },
                    { text: "<label>", correct: false },
                    { text: "<title>", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "By technical definition, which CSS property value calculates the total width of an element by adding the width, padding, and border values together?",
                answers: [
                    { text: "box-sizing: border-box;", correct: false },
                    { text: "box-sizing: padding-box;", correct: false },
                    { text: "box-sizing: inherit;", correct: false },
                    { text: "box-sizing: content-box;", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "If you are using a mobile-first approach, the styles inside the block following @media only screen and (min-width: 768px) will only take effect when the viewport is how wide?",
                answers: [
                    { text: "Greater than or equal to 768px (e.g., tablet and desktop sizes).", correct: true },
                    { text: "Less than or equal to 767px (e.g., mobile devices).", correct: false },
                    { text: "Exactly 768px (no larger or smaller).", correct: false },
                    { text: "Between 768px and 1024px (a specific tablet range).", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "The title attribute on an <img> tag has which primary function from a user experience standpoint?",
                answers: [
                    { text: "It ensures the image aligns with the nearest text caption.", correct: false },
                    { text: "It provides a brief, non-visible description for search engine optimization (SEO).", correct: false },
                    { text: "It displays a visible title or caption below the image at all times.", correct: false },
                    { text: "It displays a tooltip or hover text when the user places their mouse cursor over the image.", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: 'By definition, what is the primary usage of a group of <input type="radio"> elements?',
                answers: [
                    { text: "To trigger a JavaScript function without submitting the form.", correct: false },
                    { text: "To allow the user to select as many options as they want from a list.", correct: false },
                    { text: "To create a multi-line text entry area.", correct: false },
                    { text: "To allow the user to select only one option from a mutually exclusive set of choices.", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "An element is set to position: absolute;. If its immediate parent has position: static;, what will the element be positioned relative to?",
                answers: [
                    { text: "The immediate parent element, regardless of its position property.", correct: false },
                    { text: "Its nearest positioned ancestor.", correct: true },
                    { text: "The position of its closest sibling element.", correct: false },
                    { text: "The entire document (the <body> tag).", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which box-sizing value is used to simplify 'Usage' by ensuring that if you set an element to width: 500px, it will always remain exactly 500px wide, regardless of how much padding or border you add?",
                answers: [
                    { text: "content-box", correct: false },
                    { text: "border-box", correct: true },
                    { text: "initial", correct: false },
                    { text: "Static", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Under which specific condition will the content placed inside a <noscript> tag be rendered and visible to the user?",
                answers: [
                    { text: "When the external JavaScript file fails to load due to a 404 error.", correct: false },
                    { text: "When the user's internet connection is slow.", correct: false },
                    { text: "When JavaScript is either disabled in the browser settings or not supported by the browser.", correct: true },
                    { text: "When the page is being viewed on a mobile device.", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "The _______symbol selects only elements that are the immediate, direct children of the preceding element.",
                answers: [
                    { text: "+", correct: false },
                    { text: "( )", correct: false },
                    { text: "~", correct: false },
                    { text: ">", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "In terms of 'usage,' why is it a best practice to use the <label> element with the for attribute pointing to an input's id?",
                answers: [
                    { text: "It hides the input field from the user.", correct: false },
                    { text: "It automatically validates the email format.", correct: false },
                    { text: "It changes the text color to red if there is an error.", correct: false },
                    { text: "It increases the clickable area, allowing users to click the text to focus the input, which improves accessibility.", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "Which is the required HTML attribute that tells the browser the file path or URL where the image resource to be embedded is located?",
                answers: [
                    { text: "link", correct: false },
                    { text: "href", correct: false },
                    { text: "path", correct: false },
                    { text: "src", correct: true }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "You are in the process of building a style sheet. You want to make sure that paragraphs inside of articles have a beige background. Using the dropdown arrow, choose the correct syntax for the line of code to make this happen.",
                answers: [
                    { text: "Article ~ p {background-color: beige}", correct: false },
                    { text: "Article > p {background-color: beige}", correct: true },
                    { text: "p > Article {background-color: beige}", correct: false },
                    { text: "Article + p {background-color: beige}", correct: false }
                ],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "multiple-choice",
                question: "What is the purpose of the controls attribute in an HTML <audio> or <video> element?",
                answers: [
                    { text: "It automatically starts the media when the page loads.", correct: false },
                    { text: "It adds built-in playback controls like play, pause, and volume.", correct: true },
                    { text: "It hides the media element from the webpage.", correct: false },
                    { text: "It changes the media file format for browser compatibility.", correct: false }
                ]
            },
                        
            // --- ORDER/SEQUENCE EXAMPLES (Type: order) ---
            {
                type: "order", 
                question: "Order the tags to correctly structure a basic HTML document (inside <body>).",
                correctOrder: ["<header>", "<main>", "<footer>"],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "order", 
                question: "In what order should the tags elements appear within the HTML document?",
                correctOrder: ["<!DOCTYPE html>", "<html>", "<head>", "<title> The title goes to the browser tab", "<body>", "</body>", "</html>"],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "order", 
                question: "Which of the following represents the correct conceptual sequence when applying the three core Flexbox properties to a container?",
                correctOrder: ["<display: flex;>", "<justify-content>", "<align-items>"],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "order",
                question: "Which of the following represents the correct order of the CSS box model from innermost to outermost?",
                correctOrder: ["Content", "Padding", "Border", "Margin"],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "order", 
                question: "Place the following tags in the Correct semantic order to structure a page order",
                correctOrder: ["<header>", "<h1>Title</h1>", "<nav>Links</nav>", "</header>"],
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "order", 
                question: "The correct conceptual order of CSS precedence (which rule wins when there's a conflict), from Highest Precedence (wins) to Lowest Precedence (loses), is:",
                correctOrder: ["Inline Style", "ID Selector", "Class Selector", "External Style Sheet"],
                state: 'unanswered',
                userAnswer: null
            },

            // --- DRAG AND DROP MATCHING QUESTIONS ---
            {
                type: "drag-drop",
                question: "Match each HTML form input element type with its primary functionality:",
                matches: {
                    "radio": "Allows selecting exactly one option from a mutually exclusive group",
                    "checkbox": "Allows selecting zero, one, or multiple independent choices",
                    "submit": "Initiates data transmission to the server handler",
                    "password": "Obscures characters typed into the text input box"
                },
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "drag-drop",
                question: "Match each semantic sectioning tag with its architectural purpose:",
                matches: {
                    "header": "Contains introductory contents, logos, or primary navigations",
                    "footer": "Contains authorship metadata, copyright notices, or secondary links",
                    "aside": "Represents contents tangentially related to surrounding copy",
                    "main": "Encapsulates the unique primary contents of the document"
                },
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "drag-drop",
                question: "Match each CSS layout declaration with its functional description:",
                matches: {
                    "display: none": "Hides the element and removes its structural space completely",
                    "visibility: hidden": "Hides the element but leaves its layout boundaries occupied",
                    "position: absolute": "Removes element from normal flow, positioned relative to closest ancestor",
                    "position: static": "Keeps element in normal flow, unaffected by top, right, bottom, or left"
                },
                state: 'unanswered',
                userAnswer: null
            },
            {
                type: "drag-drop",
                question: "Match each metadata element with its structural definition:",
                matches: {
                    "link": "Establishes a connection to external files like stylesheets",
                    "meta": "Represents machine-readable configuration rules or page descriptors",
                    "title": "Defines the text shown in the browser window titlebar",
                    "style": "Contains embedded formatting rules explicitly written in CSS"
                },
                state: 'unanswered',
                userAnswer: null
            }
        ];

        // Format Seconds into MM:SS
        function formatTime(seconds) {
            const m = Math.floor(seconds / 60);
            const s = seconds % 60;
            return `${m < 10 ? "0" : ""}${m}:${s < 10 ? "0" : ""}${s}`;
        }

        // Save Current Time
        function saveTime() {
            localStorage.setItem(TIMER_TIME_KEY, timeLeft.toString());
            localStorage.setItem(TIMER_START_KEY, new Date().getTime().toString());
        }

        // Update Clock and Style Warning
        function updateTimer() {
            if (timeLeft <= 0) {
                stopTimer();
                showScore(true);
                return;
            }
            timeLeft--;
            timerDisplay.textContent = formatTime(timeLeft);
            saveTime();
            
            // Warning style if time is 5 minutes (300 seconds) or less
            if (timeLeft <= WARNING_TIME) {
                timerDisplay.classList.add('time-warning');
            } else {
                timerDisplay.classList.remove('time-warning'); 
            }
        }
        
        function startTimer() {
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(updateTimer, 1000);
            isTimerStarted = true; 
        }
        
        function stopTimer() {
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = null;
        }
        
        function handleFirstAction() {
            if (!isTimerStarted) {
                startTimer();
            }
        }

        // Progress Persistence 
        function saveProgress() {
            const data = {
                questions: questions,
                currentQuestionIndex: currentQuestionIndex,
                score: score,
                isTimerStarted: isTimerStarted 
            };
            localStorage.setItem(QUIZ_PROGRESS_KEY, JSON.stringify(data));
        }

        function loadProgress() {
            const savedData = localStorage.getItem(QUIZ_PROGRESS_KEY);
            const savedTime = localStorage.getItem(TIMER_TIME_KEY);
            const savedStartTime = localStorage.getItem(TIMER_START_KEY);

            if (savedData) {
                const data = JSON.parse(savedData);
                questions = data.questions; 
                currentQuestionIndex = data.currentQuestionIndex;
                score = data.score;
                isTimerStarted = data.isTimerStarted || false; 
                
                if (savedTime && savedStartTime && isTimerStarted) {
                    const elapsed = Math.floor((new Date().getTime() - parseInt(savedStartTime)) / 1000);
                    let loadedTime = parseInt(savedTime) - elapsed;
                    
                    timeLeft = Math.max(0, loadedTime);
                    timerDisplay.textContent = formatTime(timeLeft);
                    
                    if (timeLeft <= 0) {
                        stopTimer();
                        if (questions.some(q => q.state !== 'answered')) {
                            showScore(true);
                            return true;
                        }
                    } else {
                        startTimer(); 
                    }
                } else {
                    if (savedTime) {
                        timeLeft = parseInt(savedTime);
                        timerDisplay.textContent = formatTime(timeLeft);
                    }
                }
                
                // Keep time status updated on progress load
                if (timeLeft <= WARNING_TIME && timeLeft > 0) {
                    timerDisplay.classList.add('time-warning');
                } else {
                    timerDisplay.classList.remove('time-warning'); 
                }
                return true; 
            }
            return false; 
        }
        
        function clearProgress() {
            localStorage.removeItem(QUIZ_PROGRESS_KEY);
            localStorage.removeItem(TIMER_TIME_KEY);
            localStorage.removeItem(TIMER_START_KEY);
        }

        // Shuffle Function
        function shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
        }

        // Start New/Cached Game Session
        function startGame(shouldLoad = true) {
            const finalScore = document.querySelector('.final-score');
            if (finalScore) { finalScore.remove(); } 
            
            const progressLoaded = shouldLoad && loadProgress();

            if (!progressLoaded) {
                currentQuestionIndex = 0;
                score = 0;
                questions = JSON.parse(JSON.stringify(initialQuestions)); 
                shuffleArray(questions);
                
                timeLeft = initialTime;
                timerDisplay.textContent = formatTime(timeLeft); 
                timerDisplay.classList.remove('time-warning');
                isTimerStarted = false; 
                clearProgress(); 
                saveProgress(); 
            }
            
            if (timeLeft > 0 && isTimerStarted && !timerInterval) {
                 startTimer();
            }
            
            isReviewMode = false;
            
            reviewArea.classList.add('hide');
            questionArea.classList.remove('hide');
            
            nextButton.textContent = 'Next Question';
            skipButton.style.display = 'block';
            
            if (progressLoaded) {
                // If progress was recovered, immediately skip instructions screen
                instructionsContainer.classList.add('hide');
                quizActiveBody.classList.remove('hide');
                
                // Restore student name
                studentName = localStorage.getItem(STUDENT_NAME_KEY) || "Anonymous Student";
                if (questions.every(q => q.state === 'answered')) return;
            }

            let startIndex = questions.findIndex(q => q.state !== 'answered');
            if (startIndex === -1) startIndex = 0;
            currentQuestionIndex = startIndex;
            
            showQuestion(currentQuestionIndex);
            updateScoreDisplay();
        }

        function updateScoreDisplay() {
             scoreDisplay.textContent = `Score: ${score} / ${questions.length}`;
        }

        function showQuestion(index = currentQuestionIndex) {
            currentQuestionIndex = index;
            resetState();
            let currentQuestion = questions[currentQuestionIndex];
            
            questionText.textContent = `Q${currentQuestionIndex + 1}: ${currentQuestion.question}`;

            if (currentQuestion.type === "multiple-choice") {
                renderMultipleChoice(currentQuestion);
            } else if (currentQuestion.type === "order") {
                renderOrderQuestion(currentQuestion);
            } else if (currentQuestion.type === "drag-drop") {
                renderDragDropQuestion(currentQuestion);
            }
            
            if (isReviewMode && currentQuestion.state !== 'answered') {
                 if (currentQuestion.type === "multiple-choice") {
                      skipButton.style.display = 'none'; 
                 } 
                 else if (currentQuestion.type === 'order' || currentQuestion.type === 'drag-drop') {
                      nextButton.onclick = handleReviewAnswered; 
                      nextButton.textContent = 'Save & Review';
                 }
            }
            else if (currentQuestion.state === 'answered') {
                disableInteractions(); 
                if (currentQuestion.type === "order") {
                    checkOrder(currentQuestion, true); 
                } else if (currentQuestion.type === "drag-drop") {
                    checkDragDrop(currentQuestion, true); 
                }
                nextButton.classList.remove('hide');
            }
        }

        function resetState() {
            nextButton.classList.add('hide');
            nextButton.onclick = handleNextButton; 
            
            skipButton.style.display = isReviewMode ? 'none' : 'block';

            while (answerButtons.firstChild) {
                answerButtons.removeChild(answerButtons.firstChild);
            }
        }

        // Question Formats Rendering
        function renderMultipleChoice(question) {
            question.answers.forEach((answer, index) => {
                const button = document.createElement('button');
                button.textContent = answer.text;
                button.classList.add('btn');
                button.dataset.index = index; 
                if (answer.correct) {
                    button.dataset.correct = answer.correct;
                }
                
                if (isReviewMode && question.state !== 'answered') {
                    button.addEventListener('click', selectReviewAnswer);
                } else {
                    button.addEventListener('click', selectAnswer);
                }
                answerButtons.appendChild(button);
                
                if (question.state === 'answered') {
                    if (question.userAnswer === index) {
                        button.classList.add(question.isCorrect ? 'correct' : 'wrong');
                    } else if (answer.correct) {
                        button.classList.add('correct');
                    }
                } else if (question.userAnswer === index) {
                     button.style.backgroundColor = '#3a3a3a'; 
                }
            });
        }
        
        function selectReviewAnswer(e) {
            selectAnswer(e); 
            handleReviewAnswered(); 
        }

        function renderOrderQuestion(question) {
            const optionsContainer = document.createElement('div');
            optionsContainer.id = 'order-options';
            optionsContainer.classList.add('order-container');
            
            let options;
            
            if (question.userAnswer && question.userAnswer.length > 0) {
                 options = question.userAnswer;
            } else {
                options = [...question.correctOrder];
                for (let i = options.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [options[i], options[j]] = [options[j], options[i]];
                }
            }

            options.forEach(text => {
                const item = document.createElement('div');
                item.textContent = text;
                item.classList.add('order-item', 'btn');
                item.draggable = true;
                item.addEventListener('dragstart', dragStart);
                item.addEventListener('dragend', dragEnd);
                optionsContainer.appendChild(item);
            });
            
            optionsContainer.addEventListener('dragover', dragOver);
            optionsContainer.addEventListener('drop', dropOrder);
            
            answerButtons.appendChild(optionsContainer);
            
            nextButton.textContent = 'Check Order';
            nextButton.classList.remove('hide');
            
            nextButton.onclick = () => {
                if (isReviewMode) {
                    checkOrder(question, false); 
                    handleReviewAnswered(); 
                } else {
                    checkOrder(question, false); 
                }
            }; 
        }

        function renderDragDropQuestion(question) {
            const dragDropContainer = document.createElement('div');
            dragDropContainer.id = 'drag-drop-area';
            dragDropContainer.addEventListener('dragover', dragOver);
            dragDropContainer.addEventListener('drop', dropMatch);
            
            const allItems = Object.keys(question.matches);
            
            let itemsInGrid = [];
            const userMatches = question.userAnswer || {};

            if (Object.keys(userMatches).length > 0) {
                 const matchedItems = Object.keys(userMatches);
                 itemsInGrid = allItems.filter(item => !matchedItems.includes(item));
            } else {
                 itemsInGrid = [...allItems].sort(() => Math.random() - 0.5);
            }

            let shuffledTargets = [...Object.values(question.matches)].sort(() => Math.random() - 0.5);
            
            itemsInGrid.forEach(tag => {
                const dragItem = createDragItem(tag, question.matches[tag]);
                dragDropContainer.appendChild(dragItem);
            });

            shuffledTargets.forEach(description => {
                const dropTarget = createDropTarget(description);
                dragDropContainer.appendChild(dropTarget);
                
                const matchedItemTag = Object.keys(userMatches).find(tag => userMatches[tag] === description);

                if (matchedItemTag) {
                    const matchedDragItem = createDragItem(matchedItemTag, question.matches[matchedItemTag]);
                    dropTarget.appendChild(matchedDragItem);
                }
            });

            answerButtons.appendChild(dragDropContainer);
            
            nextButton.textContent = 'Check Matches';
            nextButton.classList.remove('hide');

            nextButton.onclick = () => {
                if (isReviewMode) {
                    checkDragDrop(question, false); 
                    handleReviewAnswered(); 
                } else {
                    checkDragDrop(question, false); 
                }
            }; 
        }

        function createDragItem(tag, matchValue) {
            const dragItem = document.createElement('div');
            dragItem.textContent = tag;
            dragItem.classList.add('drag-item', 'btn');
            dragItem.draggable = true;
            dragItem.dataset.match = matchValue;
            dragItem.addEventListener('dragstart', dragStart);
            dragItem.addEventListener('dragend', dragEnd);
            return dragItem;
        }

        // Bookmark target accept matching setup
        function createDropTarget(description) {
            const dropTarget = document.createElement('div');
            dropTarget.textContent = description;
            dropTarget.classList.add('drop-target', 'btn');
            dropTarget.dataset.accept = description;
            dropTarget.addEventListener('dragover', dragOver);
            dropTarget.addEventListener('drop', dropMatch);
            return dropTarget;
        }

        // Answer verification
        function selectAnswer(e) {
            handleFirstAction(); 
            
            const selectedButton = e.target;
            const currentQuestion = questions[currentQuestionIndex];
            const selectedIndex = parseInt(selectedButton.dataset.index);

            currentQuestion.userAnswer = selectedIndex;
            currentQuestion.state = 'answered'; 

            const isCorrect = selectedButton.dataset.correct === 'true';

            if (currentQuestion.isCorrect === undefined) {
                 if (isCorrect) score++;
            } else if (currentQuestion.isCorrect === false && isCorrect) {
                 score++;
            } else if (currentQuestion.isCorrect === true && !isCorrect) {
                 score--;
            }
            currentQuestion.isCorrect = isCorrect;
            updateScoreDisplay();
            saveProgress(); 

            Array.from(answerButtons.children).forEach(button => {
                button.classList.add('disabled');
                if (button.dataset.correct === 'true') {
                    button.classList.add('correct');
                } else if (parseInt(button.dataset.index) === selectedIndex && !isCorrect) {
                    button.classList.add('wrong');
                }
            });
            
            disableInteractions();

            if (!isReviewMode) { 
                nextButton.classList.remove('hide');
                if (isQuizComplete()) {
                    nextButton.textContent = 'Final Score';
                }
            }
        }

        function checkOrder(question, isReview = false) {
            if (!isReview) {
                handleFirstAction(); 
            }
            
            const orderedItems = Array.from(document.querySelectorAll('#order-options .order-item'));
            const userOrder = orderedItems.map(item => item.textContent);
            const correctOrder = question.correctOrder;
            
            question.userAnswer = userOrder;
            question.state = 'answered';

            let isCorrect = userOrder.length === correctOrder.length && 
                            userOrder.every((value, index) => value === correctOrder[index]);

            if (!isReview) {
                if (question.isCorrect === undefined) {
                     if (isCorrect) score++;
                } else if (question.isCorrect === false && isCorrect) {
                     score++;
                } else if (question.isCorrect === true && !isCorrect) {
                     score--;
                }
                question.isCorrect = isCorrect;
                updateScoreDisplay();
                saveProgress(); 
            }

            if (!isReview) {
                if (isCorrect) {
                    questionText.innerHTML += " <br><span style='color: #4caf50; font-weight: bold;'>✅ Correct Order!</span>";
                } else {
                    questionText.innerHTML += " <br><span style='color: #f44336; font-weight: bold;'>❌ Incorrect.</span> <br>Correct sequence: <br>" + correctOrder.join(" → ");
                }
            }
            orderedItems.forEach((item, index) => {
                if (item.textContent !== correctOrder[index]) {
                    item.classList.add('wrong');
                } else {
                    item.classList.add('correct');
                }
            });

            if (!isReview && !isReviewMode) {
                nextButton.textContent = isQuizComplete() ? 'Final Score' : 'Next Question';
                nextButton.onclick = handleNextButton;
                disableInteractions();
            }
            
            if (!isReviewMode) {
                 disableInteractions();
            }
        }

        function checkDragDrop(question, isReview = false) {
             if (!isReview) {
                handleFirstAction(); 
            }
            
            let correctMatches = 0;
            const dropTargets = document.querySelectorAll('.drop-target');
            const totalPossible = Object.keys(question.matches).length;
            const userMatches = {};

            dropTargets.forEach(target => {
                const draggedItem = target.querySelector('.drag-item');
                const targetText = target.dataset.accept;
                
                if (draggedItem) {
                    const itemTag = draggedItem.textContent;
                    userMatches[itemTag] = targetText;
                    
                    if (draggedItem.dataset.match === targetText) {
                        target.classList.add('correct');
                        draggedItem.classList.add('correct');
                        correctMatches++;
                    } else {
                        target.classList.add('wrong');
                        draggedItem.classList.add('wrong');
                    }
                } else {
                    target.classList.add('wrong');
                }
            });
            
            question.userAnswer = userMatches;
            question.state = 'answered';

            let isCorrect = (correctMatches === totalPossible);
            
            if (!isReview) {
                if (question.isCorrect === undefined) {
                     if (isCorrect) score++;
                } else if (question.isCorrect === false && isCorrect) {
                     score++;
                } else if (question.isCorrect === true && !isCorrect) {
                     score--;
                }
                question.isCorrect = isCorrect;
                updateScoreDisplay();
                saveProgress(); 
            }
            
            document.querySelectorAll('#drag-drop-area > .drag-item').forEach(item => {
                item.classList.add('wrong');
            });

            if (!isReview && !isReviewMode) {
                if (isCorrect) {
                    questionText.innerHTML += " <br><span style='color: #4caf50; font-weight: bold;'>✅ All Matches Correct!</span>";
                } else {
                    questionText.innerHTML += ` <br><span style='color: #f44336; font-weight: bold;'>❌ You got ${correctMatches} of ${totalPossible} correct.</span>`;
                }
                nextButton.textContent = isQuizComplete() ? 'Final Score' : 'Next Question';
                nextButton.onclick = handleNextButton;
                disableInteractions();
            }
            
            if (!isReviewMode) {
                 disableInteractions();
            }
        }

        // Navigation
        function handleReviewAnswered() {
             showReviewScreen(); 
        }

        // Action when a student clicks Skip
        function handleSkip() {
            handleFirstAction(); 
            if (questions[currentQuestionIndex].state !== 'answered') {
                questions[currentQuestionIndex].state = 'skipped';
                saveProgress(); 
            }
            handleNextButton();
        }

        // Routing to next unanswered item
        function handleNextButton() {
            let nextIndex = questions.findIndex((q, i) => i > currentQuestionIndex && q.state !== 'answered');
            if (nextIndex === -1) {
                nextIndex = questions.findIndex((q, i) => i < currentQuestionIndex && q.state !== 'answered');
            }
            
            if (nextIndex !== -1) {
                showQuestion(nextIndex);
            } else {
                showReviewScreen(); 
            }
        }

        function isQuizComplete() {
            return questions.every(q => q.state === 'answered');
        }

        function showReviewScreen() {
            isReviewMode = true;
            questionArea.classList.add('hide');
            skipButton.style.display = 'none';
            
            reviewArea.classList.remove('hide');
            reviewButtonsContainer.innerHTML = '';
            
            nextButton.classList.remove('hide'); 
            nextButton.textContent = 'Submit Quiz';
            nextButton.onclick = () => showScore(false);
            
            let unansweredCount = questions.filter(q => q.state !== 'answered').length;
            
            const statusMessage = document.createElement('p');
            statusMessage.style.fontWeight = 'bold';
            if (unansweredCount > 0) {
                 statusMessage.textContent = `⚠️ You have ${unansweredCount} questions remaining. Click a red/yellow button to return and answer.`;
                 statusMessage.style.color = '#ff5252'; 
            } else {
                 statusMessage.textContent = '✅ All questions answered. Ready to submit!';
                 statusMessage.style.color = '#4caf50'; 
            }
            reviewButtonsContainer.appendChild(statusMessage);

            questions.forEach((q, originalIndex) => {
                const button = document.createElement('button');
                button.textContent = originalIndex + 1;
                button.classList.add('review-button');
                
                let statusClass;
                if (q.state === 'answered') {
                    statusClass = 'status-answered';
                    button.title = 'Answered';
                } else if (q.state === 'skipped') {
                    statusClass = 'status-skipped';
                    button.title = 'Skipped';
                } else {
                    statusClass = 'status-unanswered';
                    button.title = 'Unanswered';
                }
                
                button.classList.add(statusClass);

                button.onclick = () => {
                    reviewArea.classList.add('hide');
                    questionArea.classList.remove('hide');
                    showQuestion(originalIndex);
                };
                reviewButtonsContainer.appendChild(button);
            });
        }
        
        // Final results page evaluation with strict 84% passing threshold & Formspree Dispatch
        function showScore(timedOut = false) {
            stopTimer(); 
            resetState();
            questionArea.classList.add('hide');
            reviewArea.classList.add('hide');
            skipButton.style.display = 'none'; 
            
            const finalScoreMessage = document.createElement('div');
            finalScoreMessage.classList.add('final-score');
            
            // Calculates the dynamic percentage score
            const scorePercentage = Math.round((score / questions.length) * 100);
            const passed = scorePercentage >= 84;

            if (timedOut) {
                 finalScoreMessage.textContent = `Time's Up! Your Score is ${score} out of ${questions.length} (${scorePercentage}%)`;
                 finalScoreMessage.style.color = '#f44336';
            } else {
                 finalScoreMessage.textContent = `Quiz Complete! Your Final Score is ${score} out of ${questions.length} (${scorePercentage}%)`;
                 finalScoreMessage.style.color = passed ? '#4caf50' : '#f44336';
            }
            
            const feedbackText = document.createElement('p');
            feedbackText.style.fontSize = '1.25em';
            feedbackText.style.textAlign = 'center';
            feedbackText.style.fontWeight = 'bold';
            feedbackText.style.marginTop = '15px';
            feedbackText.style.lineHeight = '1.5';
            
            if (passed) {
                feedbackText.innerHTML = `🎉 Congratulations! You have successfully passed the Certiport benchmark threshold!`;
                feedbackText.style.color = '#4caf50';
            } else {
                feedbackText.innerHTML = `📚 You did not reach the passing threshold. Please review your material and try again to reach the 84% benchmark.`;
                feedbackText.style.color = '#f44336';
            }

            // Create safe submission status message element
            const statusBox = document.createElement('div');
            statusBox.id = "email-status-message";
            statusBox.textContent = "📤 Dispatched evaluation record to instructor...";
            statusBox.style.color = "#00bcd4";

            // Safely insert elements directly into active body to avoid parent insertion crashes
            quizActiveBody.appendChild(finalScoreMessage);
            quizActiveBody.appendChild(feedbackText);
            quizActiveBody.appendChild(statusBox);

            // ========================================================
            // SECURE DATA TRANSMISSION (Runs on completion/timeout)
            // ========================================================
            const payload = {
                student_name: studentName || "Anonymous Student",
                raw_score: `${score} / ${questions.length}`,
                percentage: `${scorePercentage}%`,
                passed_status: passed ? "PASSED (>= 84%)" : "FAILED (< 84%)",
                remaining_time: formatTime(timeLeft),
                timestamp_utc: new Date().toISOString()
            };

            // Only attempt fetch routing if Formspree ID has been entered in the config
            if (FORMSPREE_FORM_ID && FORMSPREE_FORM_ID !== "YOUR_FORMSPREE_FORM_ID_HERE") {
                fetch(`https://formspree.io/f/${FORMSPREE_FORM_ID}`, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                })
                .then(response => {
                    if (response.ok) {
                        statusBox.textContent = `✅ Results securely sent to instructor email (${INSTRUCTOR_EMAIL}).`;
                        statusBox.style.color = "#4caf50";
                    } else {
                        statusBox.textContent = "⚠️ Delivery failed. Please notify your instructor.";
                        statusBox.style.color = "#ff5252";
                    }
                })
                .catch(error => {
                    statusBox.textContent = "❌ Network error. Connection blocked.";
                    statusBox.style.color = "#ff5252";
                });
            } else {
                // If they haven't configured a Formspree ID key yet, fallback securely
                statusBox.textContent = "ℹ️ Results saved locally. (Formspree ID not configured in code).";
                statusBox.style.color = "#ffc107";
            }

            nextButton.textContent = 'Play Again';
            nextButton.classList.remove('hide');
            nextButton.onclick = () => {
                finalScoreMessage.remove();
                feedbackText.remove();
                statusBox.remove();
                instructionsContainer.classList.remove('hide');
                quizActiveBody.classList.add('hide');
                startGame(false);
            }; 
            clearProgress(); 
        }

        function disableInteractions() {
            Array.from(document.querySelectorAll('.btn')).forEach(el => {
                el.classList.add('disabled');
                el.draggable = false;
                el.removeEventListener('click', selectAnswer);
                el.removeEventListener('click', selectReviewAnswer);
                el.removeEventListener('dragstart', dragStart);
                el.removeEventListener('dragend', dragEnd);
            });
        }

        // Drag and Drop (with Auto-Save)
        function dragStart(e) {
            if (e.target.classList.contains('disabled')) {
                e.preventDefault();
                return;
            }
            draggedItem = e.target;
            e.dataTransfer.setData('text/plain', e.target.textContent);
            setTimeout(() => e.target.classList.add('dragging'), 0);
        }

        // Native dragend listener to make drops outside zones seamless
        function dragEnd(e) {
            e.target.classList.remove('dragging');
            draggedItem = null;
        }

        function dragOver(e) {
            e.preventDefault(); 
        }

        // Robust sequence sort handler
        function dropOrder(e) {
            e.preventDefault();
            if (!draggedItem) return;

            const container = document.getElementById('order-options');
            
            if (draggedItem.classList.contains('order-item')) {
                handleFirstAction(); 
                
                const targetElement = e.target.closest('.order-item');
                
                if (targetElement && targetElement !== draggedItem) {
                    const bounding = targetElement.getBoundingClientRect();
                    const offset = bounding.y + (bounding.height / 2);

                    if (e.clientY < offset) {
                        targetElement.parentNode.insertBefore(draggedItem, targetElement);
                    } else {
                        targetElement.parentNode.insertBefore(draggedItem, targetElement.nextSibling);
                    }
                } else if (e.target.id === 'order-options' || e.target.closest('#order-options')) {
                    container.appendChild(draggedItem);
                }
            }
            draggedItem.classList.remove('dragging');
            draggedItem = null;
            
            const currentQuestion = questions[currentQuestionIndex];
            const orderedItems = Array.from(document.querySelectorAll('#order-options .order-item'));
            currentQuestion.userAnswer = orderedItems.map(item => item.textContent);
            if(currentQuestion.state !== 'answered') {
                currentQuestion.state = 'skipped';
                saveProgress(); 
            }
        }

        // Fully protected crash-proof matching handler
        function dropMatch(e) {
            e.preventDefault();
            
            // CRASH SHIELD: If draggedItem is null, exit immediately
            if (!draggedItem) return;

            const target = e.target.closest('.drop-target');
            const dragDropArea = document.getElementById('drag-drop-area');

            if (draggedItem.classList.contains('drag-item')) {
                handleFirstAction(); 
                
                if (target) {
                    if (target.querySelector('.drag-item')) {
                        const existingItem = target.querySelector('.drag-item');
                        dragDropArea.appendChild(existingItem);
                    }
                    target.appendChild(draggedItem);
                } else {
                    dragDropArea.appendChild(draggedItem);
                }
            }
            
            draggedItem.classList.remove('dragging');
            draggedItem = null;

            const currentQuestion = questions[currentQuestionIndex];
            const userMatches = {};
            document.querySelectorAll('.drop-target').forEach(t => {
                const item = t.querySelector('.drag-item');
                if (item) {
                    userMatches[item.textContent] = t.dataset.accept;
                }
            });
            currentQuestion.userAnswer = userMatches;
            if(currentQuestion.state !== 'answered') {
                currentQuestion.state = 'skipped';
                saveProgress(); 
            }
        }
        
        // Event Listeners and Landing Navigation
        startExamButton.addEventListener('click', () => {
            studentName = studentNameInput.value.trim();
            if (!studentName) {
                alert("Please enter your name to start the final exam.");
                return;
            }
            localStorage.setItem(STUDENT_NAME_KEY, studentName);
            instructionsContainer.classList.add('hide');
            quizActiveBody.classList.remove('hide');
            startTimer();
        });

        skipButton.addEventListener('click', handleSkip);

        // Load or Start Quiz
        startGame();
    </script>
</body>
</html>
