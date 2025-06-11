import math
from collections import defaultdict


# Load words from file
def load_words(filename="words.txt"):
    with open(filename) as f:
        return [line.strip().lower() for line in f if len(line.strip()) == 5]


# Generate feedback pattern (e.g., "GYBBG")
def get_feedback(guess, target):
    feedback = ['B'] * 5
    guess_chars = list(guess)
    target_chars = list(target)

    # Green pass
    for i in range(5):
        if guess_chars[i] == target_chars[i]:
            feedback[i] = 'G'
            target_chars[i] = None

    # Yellow pass
    for i in range(5):
        if feedback[i] == 'B' and guess_chars[i] in target_chars:
            feedback[i] = 'Y'
            target_chars[target_chars.index(guess_chars[i])] = None

    return ''.join(feedback)


# Compute entropy of a guess against all remaining possible words
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


# Suggest best guess
def suggest_best_guess(possible_words, all_words):
    best_guess = None
    max_entropy = -1

    if len(possible_words)==1:
        return possible_words[0], 1

    for guess in all_words:
        entropy = compute_entropy(guess, possible_words)
        if entropy > max_entropy:
            max_entropy = entropy
            best_guess = guess

    return best_guess, max_entropy


def filter_possible_words(possible_words, guess, feedback):
    return [
        word for word in possible_words
        if get_feedback(guess, word) == feedback
    ]