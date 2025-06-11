from flask import Flask, request, redirect, url_for
from templates import render_wordle_template
from session import WordleSession

app = Flask(__name__)
app.secret_key = "your-secret-key"

# For demo: use a global session object (not thread-safe, but fine for single-user local use)
session_data = WordleSession()

def get_top_guess_words(top_guesses):
    # If top_guesses is a list of (word, entropy), return just the words
    if top_guesses and isinstance(top_guesses[0], (list, tuple)):
        return [g[0] for g in top_guesses]
    return top_guesses

@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    if request.method == "POST":
        selected_guess = request.form.get("selected_guess")
        if selected_guess:
            session_data.set_guess(selected_guess)
        else:
            feedback = request.form["feedback"].strip().upper()
            session_data.update_after_feedback(feedback, top_n=3)
            if feedback == "GGGGG":
                msg = f"🎉 Yay! Guessed in {session_data.tries} tries."
                return render_wordle_template(
                    guess=session_data.guess,
                    tries=session_data.tries,
                    message=msg,
                    possible_words=session_data.possible_words,
                    top_guesses=get_top_guess_words(session_data.top_guesses)
                )
            if len(session_data.possible_words) == 0:
                msg = "❌ Sorry, the word isn't in my vocabulary."
                return render_wordle_template(
                    guess=session_data.guess,
                    tries=session_data.tries,
                    message=msg,
                    possible_words=session_data.possible_words,
                    top_guesses=[]
                )
            if session_data.tries >= 6:
                msg = "😓 Oops, I failed in 6 tries!"
                return render_wordle_template(
                    guess=session_data.guess,
                    tries=session_data.tries,
                    message=msg,
                    possible_words=session_data.possible_words,
                    top_guesses=get_top_guess_words(session_data.top_guesses)
                )
    return render_wordle_template(
        guess=session_data.guess,
        tries=session_data.tries,
        message=msg,
        possible_words=session_data.possible_words,
        top_guesses=get_top_guess_words(session_data.top_guesses)
    )

@app.route("/reset")
def reset():
    session_data.reset()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
