import requests

# Function to query an API for words matching a description
def find_words(description):
    api_url = f"https://api.datamuse.com/words?ml={description}&sp=????"
    response = requests.get(api_url)
    if response.status_code == 200:
        words = [word['word'] for word in response.json()]
        return words
    else:
        return []

while True:
    description = input("describe the word: ")
    four_letter_words = find_words(description)
    print(four_letter_words)