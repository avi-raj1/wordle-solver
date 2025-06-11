from flask import Flask, render_template_string, request, redirect, url_for
from utils import load_words, suggest_best_guess, filter_possible_words

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Required for sessions if you want to persist across requests

# Global session (basic – not for production)
session_data = {
    "tries": 0,
    "feedback": None,
    "all_words": load_words("words.txt"),
    "possible_words": [],
    "guess": "tares"
}
session_data["possible_words"] = session_data["all_words"].copy()

# Basic HTML template
TEMPLATE = """
<!doctype html>
<title>Wordle Helper</title>
<h2>Try {{ guess }} (Attempt {{ tries + 1 }})</h2>
<form method="POST">
    <label>Enter feedback (B=Black, Y=Yellow, G=Green):</label><br>
    <input name="feedback" maxlength="5" required autofocus>
    <button type="submit">Submit</button>
</form>
<p>{{ message }}</p>
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
            return render_template_string(TEMPLATE, guess=session_data["guess"], tries=session_data["tries"], message=msg)

        session_data["possible_words"] = filter_possible_words(
            session_data["possible_words"], session_data["guess"], feedback
        )

        if len(session_data["possible_words"]) == 0:
            msg = "❌ Sorry, the word isn't in my vocabulary."
            return render_template_string(TEMPLATE, guess=session_data["guess"], tries=session_data["tries"], message=msg)

        session_data["guess"], _ = suggest_best_guess(
            session_data["possible_words"], session_data["all_words"]
        )

        if session_data["tries"] >= 6:
            msg = "😓 Oops, I failed in 6 tries!"
            return render_template_string(TEMPLATE, guess=session_data["guess"], tries=session_data["tries"], message=msg)

    return render_template_string(TEMPLATE, guess=session_data["guess"], tries=session_data["tries"], message=msg)

@app.route("/reset")
def reset():
    session_data["tries"] = 0
    session_data["feedback"] = None
    session_data["possible_words"] = session_data["all_words"].copy()
    session_data["guess"] = "tares"
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
