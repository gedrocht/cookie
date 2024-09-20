import word_generator

def init_word_list(name, search_terms):
    found_words = []
    search_i = 0
    for term in search_terms:
        print(f"Searching for: '{term}' - {search_i+1}/{len(search_terms)} - {round(search_i/len(search_terms)*100)}%")
        search_i += 1
        related_words = word_generator.get_related_nouns(term)
        for word in related_words:
            if not found_words.__contains__(word):
                found_words.append(word)
    print(f"WORDS COLLECTED: {len(found_words)}")
    with open(f"{name}.txt", "w") as file:
        # Iterate through the list of strings
        for string in found_words:
            # Write each string to the file, followed by a newline character
            file.write(string + "\n")
    return found_words

print("Initializing word generator")
word_generator.init()
print("Generating file 1 of 7")
plot_moods = init_word_list("plot_moods", ['eldrich horror', 'world-ending events', 'unknown horror', 'menace', 'fearful confusion', 'supernatural threat', 'unpredictability', 'mortal terror', 'odd event', 'optimism', 'a surprising turn', 'a strange object', 'a strange individual', 'a strange group', 'a strange substance', 'a strange device', 'a strange weather phenomenon', 'a strange signal', 'a strange sound', 'a strange smell', 'a strange taste', 'contamination', 'radiation', 'illness', 'contageon', 'psychosis', 'energy', 'vehicles', 'vehicle', 'surprise', 'plan', 'military', 'police', 'mob', 'militia', 'attack', 'explosion', 'collapse', 'corruption', 'poison', 'plant', 'mold', 'salespeople', 'intrusions', 'trespassers', 'animals', 'creatures', 'imagery',  'symptoms', 'psychological warping', 'mind control', 'manipulation', 'running', 'whispering', 'invisible', 'haunting', 'intruding', 'gassing', 'inhalation', 'intoxication', 'brainwashing', 'murder', 'mass murder', 'acidic', 'mass hysteria', 'extinction', 'famine', 'war', 'plague', 'salespeople', 'visitors', 'guests', 'insects', 'fever', 'dust', 'rot', 'forces', 'betrayal', 'tricks', 'contracts', 'infernal contracts', 'unknown life forms'])
print("Generating file 2 of 7")
plots = init_word_list("plots", ['phenomenon', 'situations', 'crises', 'emergencies', 'happenings', 'events', 'mysteries', 'accidents', 'developments'])
print("Generating file 3 of 7")
stakes = init_word_list("stakes", ['tension', 'fear', 'danger', 'a threat', 'disruption', 'confusion', 'horror', 'dread', 'shock', 'madness', 'death', 'disease', 'societal collapse', 'restriction', 'capture', 'panic', 'fleeing', 'evacuation', 'destruction', 'disruption', 'unknown damage'])
print("Generating file 4 of 7")
subplots = init_word_list("subplots", ['phenomenon', 'situations', 'crises', 'emergencies', 'happenings', 'events', 'mysteries', 'accidents', 'developments'])
print("Generating file 5 of 7")
subplot_stakes_beginnings = init_word_list("subplot_stakes_beginnings", ['dangerous', 'unpredictable', 'surprising', 'unusual', 'apocalyptic', 'sudden', 'unknown', 'volatile', 'unplanned', 'accidental', 'hazardous', 'deadly'])
print("Generating file 6 of 7")
subplot_stakes_ends = init_word_list("subplot_stakes_ends", ['effects', 'side-effects', 'consequences', 'ramifications', 'implications', 'threats', 'phenomenon', 'results', 'symptoms', 'damage'])
print("Generating file 7 of 7")
stake_multipliers = init_word_list("stake_multipliers", ["insignificant", "noticable", "significant", "extremely significant", "dire", "unimaginable"])