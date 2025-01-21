from random import random
from datetime import datetime
import os
import re
import hashlib
from colorama import Style, init
import spacy
from math import ceil

# Load the small English NLP model
nlp = spacy.load("en_core_web_sm")

def expand_state_abbreviations(text):
    state_abbreviation_map = {
        # US States
        "AL": "Alabama",
        "AK": "Alaska",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "FL": "Florida",
        "GA": "Georgia",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
        # Canadian Provinces
        "ON": "Ontario",
        "QC": "Quebec",
        "BC": "British Columbia",
        "AB": "Alberta",
        "MB": "Manitoba",
        "SK": "Saskatchewan",
        "NS": "Nova Scotia",
        "NB": "New Brunswick",
        "NL": "Newfoundland and Labrador",
        "PE": "Prince Edward Island",
        # Australian States
        "NSW": "New South Wales",
        "VIC": "Victoria",
        "QLD": "Queensland",
        "WA": "Western Australia",
        "SA": "South Australia",
        "TAS": "Tasmania",
        "ACT": "Australian Capital Territory",
        "NT": "Northern Territory"
    }
    
    doc = nlp(text)
    tokens = []
    for token in doc:
        # Replace state abbreviation if it is recognized as a proper noun, matches the map, and is part of a location entity
        if token.text in state_abbreviation_map and token.pos_ == "PROPN" and token.ent_type_ == "GPE":
            tokens.append(state_abbreviation_map[token.text])
        else:
            tokens.append(token.text)
    
    return " ".join(tokens)

def expand_measurements(text):
    measurement_map = {
        "in": "inches",
        "ft": "feet",
        "yd": "yards",
        "mi": "miles",
        "mm": "millimeters",
        "cm": "centimeters",
        "m": "meters",
        "km": "kilometers",
        "oz": "ounces",
        "lb": "pounds",
        "g": "grams",
        "kg": "kilograms",
        "ml": "milliliters",
        "l": "liters",
        "gal": "gallons",
        "K": "Kelvin",
        "°C": "degrees Celsius",
        "°F": "degrees Fahrenheit",
        "Pa": "Pascals",
        "kPa": "kilopascals",
        "MPa": "megapascals",
        "psi": "pounds per square inch",
        "atm": "atmospheres",
        "N": "Newtons",
        "kN": "kilonewtons",
        "J": "Joules",
        "kJ": "kilojoules",
        "W": "Watts",
        "kW": "kilowatts",
        "MW": "megawatts",
        "V": "Volts",
        "kV": "kilovolts",
        "A": "Amperes",
        "mA": "milliamperes",
        "Ω": "Ohms",
        "mol": "moles",
        "cd": "candela",
        "Hz": "Hertz",
        "kHz": "kilohertz",
        "MHz": "megahertz",
        "sq ft": "square feet",
        "sq m": "square meters",
        "ha": "hectares",
        "cc": "cubic centimeters",
        "cu ft": "cubic feet",
        "mph": "miles per hour",
        "km/h": "kilometers per hour",
        "eV": "electronvolts",
        "hp": "horsepower"
    }
    
    doc = nlp(text)
    tokens = []

    for token in doc:
        if token.text in measurement_map and token.nbor(-1).like_num and token.dep_ not in ["prep", "det"]:
            tokens.append(measurement_map[token.text])
        else:
            tokens.append(token.text)
    
    return " ".join(tokens)

def expand_text(text):
    text = expand_state_abbreviations(text)
    text = expand_measurements(text)
    return text

from difflib import SequenceMatcher

def clean_text(text):
    """
    Cleans the text by removing extra whitespace, punctuation, and converting to lowercase.
    """
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)  # Remove punctuation and special characters
    return text.strip().lower()

def compare_texts(text1, text2):
    """
    Compares two blocks of text and returns the percentage match.
    """
    cleaned_text1 = clean_text(text1)
    cleaned_text2 = clean_text(text2)
    
    similarity_ratio = SequenceMatcher(None, cleaned_text1, cleaned_text2).ratio()
    return round(similarity_ratio * 100, 2)

def roll(odds): 
    return odds > random()

def pick(arr):
    return arr[round(random()*len(arr)-1)]

def join(split, char):
    output = ""
    for i in range(0,len(split)):
        text = split[i]
        if len(text) == 0:
            continue
        output += text
        if i + 1 < len(split):
            output += char
    return output + char

def select_portion_of_text(progress, text):
    text_split = text.split(".")
    start = 0
    end = 0
    if progress < 0.5:
        end = (1-progress)*len(text_split)
        end = round((2*end + len(text_split)) / 3.0)
    else:
        start = (1-progress)*len(text_split)
        start = round(0.666*start) # haha, get it? like the devil
        end = len(text_split)-1
    return join(text_split[start:end], ". ").strip()

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

def create_directory(path):
    # Check if the directory already exists
    if not os.path.exists(path):
        try:
            # Create the directory
            os.makedirs(path)
        except OSError as e:
            pass
    else:
        pass

def text_to_rgb(text):
    hash_object = hashlib.md5(text.encode())
    hex_hash = hash_object.hexdigest()
    # Combine multiple parts of the hash to calculate RGB
    r = max((int(hex_hash[0:8], 16) % 256), 64)
    g = max((int(hex_hash[8:16], 16) % 256), 64)
    b = max((int(hex_hash[16:24], 16) % 256), 64)
    return (r, g, b)

def rgb_to_ansi(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def colorize_module_name(module_name):
    r, g, b = text_to_rgb(module_name)
    return f"[{rgb_to_ansi(r, g, b)}{module_name}{Style.RESET_ALL}]"

# Main log function
def log(msg, source, color):
    MSG_WIDTH = 64
    timestamp = f"[{get_timestamp()}]"
    if len(msg.strip()) == 0:
        return
    
    # Clean up message
    msg = msg.replace("\n", " ").replace("\r", " ")

    # Colorize the source identifier
    colorized_module_name = colorize_module_name(source)
    line_info = f"{timestamp} {colorized_module_name} "

    # Print long messages with proper formatting
    if len(msg) > MSG_WIDTH:
        blank_indent = ""
        for str_t in range(0,len(timestamp) + (2+len(f"[{source}]"))):
            blank_indent += " "

        num_message_parts = ceil(len(msg) / MSG_WIDTH)
        for i in range(0, num_message_parts):
            start_index = i * MSG_WIDTH
            end_index = (i+1) * MSG_WIDTH
            msg_part = msg[start_index:end_index]
            output_msg = ""
            
            if i == 0:
                output_msg += line_info
            else:
                output_msg += blank_indent
            
            output_msg += color + msg_part

            if i + 1 >= num_message_parts:
                output_msg += Style.RESET_ALL
            print(f"{output_msg}")
            # print(f"{timestamp}   {msg_part}{Style.RESET_ALL}")
    else:
        print(f"{line_info}{color}{msg}{Style.RESET_ALL}")


def split_string_by_length(input_string, segment_length):
    # Split the input string into segments of the specified length
    return [input_string[i:i + segment_length] for i in range(0, len(input_string), segment_length)]

def split_text(text):
    # for i, chunk in enumerate(chunks, 1):
    # Define a regular expression pattern to split on punctuation marks
    pattern = r'(?<=[.!?…:])\s+(?=[A-Z])'
    # Split the text based on the pattern
    chunks = re.split(pattern, text)
    return chunks

from datetime import datetime, timedelta
from typing import List, Optional

import time
from statistics import mean

def get_current_time():
    return int(time.time())

def get_duration(start_time: int, end_time: int):
    return end_time - start_time

def get_average_duration(times):
    durations = []
    for i, timestamp in enumerate(times):
        if i + 1 < len(times):
            durations.append(get_duration(timestamp, times[i+1]))
    return mean(durations)

def get_remaining_time(times, num_remaining):
    delay = get_average_duration(times)
    remaining = int(num_remaining * delay)
    
    future_time = datetime.now() + timedelta(seconds=remaining)

    return (str(timedelta(seconds=remaining)), future_time.strftime("%H:%M:%S"))