import nltk
from nltk.corpus import wordnet as wn
from nltk import pos_tag, word_tokenize
from random import choice

def init():
  nltk.download('wordnet')  # For accessing English words
  nltk.download('averaged_perceptron_tagger')  # For POS tagging
  nltk.download('averaged_perceptron_tagger_eng')
  nltk.download('punkt')  # Tokenizer models

# Function to get synonyms
def get_synonyms(word):
    synonyms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            lemma_name = lemma.name()
            word_tag = pos_tag([lemma_name])[0][1]
            if word_tag not in ['NNP', 'NNPS']:  # Proper nouns
                synonyms.append(lemma_name.replace("_"," "))
    return synonyms

def get_related_nouns(description):
    matching_words = []
    for synset in wn.all_synsets():
        if description in synset.definition():
            for lemma in synset.lemmas():
                lemma_name = lemma.name()
                word_tag = pos_tag([lemma_name])[0][1]
                if word_tag not in ['NN']: # nouns only 
                  continue
                if word_tag in ['NNP', 'NNPS']:  # no proper nouns
                  continue
                matching_words.append(lemma_name.replace("_"," "))
    return matching_words

'''
# Get all synsets (word senses) in WordNet
synsets = wn.all_synsets()

# Example: Get synonyms of "scary"
synonyms_of_scary = get_synonyms("scary")
print("Synonyms of scary:", synonyms_of_scary)
'''