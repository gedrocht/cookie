import schedule
import datetime
import time
from playsound import playsound
import pyaudio
import wave
import sys
from Talker import text_to_speech

global _WARNING_DELAY
_WARNING_DELAY = 5

global _NUM_WARNINGS
_NUM_WARNINGS = 1

global _FOLLOWUP_DELAY
_FOLLOWUP_DELAY = 10

global _NUM_FOLLOWUPS
_NUM_FOLLOWUPS = 1

global _CHUNK_SIZE
_CHUNK_SIZE = 1024

global _HOUR
_HOUR = "hour"

global _MINUTE
_MINUTE = "minute"

global _WARNING
_WARNING = "warning"

global _REMINDER
_REMINDER = "reminder"

global _TASK
_TASK = "task"

global _FOLLOWUP
_FOLLOWUP = "followup"

global audio_queue
audio_queue = []

global AM
AM = "AM"

global PM
PM = "PM"

global _SUNDAY
global _MONDAY
global _TUESDAY
global _WEDNESDAY
global _THURSDAY
global _FRIDAY
global _SATURDAY
global _DAY_ID
global _DAY_NAME
global _DAYS
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

global _BING_BONG
_BING_BONG = "bing_bong.wav"

def play_audio_files( soundfiles ):
    log_output = ""

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
                    phrase = "Have you " + phrase + " yet?"
                else:
                    phrase = "It's time to " + phrase + "."
            text_to_speech(phrase)
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
    return "[" + str(now.year) + "." + \
             pad(str(now.month)) + "." + \
             pad(str(now.day)) + "." + \
             pad(str(now.hour)) + ":" + \
             pad(str(now.minute)) + ":" + \
             pad(str(now.second)) + "] "

def new_reminder(hour, minute, am_pm, reminder, followup_only=False):
    offset = 0
    if am_pm == PM and hour < 12:
        offset = 12
    
    return {_HOUR: hour + offset, _MINUTE:minute, _REMINDER:reminder}

def create_reminders():
    global reminders
    reminders = [
        new_reminder( 9, 30, AM, "out_kiwi"),
        new_reminder(10, 15, AM, "brush_teeth"),
        new_reminder(12, 45, PM, "lunch"),
        new_reminder( 1, 45, PM, "brush_teeth"),
        new_reminder( 2, 15, PM, "out_ridley"),
        new_reminder( 5,  0, PM, "out_kiwi"),
        new_reminder( 6,  0, PM, "dinner"),
        new_reminder( 7,  0, PM, "shower"),
        new_reminder(10, 30, PM, "melatonin"),
    ]

def announce_time():
    global audio_queue
    audio_queue = []
    
    now = datetime.datetime.now()
    log = ""

    did_bing_bong = (now.minute % 15 == 0)

    if did_bing_bong:
        audio_queue.append(_BING_BONG)
        audio_queue.append((str(now.hour%12),"12")[now.hour==12 or now.hour==0 or now.hour==24] + ".wav")

        if now.minute == 0:
            audio_queue.append("o-clock.wav")
        else:
            audio_queue.append( str(now.minute) + ".wav" )
    
    if now.minute == 0:
        audio_queue.append(_DAYS[now.weekday()][_DAY_NAME].lower() + ".wav")

    for reminder in reminders:
        if now.hour == reminder[_HOUR] and now.minute == reminder[_MINUTE]:
            if not did_bing_bong:
                did_bing_bong = True
                audio_queue.append(_BING_BONG)
            audio_queue.append(_TASK + "_" + reminder[_REMINDER] + ".wav")
        
        for i in range(0, _NUM_WARNINGS):
            warning_time_hours = reminder[_HOUR]
            warning_time_minutes = reminder[_MINUTE] - ((i+1)*_WARNING_DELAY)
            while warning_time_minutes < 0:
                warning_time_minutes += 60
                warning_time_hours -= 1
                while warning_time_hours < 0:
                    warning_time_hours += 24
            
            if now.hour == warning_time_hours and now.minute == warning_time_minutes:
                if not did_bing_bong:
                    did_bing_bong = True
                    audio_queue.append(_BING_BONG)
                warning_phrase = "It will be time to " + reminder[_REMINDER].replace("_"," ") + " at " + \
                                 (str(now.hour%12),"12")[now.hour==12 or now.hour==0 or now.hour==24] + " "

                if now.minute == 0:
                    warning_phrase += "o-clock"
                else:
                    warning_phrase += str(now.minute)

                audio_queue.append(warning_phrase)
                

        for i in range(0, _NUM_FOLLOWUPS):
            followup_time_hours = reminder[_HOUR]
            followup_time_minutes = reminder[_MINUTE] + ((i+1)*_FOLLOWUP_DELAY)
            while followup_time_minutes >= 60:
                followup_time_minutes -= 60
                followup_time_hours += 1
                while followup_time_hours >= 24:
                    followup_time_hours -= 24
        
            if now.hour == followup_time_hours and now.minute == followup_time_minutes:
                if not did_bing_bong:
                    did_bing_bong = True
                    audio_queue.append(_BING_BONG)
                audio_queue.append(_FOLLOWUP + "_" + reminder[_REMINDER] + ".wav")

    log += play_audio_files(audio_queue)
    if len(log) > 0:
        print(get_timestamp() + log)

if __name__ == "__main__":
    create_reminders()
    
    print(get_timestamp() + "Running. " + play_audio_files([_BING_BONG]))
    text_to_speech("Initialization complete.")

    announce_time()
    schedule.every(1).minutes.do(announce_time)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            text_to_speech("Shutting down.")
            time.sleep(0.4)
            exit()
        except Exception as error:
            print( get_timestamp() + "An error has occurred. Reinitializing.")
            print(error)
            play_audio_files(["error.wav"])
            time.sleep(5)
            pass