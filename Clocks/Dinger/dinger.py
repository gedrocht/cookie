import schedule
import datetime
import time
from playsound import playsound
from Talker import text_to_speech
from pattern.en import conjugate, INDICATIVE, PARTICIPLE, PAST, PRESENT, FUTURE, SINGULAR
import nltk
import math
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import threading
import csv
import os
import uuid

# Flask app definition
app = Flask(__name__)
CORS(app)

global audio_queue
audio_queue = []

_HOURS_OFFSET = 0

_DATA_SAVER = False

_WARNING_DELAY = 5
_NUM_WARNINGS = 3
_FOLLOWUP_DELAY = 5
_NUM_FOLLOWUPS = 20
_HOUR = "hour"
_MINUTE = "minute"
_WARNING = "warning"
_REMINDER = "reminder"
_TASK = "task"
_FOLLOWUP = "followup"
_HAS_FOLLOWUPS = "HAS_FOLLOWUP"
_AM = "AM"
_PM = "PM"
_COMPLETED = "COMPLETED"
_WHICH_DAYS = "WHICH_DAYS"
_DAY_FLAG = "DAY_FLAG"
_DAY_ID = "DAY_ID"
_DAY_NAME = "DAY_NAME"
_ID = "ID"
_SKIPPED = "SKIPPED"
_DELAY = "DELAY"
_RESOLUTION_TIME = "RESOLUTION_TIME"

_MONDAY =   {_DAY_FLAG:0b00000001, _DAY_ID:0, _DAY_NAME:"Monday"}
_TUESDAY =  {_DAY_FLAG:0b00000010, _DAY_ID:1, _DAY_NAME:"Tuesday"}
_WEDNESDAY= {_DAY_FLAG:0b00000100, _DAY_ID:2, _DAY_NAME:"Wednesday"}
_THURSDAY = {_DAY_FLAG:0b00001000, _DAY_ID:3, _DAY_NAME:"Thursday"}
_FRIDAY =   {_DAY_FLAG:0b00010000, _DAY_ID:4, _DAY_NAME:"Friday"}
_SATURDAY = {_DAY_FLAG:0b00100000, _DAY_ID:5, _DAY_NAME:"Saturday"}
_SUNDAY =   {_DAY_FLAG:0b01000000, _DAY_ID:6, _DAY_NAME:"Sunday"}
_DAY_OBJECTS = [_MONDAY, _TUESDAY, _WEDNESDAY, _THURSDAY, _FRIDAY, _SATURDAY, _SUNDAY]
_DAYS =     _MONDAY[_DAY_FLAG]   | _TUESDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG] | _THURSDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG] | _SATURDAY[_DAY_FLAG] | _SUNDAY[_DAY_FLAG]
_WEEKDAYS = _MONDAY[_DAY_FLAG]   | _TUESDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG] | _THURSDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG]
_WEEKEND =  _SATURDAY[_DAY_FLAG] | _SUNDAY[_DAY_FLAG]
_FLAGS = "FLAGS"

_EVEN_WEEKS_ONLY = 	    0b0000000000000001
_ODD_WEEKS_ONLY = 	    0b0000000000000010
_NO_FOLLOWUP = 		    0b0000000000000100
_LENGTH_FIVE_MINUTES = 	0b0000000000001000
_LENGTH_QUARTER_HOUR = 	0b0000000000010000
_LENGTH_HALF_HOUR =	    0b0000000000100000
_LENGTH_HOUR = 		    0b0000000001000000
_LENGTH_HOUR_AND_A_HALF=0b0000000010000000
_LENGTH_MULTIPLE_HOURS= 0b0000000100000000
_PRIORITY_LOW = 	    0b0000001000000000
_PRIORITY_MEDIUM = 	    0b0000010000000000
_PRIORITY_HIGH = 	    0b0000100000000000
_PRIORITY_EXTREME = 	0b0001000000000000
_MULTITASKABLE = 	    0b0010000000000000
_EXCLUSIVE = 		    0b0100000000000000
_DO_NOT_RESCHEDULE = 	0b1000000000000000

_TASK_LENGTHS = _LENGTH_FIVE_MINUTES | _LENGTH_QUARTER_HOUR | _LENGTH_HALF_HOUR | _LENGTH_HOUR | _LENGTH_HOUR_AND_A_HALF | _LENGTH_MULTIPLE_HOURS

_BING_BONG = "audio/bing_bong.wav"

current_shots_path = ""

def get_csv_path():
    now = datetime.datetime.now()
    # Filepath for the CSV file to store reminders
    csv_file_path = 'reminders_' + \
                        str(now.year)    + "-" + \
                    pad(str(now.month))  + "-" + \
                    pad(str(now.day)) + ".csv"
    return csv_file_path

def generate_shots_path():
    now = datetime.datetime.now()
    shots_file_path = 'shots_' + \
                        str(now.year)    + "-" + \
                    pad(str(now.month))  + "-" + \
                    pad(str(now.day)) + ".txt"
    return shots_file_path

def play_text_to_speech(input):
    output = text_to_speech(input)
    if len(output) > 0:
        print_log("Created new file \"" + output + "\"")

def generate_followup_phrase(phrase):
    tokens = nltk.word_tokenize(phrase)
    tagged = nltk.pos_tag(tokens)
    verbs = [word for word, pos in tagged if pos.startswith("V")]
    for identified_verb in verbs:
        tensed_verb = conjugate(identified_verb,
                                tense = PAST + PARTICIPLE,
                                number = SINGULAR,
                                person = 3,
                                mood = INDICATIVE)
        if not tensed_verb is None:
            phrase = phrase.replace(identified_verb, tensed_verb)

    return "Have you " + phrase + " yet?"

def play_audio(audio_to_play):
    log_output = ""
    text_to_speech_phrase = ""
    if len(audio_to_play) > 0:
        print_log("Playing audio files: " + str(audio_to_play))
    for file in audio_to_play:
        if file == _BING_BONG:
            playsound( file )
            log_output += "[" + file + "] "
        else:
            phrase = file
            if phrase.find("_") > -1:
                segments = phrase.split("_")
                is_followup = (segments[0] == "followup")
                phrase = phrase[len(segments[0])+1:]
                phrase = phrase.replace("_"," ")
                if is_followup:
                    phrase = generate_followup_phrase(phrase)
                else: 
                    phrase = "It's time to " + phrase + "."

            if len(text_to_speech_phrase) > 0:
                text_to_speech_phrase += ", "
            text_to_speech_phrase += phrase
            log_output += "[" + phrase + "] "
    if len(text_to_speech_phrase) > 0:
        play_text_to_speech(text_to_speech_phrase)
    return log_output

def pad( string ):
    string = str(string)
    if len(string) < 2:
        return "0" + string
    else:
        return string

def get_timestamp():
    now = datetime.datetime.now()
    return "[" + str(now.year)    + "." + \
             pad(str(now.month))  + "." + \
             pad(str(now.day))    + "." + \
             pad(str(now.hour))   + ":" + \
             pad(str(now.minute)) + ":" + \
             pad(str(now.second)) + "] "

def print_log(log_message):
    print(get_timestamp() + str(log_message))

def new_reminder(hour, minute, am_pm, days_of_week, reminder, flags=0b00000000):
    offset = 0
    if am_pm == _PM and hour < 12:
        offset = 12

    return {_ID: uuid.uuid4().time_low, _HOUR: hour + offset, _MINUTE:minute, _WHICH_DAYS:days_of_week,
            _REMINDER:reminder, _FLAGS:flags, _COMPLETED:False, _SKIPPED:False, _DELAY:0, _RESOLUTION_TIME:""}

def create_reminders():
    global reminders
    reminders = [
        new_reminder( 9, 30, _AM, _DAYS, "take out Kiwi", _PRIORITY_HIGH | _LENGTH_FIVE_MINUTES),
        new_reminder( 9, 45, _AM, _DAYS, "refill the birds' food", _PRIORITY_HIGH | _LENGTH_FIVE_MINUTES),
        
        new_reminder(10, 45, _AM, _DAYS, "brush your teeth", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR),
        new_reminder(10, 55, _AM, _TUESDAY[_DAY_FLAG], "attend sprint retrospective", _NO_FOLLOWUP | _PRIORITY_EXTREME | _LENGTH_HALF_HOUR | _ODD_WEEKS_ONLY | _DO_NOT_RESCHEDULE),

        new_reminder(11,  0, _AM, _MONDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG], "empty the roomba", _PRIORITY_LOW | _LENGTH_FIVE_MINUTES),
        new_reminder(11, 25, _AM, _WEEKDAYS, "attend daily stand-up", _NO_FOLLOWUP | _PRIORITY_EXTREME | _LENGTH_HALF_HOUR | _DO_NOT_RESCHEDULE),

        new_reminder(12,  0, _PM, _DAYS, "record your mood", _PRIORITY_MEDIUM | _LENGTH_FIVE_MINUTES),
        new_reminder(12, 30, _PM, _DAYS, "put away Kiwi", _PRIORITY_MEDIUM | _LENGTH_FIVE_MINUTES),

        new_reminder(12, 50, _PM, _THURSDAY[_DAY_FLAG], "take out the trash", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR),
        new_reminder(12, 50, _PM, _MONDAY[_DAY_FLAG], "clean the bathroom sink", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR | _EVEN_WEEKS_ONLY),
        new_reminder(12, 50, _PM, _MONDAY[_DAY_FLAG], "clip your nails", _PRIORITY_MEDIUM | _LENGTH_FIVE_MINUTES | _ODD_WEEKS_ONLY),
        new_reminder(12, 50, _PM, _TUESDAY[_DAY_FLAG], "change the birds' cage paper", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR | _EVEN_WEEKS_ONLY),
        new_reminder(12, 50, _PM, _TUESDAY[_DAY_FLAG], "clean the toilet", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR | _ODD_WEEKS_ONLY),
        new_reminder(12, 50, _PM, _WEDNESDAY[_DAY_FLAG], "empty the dishwasher", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR),

        new_reminder( 1, 20, _PM, _WEEKDAYS, "have lunch", _PRIORITY_HIGH | _LENGTH_HOUR),
        new_reminder( 2, 15, _PM, _WEEKEND, "have lunch", _PRIORITY_HIGH | _LENGTH_HOUR),

        new_reminder( 1, 50, _PM, _SATURDAY[_DAY_FLAG], "load and run the dishwasher", _PRIORITY_HIGH | _LENGTH_HALF_HOUR),
        new_reminder( 1, 55, _PM, _WEEKDAYS, "attend developer huddle", _NO_FOLLOWUP | _PRIORITY_EXTREME | _LENGTH_HOUR | _MULTITASKABLE | _DO_NOT_RESCHEDULE),

        new_reminder( 2, 35, _PM, _DAYS, "take out Ridley", _PRIORITY_HIGH | _LENGTH_FIVE_MINUTES | _DO_NOT_RESCHEDULE),
        new_reminder( 3,  0, _PM, _DAYS, "replace the birds' water", _PRIORITY_HIGH | _LENGTH_FIVE_MINUTES | _DO_NOT_RESCHEDULE),

        new_reminder( 3, 40, _PM, _WEEKDAYS, "brush your teeth", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR),
        new_reminder( 3, 55, _PM, _THURSDAY[_DAY_FLAG], "attend backlog refinement", _NO_FOLLOWUP | _PRIORITY_EXTREME | _LENGTH_HOUR | _DO_NOT_RESCHEDULE),

        new_reminder( 4,  0, _PM, _MONDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG], "apply to some jobs", _PRIORITY_EXTREME | _LENGTH_HALF_HOUR),
        new_reminder( 4,  0, _PM, _TUESDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG], "check job emails", _PRIORITY_EXTREME | _LENGTH_HALF_HOUR),
        new_reminder( 4, 15, _PM, _WEEKDAYS, "update your timesheet", _PRIORITY_EXTREME | _LENGTH_FIVE_MINUTES),

        new_reminder( 4, 50, _PM, _FRIDAY[_DAY_FLAG], "take out the trash", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR),
        new_reminder( 4, 50, _PM, _TUESDAY[_DAY_FLAG], "clean the bathroom sink", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR | _EVEN_WEEKS_ONLY),
        new_reminder( 4, 50, _PM, _WEDNESDAY[_DAY_FLAG], "change the birds' cage paper", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR | _EVEN_WEEKS_ONLY),
        new_reminder( 4, 50, _PM, _WEDNESDAY[_DAY_FLAG], "clean the toilet", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR | _ODD_WEEKS_ONLY),
        new_reminder( 4, 50, _PM, _THURSDAY[_DAY_FLAG], "empty the dishwasher", _PRIORITY_HIGH | _LENGTH_QUARTER_HOUR),

        new_reminder( 5, 10, _PM, _DAYS, "log your weight", _PRIORITY_LOW | _LENGTH_FIVE_MINUTES),
        new_reminder( 6, 10, _PM, _DAYS, "take out Kiwi", _PRIORITY_HIGH | _LENGTH_FIVE_MINUTES),
        
        new_reminder(12, 40, _PM, _WEEKEND, "have a shower", _PRIORITY_HIGH | _LENGTH_HOUR | _EXCLUSIVE),
        new_reminder( 2, 55, _PM, _MONDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG] | _THURSDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG], "have a shower", _PRIORITY_HIGH | _LENGTH_HOUR | _EXCLUSIVE),
        new_reminder( 2, 55, _PM, _TUESDAY[_DAY_FLAG] | _WEDNESDAY[_DAY_FLAG] | _THURSDAY[_DAY_FLAG] | _FRIDAY[_DAY_FLAG], "have a shower", _PRIORITY_HIGH | _LENGTH_HOUR | _EXCLUSIVE | _EVEN_WEEKS_ONLY),
        new_reminder(10,  0, _AM, _TUESDAY[_DAY_FLAG], "have a shower", _PRIORITY_HIGH | _LENGTH_HOUR | _EXCLUSIVE | _DO_NOT_RESCHEDULE | _ODD_WEEKS_ONLY),

        new_reminder( 7, 30, _PM, _DAYS, "finish drinking and have dinner", _PRIORITY_HIGH | _LENGTH_HOUR),

        new_reminder(10, 40, _PM, _DAYS, "finish eating and clean up", _PRIORITY_MEDIUM | _LENGTH_QUARTER_HOUR),
        new_reminder(10, 55, _PM, _DAYS, "take your melatonin and put on your fitbit", _PRIORITY_EXTREME | _LENGTH_FIVE_MINUTES | _DO_NOT_RESCHEDULE),
        new_reminder(11, 15, _PM, _DAYS, "brush your teeth", _PRIORITY_EXTREME | _LENGTH_QUARTER_HOUR)
    ]
    reminders = sorted(reminders, key=lambda x: (x[_HOUR], x[_MINUTE]))

def is_reminder_valid(weekday, week_number, reminder):
    if reminder[_COMPLETED] or reminder[_SKIPPED]:
        return False

    week_number_is_even = (week_number % 2) == 0
    if (reminder[_FLAGS] & _EVEN_WEEKS_ONLY and not week_number_is_even) or \
       (reminder[_FLAGS] & _ODD_WEEKS_ONLY and week_number_is_even):
        return False

    valid_day_of_week = False
    
    if reminder[_WHICH_DAYS] & (1 << weekday):
        return True
        
    return valid_day_of_week

def get_valid_reminders(weekday, week_number):
    valid_reminders = []

    for reminder in reminders:
        if is_reminder_valid(weekday, week_number, reminder):
            valid_reminders.append(reminder)
    
    return valid_reminders

def get_minutes_since_midnight(hour, minute):
    return hour * 60 + minute

def minutes_since_midnight_to_time(minutes_since_midnight):
    return (math.floor(minutes_since_midnight/60), minutes_since_midnight % 60)

def reminder_length_to_number(reminder_length):
    if reminder_length & _LENGTH_FIVE_MINUTES: return 5
    if reminder_length & _LENGTH_QUARTER_HOUR: return 15
    if reminder_length & _LENGTH_HALF_HOUR: return 30
    if reminder_length & _LENGTH_HOUR: return 60
    if reminder_length & _LENGTH_HOUR_AND_A_HALF: return 90
    if reminder_length & _LENGTH_MULTIPLE_HOURS: return 200

def get_task_finish_time(reminder):
    length_in_minutes = -1
    if _TASK_LENGTHS & reminder[_FLAGS]:
        length_in_minutes = reminder_length_to_number(reminder[_FLAGS])
    else:
        raise Exception("Task length not set")

    finish_hours = reminder[_HOUR]
    finish_minutes = reminder[_MINUTE] + length_in_minutes
    while finish_minutes >= 60:
        finish_hours += 1
        finish_minutes -= 60
    
    if finish_hours > 24 or (finish_hours == 24 and finish_minutes > 0):
        raise Exception("Multi-day tasks not yet supported")
    
    return (finish_hours, finish_minutes)

def get_compressed_reminders(hour, minute, weekday, week_number):
    compressed_reminders = []

    todays_reminders = get_valid_reminders(weekday, week_number)
    todays_reminders.reverse()
    following_task = None
    compression_start_dayminutes = get_minutes_since_midnight(hour, minute)

    for reminder in todays_reminders:    
        if compression_start_dayminutes > get_minutes_since_midnight(reminder[_HOUR], reminder[_MINUTE]):
            compressed_reminders.append(reminder)
            continue
        if reminder[_FLAGS] & _MULTITASKABLE or \
           reminder[_FLAGS] & _DO_NOT_RESCHEDULE:
            compressed_reminders.append(reminder)
            continue
        if following_task is None:
            following_task = reminder
            compressed_reminders.append(reminder)
            continue
        
        following_task_start_minutes = get_minutes_since_midnight(following_task[_HOUR], following_task[_MINUTE])
        new_task_start_minutes = -1
        if reminder[_FLAGS] & _TASK_LENGTHS:
            new_task_start_minutes = following_task_start_minutes - reminder_length_to_number(reminder[_FLAGS])
        else:
            raise Exception("Task length not set")
        (new_start_hour, new_start_minute) = minutes_since_midnight_to_time(new_task_start_minutes)
        reminder[_HOUR] = new_start_hour
        reminder[_MINUTE] = new_start_minute
        following_task = reminder
        compressed_reminders.append(reminder)
    
    compressed_reminders.reverse()
    compressed_reminders = sorted(reminders, key=lambda x: (x[_HOUR], x[_MINUTE]))
    return compressed_reminders

def reminder_to_string(reminder):
    (finish_hours, finish_minutes) = get_task_finish_time(reminder)

    output = pad(reminder[_HOUR]) + ":" + pad(reminder[_MINUTE]) + " - " + \
             pad(finish_hours) + ":" + pad(finish_minutes) + " " + \
             reminder[_REMINDER][0:100]

    return output

def phrase_minutes_for_humans(minutes):
    if minutes > 60:
        remaining_minutes = minutes % 60
        hours = math.floor(minutes / 60)
        plural_hours = hours != 1
        plural_minutes = remaining_minutes != 1
        phrase = str(hours) + " hour"
        if plural_hours:
            phrase += "s"
        if remaining_minutes > 0:
            phrase += " and " + str(remaining_minutes)
            if plural_minutes:
                phrase += "s"
        return phrase
    plural_minutes = minutes != 1
    phrase = str(minutes) + " minute"
    if plural_minutes:
        phrase += "s"
    return phrase

def get_delay(n):
  if n < 6: return [0,5,10,20,40,60][n]
  return 30*(n-2)
  '''
  if n == 0:
    return 0
  
  output = 0
  
  for x in range(2,n+2):
    output += 10 * math.log10(x) + 10
  return int(output - (output % 5))
  '''

def announce_time(hour, minute, weekday, week_number):
    if hour == 23 and minute == 59:
        for reminder in reminders:
            reminder[_SKIPPED] = True
            reminder[_RESOLUTION_TIME] = str(datetime.datetime.now())
    elif hour == 0 and minute == 0:
        load_reminders()

    global audio_queue
    audio_queue = []
    log = ""

    did_bing_bong = (minute % 15 == 0)

    if did_bing_bong:
        audio_queue.append(_BING_BONG)
        hour_string = (str(hour%12),"12")[hour==12 or hour==0 or hour==24]

        if minute == 0:
            audio_queue.append(hour_string + " o-clock")
        else:
            audio_queue.append( hour_string + ":" + pad(minute) )
    
    if minute == 0:
        audio_queue.append(_DAY_OBJECTS[weekday][_DAY_NAME].lower())

    for reminder in reminders:
        if not is_reminder_valid(weekday, week_number, reminder):
            continue
        
        delayed_hour = reminder[_HOUR] + reminder[_DELAY]
        if delayed_hour > 23:
            delayed_hour = 23

        if hour == delayed_hour and minute == reminder[_MINUTE]:
            if not did_bing_bong:
                did_bing_bong = True
                audio_queue.append(_BING_BONG)
            audio_queue.append(_TASK + "_" + reminder[_REMINDER])
        
        for i in range(0, _NUM_WARNINGS):
            warning_time_hours = delayed_hour
            warning_time_minutes = reminder[_MINUTE] - (int(math.pow(2,i))*_WARNING_DELAY)

            while warning_time_minutes < 0:
                warning_time_minutes += 60
                warning_time_hours -= 1
                while warning_time_hours < 0:
                    warning_time_hours += 24
            
            if hour == warning_time_hours and minute == warning_time_minutes:
                if not did_bing_bong:
                    did_bing_bong = True
                    audio_queue.append(_BING_BONG)
                
                phrase = reminder[_REMINDER].replace("_"," ")
                tokens = nltk.word_tokenize(phrase)
                tagged = nltk.pos_tag(tokens)
                verbs = [word for word, pos in tagged if pos.startswith("V")]
                for identified_verb in verbs:
                    tensed_verb = conjugate(identified_verb, tense=FUTURE)
                    if not tensed_verb is None:
                        phrase = phrase.replace(identified_verb, tensed_verb)
                
                warning_phrase = "It will be time to " + phrase + " in " + \
                                 phrase_minutes_for_humans(int(math.pow(2,i))*_WARNING_DELAY)

                audio_queue.append(warning_phrase)

        if not reminder[_FLAGS] & _NO_FOLLOWUP:
            for i in range(1, _NUM_FOLLOWUPS):
                followup_time_hours = delayed_hour
                # followup_time_minutes = reminder[_MINUTE] + (int(math.pow(2,i))*_FOLLOWUP_DELAY)
                followup_time_minutes = reminder[_MINUTE] + get_delay(i)
                while followup_time_minutes >= 60:
                    followup_time_minutes -= 60
                    followup_time_hours += 1
                    while followup_time_hours >= 24:
                        followup_time_hours -= 24
            
                if hour == followup_time_hours and minute == followup_time_minutes:
                    if not did_bing_bong:
                        did_bing_bong = True
                        audio_queue.append(_BING_BONG)
                    audio_queue.append(_FOLLOWUP + "_" + reminder[_REMINDER])

    log += play_audio(audio_queue)
    if len(log) > 0:
        print_log(log)

def _test_reminder_compression(hour, minute):
    now = datetime.datetime.now()
    create_reminders()
    valid_reminders = get_valid_reminders(now.weekday(), now.isocalendar().week)
    for reminder in valid_reminders:
        print(reminder_to_string(reminder))
    print("========================================")
    compressed_reminders = get_compressed_reminders(hour, minute, now.weekday(), now.isocalendar().week)
    for reminder in compressed_reminders:
        print(reminder_to_string(reminder))

def announce_current_time():
    now = datetime.datetime.now()
    announce_time(now.hour, now.minute, now.weekday(), now.isocalendar().week)

def list_reminders():
    for reminder in reminders:
        print(reminder_to_string(reminder))

def load_reminders():
    global reminders
    reminders = []
    data = read_reminders()
    if data is None:
        create_reminder_file()
        data = read_reminders()

    reminders = []
    for row in data:
        reminders.append(\
            {_ID: int(row[_ID]),\
             _HOUR: int(row[_HOUR]),\
             _MINUTE: int(row[_MINUTE]),\
             _WHICH_DAYS: int(row[_WHICH_DAYS]),\
             _REMINDER: row[_REMINDER],\
             _FLAGS: int(row[_FLAGS]),\
             _COMPLETED: row[_COMPLETED] == "True",\
             _SKIPPED: row[_SKIPPED] == "True",\
             _DELAY: int(row[_DELAY]),\
             _RESOLUTION_TIME: row[_RESOLUTION_TIME]
            }
        )
    reminders = sorted(reminders, key=lambda x: (x[_HOUR], x[_MINUTE]))

# Function to read reminders from the CSV file
def read_reminders():
    if not os.path.exists(get_csv_path()):
        return None
    with open(get_csv_path(), mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]

# Function to write a new reminder to the CSV file
def write_reminder(reminder):
    with open(get_csv_path(), mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=reminder.keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(reminder)

# Function to overwrite the entire CSV file (used for updating and deleting)
def overwrite_reminders(reminders):
    with open(get_csv_path(), mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=reminders[0].keys())
        writer.writeheader()
        writer.writerows(reminders)

# Flask routes for CRUD operations

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    global reminders
    load_reminders()
    return jsonify(reminders)

@app.route('/api/reminders/valid', methods=['GET'])
def get_reminders_valid():
    now = datetime.datetime.now()
    valid_reminders = get_valid_reminders(now.weekday(), now.isocalendar().week)
    return jsonify(valid_reminders)

@app.route('/api/reminders', methods=['POST'])
def add_reminder():
    reminder = request.json
    write_reminder(reminder)
    return jsonify({'status': 'success', 'message': 'Reminder added'})

@app.route('/api/reminders', methods=['PUT'])
def update_reminder():
    global reminders
    load_reminders()
    updated_reminder = request.json
    for i, reminder in enumerate(reminders):
        if reminder[_ID] == updated_reminder[_ID]:
            reminders[i] = updated_reminder
            overwrite_reminders(reminders)
            return jsonify({'status': 'success', 'message': 'Reminder updated'})
    return jsonify({'status': 'error', 'message': 'Reminder not found'})

@app.route('/api/reminders', methods=['DELETE'])
def delete_reminder():
    global reminders
    load_reminders()
    reminder_id = request.json[_ID]
    reminders = [reminder for reminder in reminders if reminder[_ID] != reminder_id]
    overwrite_reminders(reminders)
    return jsonify({'status': 'success', 'message': 'Reminder deleted'})

@app.route('/api/reminders/complete', methods=['POST'])
def complete_reminder():
    global reminders
    load_reminders()
    reminder_id = int(request.json[_ID])
    for reminder in reminders:
        if reminder[_ID] == reminder_id:
            reminder[_COMPLETED] = True
            reminder[_RESOLUTION_TIME] = str(datetime.datetime.now())
            overwrite_reminders(reminders)
            return jsonify({'status': 'success', 'message': 'Reminder marked as completed'})
    return jsonify({'status': 'error', 'message': 'Reminder not found'})

@app.route('/api/reminders/skip', methods=['POST'])
def skip_reminder():
    global reminders
    load_reminders()
    reminder_id = int(request.json[_ID])
    for reminder in reminders:
        if reminder[_ID] == reminder_id:
            reminder[_SKIPPED] = True
            reminder[_RESOLUTION_TIME] = str(datetime.datetime.now())
            overwrite_reminders(reminders)
            return jsonify({'status': 'success', 'message': 'Reminder marked as skipped'})
    return jsonify({'status': 'error', 'message': 'Reminder not found'})

@app.route('/api/reminders/add_delay', methods=['POST'])
def add_delay_reminder():
    global reminders
    load_reminders()
    reminder_id = int(request.json[_ID])
    for reminder in reminders:
        if reminder[_ID] == reminder_id:
            if reminder[_FLAGS] & _DO_NOT_RESCHEDULE:
                return jsonify({'status': 'error', 'message': 'Reminder cannot be rescheduled'})
            if reminder[_HOUR] + reminder[_DELAY] < 23:
                reminder[_DELAY] += 1
            overwrite_reminders(reminders)
            return jsonify({'status': 'success', 'message': 'Reminder delay has been increased'})
    return jsonify({'status': 'error', 'message': 'Reminder not found'})

@app.route('/api/reminders/subtract_delay', methods=['POST'])
def subtract_delay_reminder():
    global reminders
    load_reminders()
    reminder_id = int(request.json[_ID])
    for reminder in reminders:
        if reminder[_ID] == reminder_id:
            reminder[_DELAY] -= 1
            if reminder[_DELAY] < 0:
                reminder[_DELAY] = 0
            overwrite_reminders(reminders)
            return jsonify({'status': 'success', 'message': 'Reminder delay has been increased'})
    return jsonify({'status': 'error', 'message': 'Reminder not found'})

@app.route('/api/message', methods=['POST'])
def message():
    data = request.json
    return jsonify({'message': 'Hello, ' + data.get('name', 'World') + '!'})

# Special route to shut down the server
@app.route('/shutdown', methods=['POST'])
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@app.route('/api/shots', methods=['POST'])
def add_shot():
    global current_shots_path
    if len(current_shots_path) == 0:
        current_shots_path = generate_shots_path()
    with open(current_shots_path, 'a+') as file:
        # Write the current timestamp to the file on a new line
        file.write(f"{datetime.datetime.now()}\n")
    return jsonify({"status": "success", "message": "Shot has been added to log"})

@app.route('/api/shots', methods=["GET"])
def get_shots():
    global current_shots_path
    num_shots = 0
    if len(current_shots_path) == 0:
        current_shots_path = generate_shots_path()
    if os.path.exists(current_shots_path):
        with open(current_shots_path, 'r') as file:
            # Move back to the beginning of the file to count all lines
            file.seek(0)
            # Count the total number of lines
            num_shots = len(file.readlines())
    return jsonify(num_shots)

@app.route("/api/shots/reset", methods=["POST"])
def reset_shots():
    global current_shots_path
    current_shots_path = generate_shots_path()
    return jsonify({"status": "success", "message": "Shots for the day have been reset"})

def run_flask_app():
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000, threaded=True)

def create_reminder_file():
    global reminders
    create_reminders()
    now = datetime.datetime.now()
    reminders = get_valid_reminders(now.weekday(), now.isocalendar().week)
    reminders = sorted(reminders, key=lambda x: (x[_HOUR], x[_MINUTE]))
    overwrite_reminders(reminders)

if __name__ == "__main__":
    global reminders

    # Starting the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    
    load_reminders()
    list_reminders()

    if not _DATA_SAVER:
        nltk.download("averaged_perceptron_tagger", quiet=True)
        nltk.download("punkt", quiet=True)
    try:
        conjugate("initialize", tense=FUTURE)
    except Exception:
        pass # will fail the first time, every time
    
    print_log("Running. " + play_audio([_BING_BONG]))
    if not _DATA_SAVER:
        output = play_text_to_speech("Initialization complete.")
    
    announce_current_time()
    schedule.every(1).minutes.do(announce_current_time)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            if not _DATA_SAVER:
                play_text_to_speech("Shutting down.")
                time.sleep(0.4)
            # requests.post('http://localhost:5000/shutdown')  # Trigger the shutdown endpoint
            # flask_thread.join()  # Wait for the Flask thread to finish
            print("Flask server stopped.")
            # flask_thread.join()
            exit()
        except Exception as error:
            print_log("An error has occurred. Reinitializing.")
            print(error, type(error))
            play_text_to_speech("An error has occurred.")
            time.sleep(5)