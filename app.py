from flask import Flask, render_template_string, request, session, redirect, url_for
from utils import load_words, filter_possible_words, suggest_top_guesses

app = Flask(__name__)
app.secret_key = 'khdvjhfvkjvhjkdvkjkjnjk'  # Change this in production!

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
    .keyboard { user-select: none; }
    .kb-row { display: flex; justify-content: center; margin: 4px 0; }
    .kb-key {
      background: #d3d6da; color: #222; border: none; border-radius: 4px;
      margin: 2px; padding: 0 12px; height: 44px; min-width: 36px;
      font-size: 1.1em; font-weight: bold; cursor: pointer; transition: background 0.2s;
      box-shadow: 0 1px 1px rgba(0,0,0,0.08);
    }
    .kb-key.kb-enter { min-width: 100px; max-width: 100px; }
    .kb-key.kb-back { min-width: 60px; max-width: 60px; }
    .kb-key.kb-green { background: #6aaa64; color: #fff; }
    .kb-key.kb-yellow { background: #c9b458; color: #fff; }
    .kb-key.kb-grey { background: #787c7e; color: #fff; }
    .kb-key:active { filter: brightness(0.9); }
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
    <button type="submit" class="submit-btn" id="submit-btn" disabled>Submit</button>
    <div class="keyboard" id="keyboard" style="margin: 30px auto 0 auto; max-width: 400px;">
      <div class="kb-row">
        <button type="button" class="kb-key" data-key="Q">Q</button>
        <button type="button" class="kb-key" data-key="W">W</button>
        <button type="button" class="kb-key" data-key="E">E</button>
        <button type="button" class="kb-key" data-key="R">R</button>
        <button type="button" class="kb-key" data-key="T">T</button>
        <button type="button" class="kb-key" data-key="Y">Y</button>
        <button type="button" class="kb-key" data-key="U">U</button>
        <button type="button" class="kb-key" data-key="I">I</button>
        <button type="button" class="kb-key" data-key="O">O</button>
        <button type="button" class="kb-key" data-key="P">P</button>
      </div>
      <div class="kb-row">
        <button type="button" class="kb-key" data-key="A">A</button>
        <button type="button" class="kb-key" data-key="S">S</button>
        <button type="button" class="kb-key" data-key="D">D</button>
        <button type="button" class="kb-key" data-key="F">F</button>
        <button type="button" class="kb-key" data-key="G">G</button>
        <button type="button" class="kb-key" data-key="H">H</button>
        <button type="button" class="kb-key" data-key="J">J</button>
        <button type="button" class="kb-key" data-key="K">K</button>
        <button type="button" class="kb-key" data-key="L">L</button>
      </div>
      <div class="kb-row">
        <button type="button" class="kb-key kb-enter" data-key="ENTER">ENTER</button>
        <button type="button" class="kb-key" data-key="Z">Z</button>
        <button type="button" class="kb-key" data-key="X">X</button>
        <button type="button" class="kb-key" data-key="C">C</button>
        <button type="button" class="kb-key" data-key="V">V</button>
        <button type="button" class="kb-key" data-key="B">B</button>
        <button type="button" class="kb-key" data-key="N">N</button>
        <button type="button" class="kb-key" data-key="M">M</button>
        <button type="button" class="kb-key kb-back" data-key="BACKSPACE">⌫</button>
      </div>
    </div>
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
    const submitBtn = document.getElementById('submit-btn');
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
    // Enable/disable submit button based on guessArr
    function updateSubmitBtn() {
      const isFilled = guessArr.join('').length === 5 && guessArr.every(l => /[A-Z]/.test(l));
      submitBtn.disabled = !isFilled;
    }
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
        updateSubmitBtn();
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
    // Keyboard click support
    document.querySelectorAll('.kb-key').forEach(btn => {
      btn.addEventListener('click', function() {
        const key = btn.dataset.key;
        if (key === 'ENTER') {
          if (!submitBtn.disabled) submitBtn.click();
        } else if (key === 'BACKSPACE') {
          // Find last filled tile
          let lastIdx = guessArr.slice().reverse().findIndex(l => l);
          if (lastIdx !== -1) {
            let idx = 4 - lastIdx;
            guessArr[idx] = '';
            document.querySelector(`.word-row[data-row='${activeRow}'] .tile[data-col='${idx}']`).textContent = '';
            focusTile(idx);
            updateSubmitBtn();
          }
        } else if (/^[A-Z]$/.test(key)) {
          // Find first empty tile
          let idx = guessArr.findIndex(l => !l);
          if (idx !== -1) {
            guessArr[idx] = key;
            document.querySelector(`.word-row[data-row='${activeRow}'] .tile[data-col='${idx}']`).textContent = key;
            focusTile(idx);
            updateSubmitBtn();
          }
        }
      });
    });

    // Update keyboard key colors based on guesses and feedback
    function updateKeyboardColors() {
      // Track best state for each letter: G > Y > B
      const letterStates = {};
      const stateRank = { 'G': 3, 'Y': 2, 'B': 1 };
      {% for g, f in guesses %}
        {% for i in range(5) %}
          (function() {
            var letter = '{{g[i]|upper}}';
            var fb = '{{f[i]}}';
            if (letter && /[A-Z]/.test(letter)) {
              if (!letterStates[letter] || stateRank[fb] > stateRank[letterStates[letter]]) {
                letterStates[letter] = fb;
              }
            }
          })();
        {% endfor %}
      {% endfor %}
      document.querySelectorAll('.kb-key').forEach(btn => {
        const letter = btn.textContent.trim();
        btn.classList.remove('kb-green', 'kb-yellow', 'kb-grey');
        if (letterStates[letter] === 'G') btn.classList.add('kb-green');
        else if (letterStates[letter] === 'Y') btn.classList.add('kb-yellow');
        else if (letterStates[letter] === 'B') btn.classList.add('kb-grey');
      });
    }
    updateKeyboardColors();
    // Initial state
    updateSubmitBtn();
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