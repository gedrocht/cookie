import nltk
from nltk import word_tokenize, pos_tag

# Download required resources if not already downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def extract_pos(words_list, target_pos):
    result = []
    for sentence in words_list:
        tokens = word_tokenize(sentence)  # Tokenize the sentence
        tagged = pos_tag(tokens)  # POS tag the tokens
        result.extend([word for word, pos in tagged if pos.startswith(target_pos)])  # Filter by POS
    return result

def get_verbs(words):
    return extract_pos(words, "VB")

def get_nouns(words):
    return extract_pos(words, "NN")

def get_adjectives(words):
    return extract_pos(words, "JJ")
