
# return "You are a text filterer that takes in text and responds with a list of 1-7 objects mentioned in the text. Your response must only contain the list of objects."
# You will summarize and describe the emergency, then describe a set of simple pictograms, diagrams, and/or symbols that represents the emergency.
def _IMAGE_DESCRIBER():
    return '''
You are a text filterer that takes in an emergency announcement.
You will add visual descriptions of imagery representing the emergency described in the emergency announcement.
You will add visual descriptions of imagery representing the instructions given in the emergency announcement.
You will add visual descriptions of imagery representing the dangers described in the emergency announcement.
You will phrase your descriptions as though they are instructions of how to create the imagery you are describing.
'''

'''
You will rewrite the summary in your own words, shortening it by one tenth.
If you do not have enough space to include everything, you will omit a random detail to make room.
'''