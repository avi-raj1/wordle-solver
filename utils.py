import math
from collections import defaultdict


def load_words(filename="words.txt"):
    with open(filename) as f:
        return [line.strip().lower() for line in f if len(line.strip()) == 5]


def get_feedback(guess, target):
    feedback = ['B'] * 5
    guess_chars = list(guess)
    target_chars = list(target)

    for i in range(5):
        if guess_chars[i] == target_chars[i]:
            feedback[i] = 'G'
            target_chars[i] = None

    for i in range(5):
        if feedback[i] == 'B' and guess_chars[i] in target_chars:
            feedback[i] = 'Y'
            target_chars[target_chars.index(guess_chars[i])] = None

    return ''.join(feedback)


def compute_entropy(guess, possible_words):
    pattern_counts = defaultdict(int)

    for target in possible_words:
        pattern = get_feedback(guess, target)
        pattern_counts[pattern] += 1

    total = len(possible_words)
    entropy = 0

    for count in pattern_counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    return entropy


def suggest_top_guesses(possible_words, all_words, top_n=3):
    scored = [(word, compute_entropy(word, possible_words)) for word in all_words]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [word for word, _ in scored[:top_n]]


def filter_possible_words(possible_words, guess, feedback):
    return [
        word for word in possible_words
        if get_feedback(guess, word) == feedback
    ]
