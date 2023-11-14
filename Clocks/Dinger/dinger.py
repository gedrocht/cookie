import schedule
import datetime
import time
from playsound import playsound
from Talker import text_to_speech
from pattern.en import conjugate, INDICATIVE, PARTICIPLE, PAST, PRESENT, FUTURE, SINGULAR
import nltk
import math

global audio_queue
audio_queue = []

_OFFSET = 1

_DATA_SAVER = False

_WARNING_DELAY = 5
_NUM_WARNINGS = 3
_FOLLOWUP_DELAY = 5
_NUM_FOLLOWUPS = 4
_HOUR = "hour"
_MINUTE = "minute"
_WARNING = "warning"
_REMINDER = "reminder"
_TASK = "task"
_FOLLOWUP = "followup"
_HAS_FOLLOWUPS = "HAS_FOLLOWUP"
_AM = "AM"
_PM = "PM"
_WHICH_DAYS = "WHICH_DAYS"
_DAY_ID = "DAY_ID"
_DAY_NAME = "DAY_NAME"

_MONDAY = {_DAY_ID:0, _DAY_NAME:"Monday"}
_TUESDAY = {_DAY_ID:1, _DAY_NAME:"Tuesday"}
_WEDNESDAY = {_DAY_ID:2, _DAY_NAME:"Wednesday"}
_THURSDAY = {_DAY_ID:3, _DAY_NAME:"Thursday"}
_FRIDAY = {_DAY_ID:4, _DAY_NAME:"Friday"}
_SATURDAY = {_DAY_ID:5, _DAY_NAME:"Saturday"}
_SUNDAY = {_DAY_ID:6, _DAY_NAME:"Sunday"}
_DAYS = [_MONDAY, _TUESDAY,
         _WEDNESDAY, _THURSDAY,
         _FRIDAY, _SATURDAY,
         _SUNDAY]
_WEEKDAYS = [_MONDAY, _TUESDAY,
             _WEDNESDAY, _THURSDAY,
             _FRIDAY]

_WEEKEND = [_SATURDAY, _SUNDAY]
_FLAGS = "FLAGS"
_EVEN_WEEKS_ONLY = "EVEN_WEEKS_ONLY"
_ODD_WEEKS_ONLY = "ODD_WEEKS_ONLY"
_NO_FOLLOWUP = False

_LENGTH_FIVE_MINUTES = "LENGTH_FIVE_MINUTES"
_LENGTH_QUARTER_HOUR = "LENGTH_QUARTER_HOUR"
_LENGTH_HALF_HOUR = "LENGTH_HALF_HOUR"
_LENGTH_HOUR = "LENGTH_HOUR"
_LENGTH_HOUR_AND_A_HALF = "LENGTH_HOUR_AND_A_HALF"
_LENGTH_MULTIPLE_HOURS = "LENGTH_MULTIPLE_HOURS"

_TASK_LENGTHS = [
    _LENGTH_FIVE_MINUTES, 
    _LENGTH_QUARTER_HOUR, 
    _LENGTH_HALF_HOUR, 
    _LENGTH_HOUR, 
    _LENGTH_HOUR_AND_A_HALF, 
    _LENGTH_MULTIPLE_HOURS
]

_PRIORITY_LOW = "PRIORITY_LOW"
_PRIORITY_MEDIUM = "PRIORITY_MEDIUM"
_PRIORITY_HIGH = "PRIORITY_HIGH"
_PRIORITY_EXTREME = "PRIORITY_EXTREME"

_MULTITASKABLE = "MULTITASKABLE"
_EXCLUSIVE = "EXCLUSIVE"
_DO_NOT_RESCHEDULE = "SET_TIME"

_BING_BONG = "audio/bing_bong.wav"

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

def new_reminder(hour, minute, am_pm, days_of_week, reminder, has_followup=True, flags=[], followup_only=False):
    offset = 0
    if am_pm == _PM and hour < 12:
        offset = 12
    
    if not type(days_of_week) is list:
        print_log("Warning: Non-list passed to new_reminder as days_of_week")
        days_of_week = [days_of_week]

    return {_HOUR: hour + offset, _MINUTE:minute, _WHICH_DAYS:days_of_week, 
            _REMINDER:reminder, _HAS_FOLLOWUPS:has_followup, _FLAGS:flags}

def create_reminders():
    global reminders
    reminders = [
        new_reminder( 9, 30, _AM, _DAYS, "take out Kiwi", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_FIVE_MINUTES, _DO_NOT_RESCHEDULE]),
        
        new_reminder(10, 35, _AM, _DAYS, "brush your teeth", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),

        new_reminder(11,  0, _AM,[_MONDAY, _WEDNESDAY, _FRIDAY], "empty the roomba", _FOLLOWUP, [_PRIORITY_LOW, _LENGTH_FIVE_MINUTES]),
        new_reminder(11,  0, _AM, [_TUESDAY], "attend sprint retrospective", _NO_FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HALF_HOUR, _ODD_WEEKS_ONLY, _DO_NOT_RESCHEDULE]),
        new_reminder(11, 30, _AM, _WEEKDAYS, "attend daily stand-up", _NO_FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HALF_HOUR, _DO_NOT_RESCHEDULE]),

        new_reminder(12, 30, _PM, _DAYS, "put away Kiwi and deal with the birds' food and water", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_FIVE_MINUTES, _DO_NOT_RESCHEDULE]),
        new_reminder(12, 35, _PM, _DAYS, "record your mood", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_FIVE_MINUTES]),
        new_reminder(12, 40, _PM, _WEEKEND, "have a shower", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HOUR, _EXCLUSIVE]),
        new_reminder(12, 50, _PM, [_THURSDAY], "take out the trash", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),
        new_reminder(12, 50, _PM, [_MONDAY], "clean the bathroom sink", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR, _EVEN_WEEKS_ONLY]),
        new_reminder(12, 50, _PM, [_MONDAY], "clip your nails", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_FIVE_MINUTES, _ODD_WEEKS_ONLY]),
        new_reminder(12, 50, _PM, [_TUESDAY], "change the birds' cage paper", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_QUARTER_HOUR, _EVEN_WEEKS_ONLY]),
        new_reminder(12, 50, _PM, [_TUESDAY], "clean the toilet", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_QUARTER_HOUR, _ODD_WEEKS_ONLY]),
        new_reminder(12, 50, _PM, [_WEDNESDAY], "empty the dishwasher", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_QUARTER_HOUR]),
        # new_reminder(12, 50, _PM, [_FRIDAY], "clean pots and pans", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_QUARTER_HOUR]),

        new_reminder( 1, 20, _PM, _WEEKDAYS, "have lunch", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HOUR]),
        new_reminder( 1, 50, _PM, [_SATURDAY], "load and run the dishwasher", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HALF_HOUR]),
        # new_reminder( 2, 30, _PM, [_FRIDAY], "put away pots and pans", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),

        new_reminder( 2, 15, _PM, _WEEKEND, "have lunch", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HOUR]),
        new_reminder( 2,  0, _PM, _WEEKDAYS, "attend developer huddle", _NO_FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HOUR, _MULTITASKABLE, _DO_NOT_RESCHEDULE]),
        new_reminder( 2, 20, _PM, _WEEKDAYS, "brush your teeth", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),
        new_reminder( 2, 35, _PM, _DAYS, "take out Ridley", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_FIVE_MINUTES, _DO_NOT_RESCHEDULE]),

        new_reminder( 3, 15, _PM, _WEEKDAYS, "update your timesheet", _FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_FIVE_MINUTES]),

        new_reminder( 4,  0, _PM, [_MONDAY, _WEDNESDAY], "apply to some jobs", _FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HALF_HOUR]),
        new_reminder( 4,  0, _PM, [_TUESDAY, _FRIDAY], "check job emails", _FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HALF_HOUR]),
        new_reminder( 4,  0, _PM, [_THURSDAY], "attend backlog refinement", _NO_FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_HOUR, _DO_NOT_RESCHEDULE]),

        new_reminder( 6, 10, _PM, _DAYS, "take out Kiwi", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_FIVE_MINUTES, _DO_NOT_RESCHEDULE]),
        new_reminder( 6, 15, _PM, _WEEKDAYS, "have a shower", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HOUR, _EXCLUSIVE]),

        new_reminder( 7, 30, _PM, _DAYS, "have dinner", _FOLLOWUP, [_PRIORITY_HIGH, _LENGTH_HOUR]),

        new_reminder(10, 40, _PM, _DAYS, "finish eating and drinking", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),
        new_reminder(10, 55, _PM, _DAYS, "take your melatonin", _FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_FIVE_MINUTES, _DO_NOT_RESCHEDULE]),
        new_reminder(11,  5, _PM, _DAYS, "clean up", _FOLLOWUP, [_PRIORITY_MEDIUM, _LENGTH_QUARTER_HOUR]),

        new_reminder(11, 20, _PM, _DAYS, "brush your teeth", _FOLLOWUP, [_PRIORITY_EXTREME, _LENGTH_QUARTER_HOUR])
    ]

def is_reminder_valid(weekday, week_number, reminder):
    week_number_is_even = (week_number % 2) == 0
    for flag in reminder[_FLAGS]:
        if (flag == _EVEN_WEEKS_ONLY and not week_number_is_even) or \
           (flag == _ODD_WEEKS_ONLY and week_number_is_even):
            return False

    valid_day_of_week = False
    for day_object in reminder[_WHICH_DAYS]:
        if day_object[_DAY_ID] == weekday:
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
    if reminder_length == _LENGTH_FIVE_MINUTES: return 5
    if reminder_length == _LENGTH_QUARTER_HOUR: return 15
    if reminder_length == _LENGTH_HALF_HOUR: return 30
    if reminder_length == _LENGTH_HOUR: return 60
    if reminder_length == _LENGTH_HOUR_AND_A_HALF: return 90
    if reminder_length == _LENGTH_MULTIPLE_HOURS: return 200

def get_task_finish_time(reminder):
    length_in_minutes = -1
    for flag in reminder[_FLAGS]:
        if _TASK_LENGTHS.__contains__(flag):
            length_in_minutes = reminder_length_to_number(flag)
            break
    if length_in_minutes == -1:
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
        if reminder[_FLAGS].__contains__(_MULTITASKABLE) or \
           reminder[_FLAGS].__contains__(_DO_NOT_RESCHEDULE):
            compressed_reminders.append(reminder)
            continue
        if following_task is None:
            following_task = reminder
            compressed_reminders.append(reminder)
            continue
        
        following_task_start_minutes = get_minutes_since_midnight(following_task[_HOUR], following_task[_MINUTE])
        new_task_start_minutes = -1
        for flag in reminder[_FLAGS]:
            if _TASK_LENGTHS.__contains__(flag):
                new_task_start_minutes = following_task_start_minutes - reminder_length_to_number(flag)
                break
        if new_task_start_minutes == -1:
            raise Exception("Task length not set")
        (new_start_hour, new_start_minute) = minutes_since_midnight_to_time(new_task_start_minutes)
        reminder[_HOUR] = new_start_hour
        reminder[_MINUTE] = new_start_minute
        following_task = reminder
        compressed_reminders.append(reminder)
    
    compressed_reminders.reverse()
    compressed_reminders = sorted(compressed_reminders, key=lambda x: (x[_HOUR], x[_MINUTE]))
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

def announce_time(hour, minute, weekday, week_number):
    global audio_queue
    audio_queue = []
    log = ""

    did_bing_bong = (minute % 15 == 0)

    if did_bing_bong:
        audio_queue.append(_BING_BONG)
        # audio_queue.append((str(hour%12),"12")[hour==12 or hour==0 or hour==24])
        hour_string = (str(hour%12),"12")[hour==12 or hour==0 or hour==24]

        if minute == 0:
            audio_queue.append(hour_string + " o-clock")
        else:
            audio_queue.append( hour_string + ":" + pad(minute) )
    
    if minute == 0:
        audio_queue.append(_DAYS[weekday][_DAY_NAME].lower())

    for reminder in reminders:
        if not is_reminder_valid(weekday, week_number, reminder):
            continue

        if hour == reminder[_HOUR] and minute == reminder[_MINUTE]:
            if not did_bing_bong:
                did_bing_bong = True
                audio_queue.append(_BING_BONG)
            audio_queue.append(_TASK + "_" + reminder[_REMINDER])
        
        for i in range(0, _NUM_WARNINGS):
            warning_time_hours = reminder[_HOUR]
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

        if reminder[_HAS_FOLLOWUPS]:
            for i in range(0, _NUM_FOLLOWUPS):
                followup_time_hours = reminder[_HOUR]
                followup_time_minutes = reminder[_MINUTE] + (int(math.pow(2,i))*_FOLLOWUP_DELAY)
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
    now = datetime.datetime.now()
    valid_reminders = get_valid_reminders(now.weekday(), now.isocalendar().week)
    for reminder in valid_reminders:
        print(reminder_to_string(reminder))

if __name__ == "__main__":
    create_reminders()
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
            exit()
        except Exception as error:
            print_log("An error has occurred. Reinitializing.")
            print(error, type(error))
            play_text_to_speech("An error has occurred.")
            time.sleep(5)