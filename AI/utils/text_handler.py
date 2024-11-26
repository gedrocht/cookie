import re
import nltk
import inflect

# Download required NLTK resources if not already done
nltk.download('punkt')
nltk.download('punkt_tab')

# Initialize inflect engine for number-to-words conversion
p = inflect.engine()

def transform_text(text):
    # Tokenize the text into words and punctuation
    tokens = nltk.word_tokenize(text)
    transformed_tokens = []

    for token in tokens:
        # Convert acronyms (sequences of capital letters with or without dots)
        if re.fullmatch(r'([A-Z]\.?)+', token):
            # Strip periods and convert to lowercase letter names
            transformed_token = ' '.join(letter.lower() for letter in token if letter.isalpha())
        
        # Convert numbers into words (e.g., "123" -> "one hundred twenty-three")
        elif token.isdigit():
            number = int(token)
            transformed_token = p.number_to_words(number)

        # Leave other tokens unchanged
        else:
            transformed_token = token
        
        # Append transformed token to result list
        transformed_tokens.append(transformed_token)

    # Reassemble tokens into a single string
    transformed_text = ' '.join(transformed_tokens)
    return transformed_text

# Example usage
sample_text = "The S.C.P. protocol requires 123 units of 5V power."
transformed_text = transform_text(sample_text)
print(transformed_text)
