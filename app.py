from flask import Flask, render_template_string, request, redirect, url_for
from utils import load_words, suggest_best_guess, filter_possible_words

app = Flask(__name__)
app.secret_key = "your-secret-key"

session_data = {
    "tries": 0,
    "feedback": None,
    "all_words": load_words("words.txt"),
    "possible_words": [],
    "guess": "tares"
}
session_data["possible_words"] = session_data["all_words"].copy()

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Wordle Helper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f4f8;
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }
        .container {
            background: #fff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
        }
        h1, h4, h6 {
            text-align: center;
        }
        input[type="text"], input[name="feedback"] {
            width: 100%;
            padding: 0.6rem;
            margin: 1rem 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 1rem;
        }
        button {
            width: 100%;
            padding: 0.6rem;
            background-color: #4CAF50;
            color: white;
            font-size: 1rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .feedback {
            margin-top: 1rem;
            font-weight: bold;
            text-align: center;
            color: #d32f2f;
        }
        .word-list {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        .word-badge {
            color: white;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            display: inline-block;
        }
        .color-0 { background-color: #007bff; }
        .color-1 { background-color: #28a745; }
        .color-2 { background-color: #ffc107; color: #212529; }
        .color-3 { background-color: #17a2b8; }
        .color-4 { background-color: #6f42c1; }
        .color-5 { background-color: #e83e8c; }
        .color-6 { background-color: #fd7e14; }
        .color-7 { background-color: #20c997; }
        .color-8 { background-color: #6610f2; }
        .color-9 { background-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <h4>Attempt #{{ tries + 1 }}</h4>
        <h6>Words remaining: {{ possible_words|length }}</h6>
        <div class="words-preview">
            Top words:
            <div class="word-list">
                {% for word in possible_words[:7] %}
                    <span class="word-badge color-{{ loop.index0 % 7 }}">{{ word }}</span>
                {% endfor %}
            </div>
        </div>
        <h1>Try guessing: <span style="color:#0077cc">{{ guess }}</span></h1>
        <form method="POST">
            <label for="feedback">Enter feedback (B = Black, Y = Yellow, G = Green):</label>
            <input name="feedback" maxlength="5" required autofocus placeholder="e.g. BYGBG">
            <button type="submit">Submit</button>
        </form>
        {% if message %}
            <div class="feedback">{{ message }}</div>
        {% endif %}
        <div style="text-align:center; margin-top:1rem;">
            <a href="{{ url_for('reset') }}">🔄 Reset</a>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    if request.method == "POST":
        feedback = request.form["feedback"].strip().upper()
        session_data["tries"] += 1
        session_data["feedback"] = feedback

        if feedback == "GGGGG":
            msg = f"🎉 Yay! Guessed in {session_data['tries']} tries."
            return render_template_string(
                TEMPLATE,
                guess=session_data["guess"],
                tries=session_data["tries"],
                message=msg,
                possible_words=session_data["possible_words"]
            )

        session_data["possible_words"] = filter_possible_words(
            session_data["possible_words"], session_data["guess"], feedback
        )

        if len(session_data["possible_words"]) == 0:
            msg = "❌ Sorry, the word isn't in my vocabulary."
            return render_template_string(
                TEMPLATE,
                guess=session_data["guess"],
                tries=session_data["tries"],
                message=msg,
                possible_words=session_data["possible_words"]
            )

        session_data["guess"], _ = suggest_best_guess(
            session_data["possible_words"], session_data["all_words"]
        )

        if session_data["tries"] >= 6:
            msg = "😓 Oops, I failed in 6 tries!"
            return render_template_string(
                TEMPLATE,
                guess=session_data["guess"],
                tries=session_data["tries"],
                message=msg,
                possible_words=session_data["possible_words"]
            )

    return render_template_string(
        TEMPLATE,
        guess=session_data["guess"],
        tries=session_data["tries"],
        message=msg,
        possible_words=session_data["possible_words"]
    )

@app.route("/reset")
def reset():
    session_data["tries"] = 0
    session_data["feedback"] = None
    session_data["possible_words"] = session_data["all_words"].copy()
    session_data["guess"] = "tares"
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
