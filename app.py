from flask import Flask, render_template_string, request, session, redirect, url_for
from utils import load_words, filter_possible_words, suggest_top_guesses

app = Flask(__name__)
app.secret_key = 'kvfjkeekfjkjefvnkdfvjfvkjfvnfvj'  # Change this in production!

WORDS_FILE = 'word_lists/words_lite.txt'

TEMPLATE = """
<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8'>
  <title>Wordle Solver</title>
  <style>
    body { font-family: Arial, sans-serif; background: #222; color: #eee; text-align: center; }
    .board { display: flex; flex-direction: column; align-items: center; margin: 30px 0; }
    .word-row { display: flex; margin: 4px 0; }
    .tile {
      width: 48px; height: 48px; margin: 2px;
      display: flex; align-items: center; justify-content: center;
      font-size: 2em; font-weight: bold;
      background: #3a3a3c; color: #fff; border-radius: 6px; cursor: pointer;
      border: 2px solid #555;
      transition: background 0.2s;
      user-select: none;
      text-transform: uppercase;
    }
    .tile.yellow { background: #c9b458; color: #fff; }
    .tile.green { background: #6aaa64; color: #fff; }
    .tile.grey { background: #3a3a3c; color: #fff; }
    .tile:focus { outline: 2px solid #fff; }
    .tile.locked { cursor: default; opacity: 0.7; }
    .suggestions, .history { margin: 20px auto; max-width: 400px; }
    .suggestions ul, .history ul { list-style: none; padding: 0; }
    .suggestions li, .history li { margin: 4px 0; }
    .reset-btn { margin-top: 20px; padding: 8px 20px; font-size: 1em; border-radius: 5px; border: none; background: #444; color: #fff; cursor: pointer; }
    .reset-btn:hover { background: #666; }
    .submit-btn { margin-top: 20px; padding: 8px 20px; font-size: 1em; border-radius: 5px; border: none; background: #6aaa64; color: #fff; cursor: pointer; }
    .submit-btn:hover { background: #599a54; }
    .input-row { margin: 20px 0; }
    .hidden { display: none; }
  </style>
</head>
<body>
  
  <h2>Wordle Solver</h2>
  <h3>Suggestions:</h3>
  <div class="suggestions">
    {% if suggestions %}
      <div style="margin-bottom: 18px;">
        {% for s in suggestions %}
          <span style="display:inline-block;background:#444;color:#fff;padding:8px 16px;margin:0 6px 6px 0;border-radius:6px;font-size:1.2em;font-weight:bold;letter-spacing:2px;">{{s.upper()}}</span>
        {% endfor %}
      </div>
    {% endif %}
  </div>
  <form id="guess-form" method="post" autocomplete="off" {% if guesses and guesses[-1][1] == 'GGGGG' %}style="display:none;"{% endif %}>
    <div class="board" id="board">
      {% for row in range(6) %}
        <div class="word-row" data-row="{{row}}">
          {% set guess = guesses[row][0] if row < guesses|length else '' %}
          {% set fb = guesses[row][1] if row < guesses|length else '' %}
          {% for col in range(5) %}
            <div class="tile {{'locked ' + ('green' if fb and fb[col]=='G' else 'yellow' if fb and fb[col]=='Y' else 'grey') if row < guesses|length else 'grey'}}" 
                 data-row="{{row}}" data-col="{{col}}" tabindex="0">
              {{ guess[col]|default('') if guess else '' }}
            </div>
          {% endfor %}
        </div>
      {% endfor %}
    </div>
    <input type="hidden" name="guess" id="guess-input">
    <input type="hidden" name="feedback" id="feedback-input">
    <button type="submit" class="submit-btn">Submit</button>
  </form>
  <form method="get" action="/reset">
    <button type="submit" class="reset-btn">Reset Session</button>
  </form>
  <div class="suggestions">
    {% if possible_words %}
      <p>{{possible_words|length}} possible words left.</p>
    {% endif %}
  </div>
  {% if guesses and guesses[-1][1] == 'GGGGG' %}
    <div style="margin: 24px 0; font-size: 1.5em; color: #6aaa64; font-weight: bold;">
      🎉 Congratulations! You solved it in {{ guesses|length }} attempts.
    </div>
  {% endif %}
  <script>
    // --- JS for interactive board ---
    const board = document.getElementById('board');
    const guessInput = document.getElementById('guess-input');
    const feedbackInput = document.getElementById('feedback-input');
    const guesses = {{ guesses|length }};
    let activeRow = guesses;
    let guessArr = ['', '', '', '', ''];
    let feedbackArr = ['B','B','B','B','B'];
    // Focus first tile of active row
    function focusTile(idx=0) {
      const tile = document.querySelector(`.word-row[data-row='${activeRow}'] .tile[data-col='${idx}']`);
      if(tile) tile.focus();
    }
    focusTile();
    // Handle keyboard input for active row
    document.addEventListener('keydown', function(e) {
      if (activeRow > 5) return;
      if (document.activeElement.classList.contains('tile') && document.activeElement.parentElement.dataset.row == activeRow) {
        let col = parseInt(document.activeElement.dataset.col);
        if (/^[a-zA-Z]$/.test(e.key)) {
          guessArr[col] = e.key.toUpperCase();
          document.activeElement.textContent = e.key.toUpperCase();
          if (col < 4) focusTile(col+1);
        } else if (e.key === 'Backspace') {
          guessArr[col] = '';
          document.activeElement.textContent = '';
          if (col > 0) focusTile(col-1);
        } else if (e.key === 'ArrowLeft' && col > 0) {
          focusTile(col-1);
        } else if (e.key === 'ArrowRight' && col < 4) {
          focusTile(col+1);
        }
      }
    });
    // Allow clicking to focus tile
    document.querySelectorAll(`.word-row[data-row='${activeRow}'] .tile`).forEach((tile, idx) => {
      tile.addEventListener('click', function() { tile.focus(); });
    });
    // Cycle color on single click for active row
    document.querySelectorAll(`.word-row[data-row='${activeRow}'] .tile`).forEach((tile, idx) => {
      tile.addEventListener('click', function() {
        if (tile.classList.contains('locked')) return;
        let state = feedbackArr[idx];
        if (state === 'B') { feedbackArr[idx] = 'Y'; tile.className = 'tile yellow'; }
        else if (state === 'Y') { feedbackArr[idx] = 'G'; tile.className = 'tile green'; }
        else { feedbackArr[idx] = 'B'; tile.className = 'tile grey'; }
      });
    });
    // On submit, set hidden fields
    document.getElementById('guess-form').addEventListener('submit', function(e) {
      guessInput.value = guessArr.join('').toLowerCase();
      feedbackInput.value = feedbackArr.join('');
    });
  </script>
</body>
</html>
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
    # Check if the last feedback is 'GGGGG' (success)
    if possible_words and (len(guesses) == 0 or guesses[-1][1] != 'GGGGG'):
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