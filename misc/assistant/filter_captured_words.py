import nltk
nltk.download('words')

from nltk.corpus import words

# Load list of common English words
common_words = set(words.words())

# Function to filter esoteric words and write back to the original file
def filter_esoteric_words(file_path):
    print(f"Processing {file_path}...")  # Debug message to show progress
    filtered_words = []
    
    # Read the file and filter words
    with open(file_path, 'r') as f:
        for line in f:
            word = line.strip()
            if word.lower() in common_words:  # Check if the word is common
                filtered_words.append(word)
    
    # Write the filtered words back to the original file
    with open(file_path, 'w') as f:
        for word in filtered_words:
            f.write(word + '\n')

    print(f"Finished processing {file_path}. {len(filtered_words)} words written.")  # Debug message
    return filtered_words

# List of files to process
files_to_process = [
    'plots.txt',
    'plot_moods.txt',
    'subplot_stakes_beginnings.txt',
    'subplot_stakes_ends.txt',
    'stakes.txt',
    'moods.txt',
    'stake_multipliers.txt',
    'subplots.txt'
]

# Process each file
for file_path in files_to_process:
    filter_esoteric_words(file_path)

print("All files processed.")
