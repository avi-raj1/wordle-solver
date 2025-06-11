from flask import render_template_string

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
        .reset-container {
            text-align: center;
            margin-top: 1.5rem;
        }
        .reset-button {
            text-decoration: none;
            background-color: #999;
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            font-weight: bold;
            font-size: 1rem;
            transition: background-color 0.3s ease;
            display: inline-block;
        }
        .reset-button:hover {
            background-color: #c62828;
        }
        .guess-options {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0;
            justify-content: center;
        }
        .guess-options form {
            flex-grow: 1;
        }
        .guess-button {
            background-color: #0077cc;
            color: white;
        }
        .guess-button:hover {
            background-color: #005fa3;
        }
        .selected {
            background-color: gold !important;
            color: #333 !important;
            border: 2px solid #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h4>Attempt #{{ tries + 1 }}</h4>
        <h6>Words remaining: {{ possible_words|length }}</h6>
        <div class="words-preview">
            Some of remaining words:
            <div class="word-list">
                {% for word in possible_words[:7] %}
                    <span class="word-badge color-{{ loop.index0 % 10 }}">{{ word }}</span>
                {% endfor %}
            </div>
        </div>
        <h1>Try guessing:</h1>
        <div class="guess-options">
            {% for option in top_guesses %}
                <form method="POST">
                    <input type="hidden" name="selected_guess" value="{{ option }}">
                    <button type="submit" class="guess-button {% if option == guess %}selected{% endif %}">
                        {{ option }}
                    </button>
                </form>
            {% endfor %}
        </div>
        <form method="POST">
            <label for="feedback">Enter feedback (B = Black, Y = Yellow, G = Green):</label>
            <input name="feedback" maxlength="5" required autofocus placeholder="e.g. BYGBG">
            <button type="submit">Submit Feedback</button>
        </form>
        {% if message %}
            <div class="feedback">{{ message }}</div>
        {% endif %}
        <div class="reset-container">
            <a href="{{ url_for('reset') }}" class="reset-button"> Reset</a>
        </div>
    </div>
</body>
</html>
"""

def render_wordle_template(**context):
    return render_template_string(TEMPLATE, **context)
