import schedule
import datetime
import time
from playsound import playsound
from Talker import text_to_speech
from pattern.en import conjugate, PARTICIPLE, PAST, PRESENT, FUTURE
import nltk

global audio_queue
audio_queue = []

_DATA_SAVER = False

_WARNING_DELAY = 10
_NUM_WARNINGS = 1
_FOLLOWUP_DELAY = 10
_NUM_FOLLOWUPS = 1
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
_BING_BONG = "bing_bong.wav"

def play_text_to_speech(input):
    output = text_to_speech(input)
    if len(output) > 0:
        print_log("Created new file \"" + output + "\"")

def play_audio_files( soundfiles ):
    log_output = ""
    if len(soundfiles) > 0:
        print_log("Playing audio files: " + str(soundfiles))
    for file in soundfiles:
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
                    tokens = nltk.word_tokenize(phrase)
                    tagged = nltk.pos_tag(tokens)
                    verbs = [word for word, pos in tagged if pos.startswith("V")]
                    for identified_verb in verbs:
                        tensed_verb = conjugate(identified_verb, tense=PAST)
                        if not tensed_verb is None:
                            phrase = phrase.replace(identified_verb, tensed_verb)

                    phrase = "Have you " + phrase + " yet?"
                else: 
                    phrase = "It's time to " + phrase + "."
            play_text_to_speech(phrase)
            log_output += "[" + phrase + "] "
    return log_output


def _deprecated_play_audio_files( soundfiles ):
    log_output = ""
    if len(soundfiles) > 0:
        print_log("Playing audio files: " + str(soundfiles))
    
    for file in soundfiles:
        try:
            playsound( file )
            log_output += "[" + file + "] "
        except Exception as error:
            phrase = ""
            if file.find("_") == -1:
                phrase = file.split(".")[0]
            else:
                phrase = file.split(".")[0]
                segments = phrase.split("_")
                is_followup = (segments[0] == "followup")
                phrase = phrase[len(segments[0])+1:]
                phrase = phrase.replace("_"," ")
                if is_followup:
                    tokens = nltk.word_tokenize(phrase)
                    tagged = nltk.pos_tag(tokens)
                    verbs = [word for word, pos in tagged if pos.startswith("V")]
                    for identified_verb in verbs:
                        tensed_verb = conjugate(identified_verb, tense=PAST)
                        if not tensed_verb is None:
                            phrase = phrase.replace(identified_verb, tensed_verb)

                    phrase = "Have you " + phrase + " yet?"
                else:
                    phrase = "It's time to " + phrase + "."
            if not _DATA_SAVER:
                play_text_to_speech(phrase)
                log_output += "[" + phrase + "] "
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
    print(get_timestamp() + log_message)

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
        new_reminder( 9, 30, _AM, _DAYS, "take out Kiwi"),
        new_reminder(10, 35, _AM, _DAYS, "brush your teeth"),
        new_reminder(12, 30, _PM, _DAYS, "put away Kiwi"),
        new_reminder( 1, 20, _PM, _DAYS, "eat lunch"),
        new_reminder( 1, 45, _PM, _DAYS, "brush your teeth"),
        new_reminder( 2, 15, _PM, _DAYS, "take out Ridley"),
        new_reminder( 5, 50, _PM, _DAYS, "take out Kiwi"),
        new_reminder( 7,  0, _PM, _DAYS, "eat dinner"),
        new_reminder(10, 30, _PM, _DAYS, "take your melatonin"),

        new_reminder( 6,  0, _PM, _WEEKDAYS, "take a shower"),
        new_reminder(12, 30, _PM, _WEEKEND, "take a shower"),

        new_reminder(11, 30, _AM, _WEEKDAYS, "attend daily stand-up", _NO_FOLLOWUP),
        new_reminder( 2,  0, _PM, _WEEKDAYS, "attend developer huddle", _NO_FOLLOWUP),
        new_reminder( 4,  0, _PM, [_THURSDAY], "attend backlog refinement", _NO_FOLLOWUP)
    ]

def announce_time(hour, minute, weekday):
    global audio_queue
    audio_queue = []
    log = ""

    did_bing_bong = (minute % 15 == 0)

    if did_bing_bong:
        audio_queue.append(_BING_BONG)
        # audio_queue.append((str(hour%12),"12")[hour==12 or hour==0 or hour==24]) # + ".wav")
        hour_string = (str(hour%12),"12")[hour==12 or hour==0 or hour==24]

        if minute == 0:
            audio_queue.append(hour_string + " o-clock") #.wav")
        else:
            audio_queue.append( hour_string + ":" + pad(minute) ) #+ ".wav" )
    
    if minute == 0:
        audio_queue.append(_DAYS[weekday][_DAY_NAME].lower()) # + ".wav")

    for reminder in reminders:
        valid_day_of_week = False
        for day_object in reminder[_WHICH_DAYS]:
            if day_object[_DAY_ID] == weekday:
                valid_day_of_week = True
                break
            
        if not valid_day_of_week:
            continue

        if hour == reminder[_HOUR] and minute == reminder[_MINUTE]:
            if not did_bing_bong:
                did_bing_bong = True
                audio_queue.append(_BING_BONG)
            audio_queue.append(_TASK + "_" + reminder[_REMINDER])# + ".wav")
        
        for i in range(0, _NUM_WARNINGS):
            warning_time_hours = reminder[_HOUR]
            warning_time_minutes = reminder[_MINUTE] - ((i+1)*_WARNING_DELAY)
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
                
                warning_phrase = "It will be time to " + phrase + " at " + \
                                 (str(reminder[_HOUR]%12),"12")[reminder[_HOUR]==12 or reminder[_HOUR]==0 or reminder[_HOUR]==24] + ":"

                if reminder[_MINUTE] == 0:
                    warning_phrase += "o-clock"
                else:
                    warning_phrase += pad(reminder[_MINUTE])

                audio_queue.append(warning_phrase)

        if reminder[_HAS_FOLLOWUPS]:
            for i in range(0, _NUM_FOLLOWUPS):
                followup_time_hours = reminder[_HOUR]
                followup_time_minutes = reminder[_MINUTE] + ((i+1)*_FOLLOWUP_DELAY)
                while followup_time_minutes >= 60:
                    followup_time_minutes -= 60
                    followup_time_hours += 1
                    while followup_time_hours >= 24:
                        followup_time_hours -= 24
            
                if hour == followup_time_hours and minute == followup_time_minutes:
                    if not did_bing_bong:
                        did_bing_bong = True
                        audio_queue.append(_BING_BONG)
                    audio_queue.append(_FOLLOWUP + "_" + reminder[_REMINDER])# + ".wav")

    log += play_audio_files(audio_queue)
    if len(log) > 0:
        print_log(log)

def announce_current_time():
    now = datetime.datetime.now()
    announce_time(now.hour, now.minute, now.weekday)

if __name__ == "__main__":
    create_reminders()

    if not _DATA_SAVER:
        nltk.download("averaged_perceptron_tagger", quiet=True)
        nltk.download("punkt", quiet=True)
    try:
        conjugate("initialize", tense=FUTURE)
    except Exception:
        pass # will fail the first time, every time
    
    print_log("Running. " + play_audio_files([_BING_BONG]))
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
            play_audio_files(["An error has occurred."])
            time.sleep(5)