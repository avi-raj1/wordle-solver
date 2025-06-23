
from utils import load_words, suggest_top_guesses, filter_possible_words

if __name__ == "__main__":
    tries, result, feedback = 0, 0, None
    all_words = load_words("word_lists/words_lite.txt")
    possible_words = all_words.copy()
    guess = 'tares' # hard-coding this because the first guess takes around 1 min to compute
    while feedback != 'GGGGG' and tries < 6:
        print(f'Generating best guess from {len(possible_words)} possible words. Some guesses: {possible_words[:10]}')
        print(f"Can you try: {guess}")
        feedback = input('Enter result (B=Black, G=Green, Y=Yellow, eg: YBGBY): ')
        possible_words = filter_possible_words(possible_words, guess, feedback)
        guess = suggest_top_guesses(possible_words, all_words, 1)[0]
        if possible_words == 0:
            print('Sorry, the word isnt in my vocabulary')
            break
        tries += 1

    if feedback == 'GGGGG':
        print(f'Yay!! Guessed in {tries} tries')
    elif tries == 6:
        print('Oops I failed')
    else:
        print(f"This word doesn't exist in my vocabulary of {len(all_words)} words")


