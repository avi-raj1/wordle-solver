# Wordle Solver Web App

A Flask-based web application to help you solve Wordle puzzles interactively. Enter your guesses and feedback, and the app will suggest the best next guesses based on entropy.

## Features
- Interactive Wordle board UI
- Keyboard and mouse input
- Suggests top guesses based on entropy
- Tracks guess history and possible words
- Session-based state (per user)
- Reset session at any time

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the app**
   ```sh
   python app.py
   ```
4. **Open in your browser**
   - Visit [http://localhost:8080](http://localhost:8080)

## Usage
- Enter your guess and feedback (G = Green, Y = Yellow, B = Black/Gray) using the interactive board.
- The app will suggest the best next guesses.
- Click "Reset Session" to start over.

## File Structure
- `app.py` - Main Flask app
- `utils.py` - Wordle logic and helpers
- `templates.py` - HTML template for the app
- `word_lists/` - Word lists for allowed guesses
- `requirements.txt` - Python dependencies

## Notes
- For production, set a secure `app.secret_key` in `app.py`.
- The app uses session cookies for per-user state.

## License
MIT
