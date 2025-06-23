from flask import Flask, render_template_string, request, session, redirect, url_for
from utils import load_words, filter_possible_words, suggest_top_guesses

app = Flask(__name__)
app.secret_key = 'jlhbdfvhdvvkjklbhdfvlidvfljbhdf'  # Change this in production!

WORDS_FILE = 'word_lists/words_lite.txt'

TEMPLATE = """
<!doctype html>
<title>Wordle Solver</title>
<h2>Wordle Solver</h2>
<form method="post">
  <label>Enter your guess:</label>
  <input name="guess" maxlength="5" required>
  <label>Enter feedback (G/Y/B):</label>
  <input name="feedback" maxlength="5" required>
  <button type="submit">Submit</button>
</form>
<form method="get" action="/reset" style="margin-top:10px;">
  <button type="submit">Reset Session</button>
</form>
{% if guesses %}
  <h3>History</h3>
  <ul>
    {% for g, f in guesses %}
      <li>{{g}} : {{f}}</li>
    {% endfor %}
  </ul>
{% endif %}
{% if suggestions %}
  <h3>Top Suggestions</h3>
  <ul>
    {% for s in suggestions %}
      <li>{{s}}</li>
    {% endfor %}
  </ul>
{% endif %}
{% if possible_words %}
  <p>{{possible_words|length}} possible words left.</p>
{% endif %}
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'guesses' not in session:
        session['guesses'] = []

    guesses = session['guesses']

    if request.method == 'POST':
        guess = request.form['guess'].lower()
        feedback = request.form['feedback'].upper()
        guesses.append((guess, feedback))
        session['guesses'] = guesses

    # Recompute possible_words from guesses
    all_words = load_words(WORDS_FILE)
    possible_words = all_words
    for guess, feedback in guesses:
        possible_words = filter_possible_words(possible_words, guess, feedback)

    suggestions = []
    if possible_words:
        if len(guesses) == 0:
            suggestions = ['tares']
        else:
            suggestions = suggest_top_guesses(possible_words, all_words, 3)

    return render_template_string(
        TEMPLATE,
        guesses=guesses,
        suggestions=suggestions,
        possible_words=possible_words
    )

@app.route('/reset')
def reset():
    session.pop('guesses', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)