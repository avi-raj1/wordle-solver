from utils import load_words, suggest_top_guesses, filter_possible_words

class WordleSession:
    def __init__(self, wordlist_file="words_lite.txt", start_word="tares"):
        self.tries = 0
        self.feedback = None
        self.all_words = load_words(wordlist_file)
        self.possible_words = self.all_words.copy()
        self.guess = start_word
        self.top_guesses = [self.guess]

    def reset(self):
        self.tries = 0
        self.feedback = None
        self.possible_words = self.all_words.copy()
        self.guess = "tares"
        self.top_guesses = [self.guess]

    def update_after_feedback(self, feedback, top_n=3):
        self.tries += 1
        self.feedback = feedback
        self.possible_words = filter_possible_words(self.possible_words, self.guess, feedback)
        if len(self.possible_words) > 0:
            self.top_guesses = suggest_top_guesses(self.possible_words, self.all_words, top_n=top_n)
            self.guess = self.top_guesses[0]
        else:
            self.top_guesses = []

    def set_guess(self, guess):
        self.guess = guess
