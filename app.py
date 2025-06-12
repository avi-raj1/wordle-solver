from flask import Flask, request, redirect, url_for, session
from templates import render_wordle_template
from session import WordleSession
from utils import filter_possible_words, suggest_top_guesses

app = Flask(__name__)
app.secret_key = "your-secret-key"

def get_top_guess_words(top_guesses):
    if top_guesses and isinstance(top_guesses[0], (list, tuple)):
        return [g[0] for g in top_guesses]
    return top_guesses

def get_user_session():
    if 'wordle_session' not in session:
        ws = WordleSession()
        session['wordle_session'] = {
            'tries': ws.tries,
            'feedback': ws.feedback,
            'all_words': ws.all_words,
            'possible_words': ws.possible_words,
            'guess': ws.guess,
            'top_guesses': ws.top_guesses
        }
    return session['wordle_session']

def save_user_session(user_data):
    session['wordle_session'] = user_data

@app.route("/", methods=["GET", "POST"])
def index():
    msg = ""
    user_data = get_user_session()
    if request.method == "POST":
        selected_guess = request.form.get("selected_guess")
        if selected_guess:
            user_data['guess'] = selected_guess
        else:
            feedback = request.form["feedback"].strip().upper()
            user_data['tries'] += 1
            user_data['feedback'] = feedback
            user_data['possible_words'] = filter_possible_words(user_data['possible_words'], user_data['guess'], feedback)
            if feedback == "GGGGG":
                msg = f"🎉 Yay! Guessed in {user_data['tries']} tries."
                save_user_session(user_data)
                return render_wordle_template(
                    guess=user_data['guess'],
                    tries=user_data['tries'],
                    message=msg,
                    possible_words=user_data['possible_words'],
                    top_guesses=get_top_guess_words(user_data['top_guesses'])
                )
            if len(user_data['possible_words']) == 0:
                msg = "❌ Sorry, the word isn't in my vocabulary."
                save_user_session(user_data)
                return render_wordle_template(
                    guess=user_data['guess'],
                    tries=user_data['tries'],
                    message=msg,
                    possible_words=user_data['possible_words'],
                    top_guesses=[]
                )
            user_data['top_guesses'] = suggest_top_guesses(user_data['possible_words'], user_data['all_words'], top_n=5)
            user_data['guess'] = user_data['top_guesses'][0]
            if user_data['tries'] >= 6:
                msg = "😓 Oops, I failed in 6 tries!"
                save_user_session(user_data)
                return render_wordle_template(
                    guess=user_data['guess'],
                    tries=user_data['tries'],
                    message=msg,
                    possible_words=user_data['possible_words'],
                    top_guesses=get_top_guess_words(user_data['top_guesses'])
                )
    save_user_session(user_data)
    return render_wordle_template(
        guess=user_data['guess'],
        tries=user_data['tries'],
        message=msg,
        possible_words=user_data['possible_words'],
        top_guesses=get_top_guess_words(user_data['top_guesses'])
    )

@app.route("/reset")
def reset():
    session.pop('wordle_session', None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)