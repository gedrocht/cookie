import schedule
import datetime
import time
from playsound import playsound
import pyaudio
import wave
import sys

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

def play_audio_files( soundfiles ):
    global _CHUNK_SIZE

    log_output = ""

    if False:
        audio_handler = pyaudio.PyAudio()

        audio_stream = audio_handler.open(
                    format = audio_handler.get_format_from_width(2),
                    channels = 1,
                    rate = 48000,
                    output = True)

        data_bytes = bytes(0)

        for path in soundfiles:
            log_output += path + " "
            with wave.open(path, "rb") as wave_file:
                while len(audio_data := wave_file.readframes(_CHUNK_SIZE)):
                    data_bytes += audio_data
        
        audio_stream.write(data_bytes)

        audio_stream.close()
        audio_handler.terminate()
    else:
        for file in soundfiles:
            playsound( file )
            log_output += "[" + file + "] "
    return log_output

def pad( string ):
    string = str(string)
    if len(string) < 2:
        return "0" + string
    else:
        return string

def get_timestamp():
    now = datetime.datetime.now()
    return "[" + str(now.year) + "." + pad(str(now.month)) + "." + pad(str(now.day)) + "." + pad(str(now.hour)) + ":" + pad(str(now.minute)) + ":" + pad(str(now.second)) + "] "

def new_reminder(hour, minute, reminder, followup_only=False):
    global _HOUR
    global _MINUTE
    global _REMINDER
    global _FOLLOWUP_ONLY
    return {_HOUR: hour, _MINUTE:minute, _REMINDER:reminder}

def announce_time():
    global _HOUR
    global _MINUTE
    global _REMINDER
    global _TASK
    global _FOLLOWUP
    global _FOLLOWUP_DELAY
    global _NUM_FOLLOWUPS
    global _FOLLOWUP_ONLY
    
    now = datetime.datetime.now()
    log = ""

    schedule = [
                ###################################################
                ## 12:00 AM  ######################################
                ###################################################


                ###################################################
                ##  1:00 AM  ######################################
                ###################################################


                ###################################################
                ##  2:00 AM  ######################################
                ###################################################


                ###################################################
                ##  3:00 AM  ######################################
                ###################################################


                ###################################################
                ##  4:00 AM  ######################################
                ###################################################


                ###################################################
                ##  5:00 AM  ######################################
                ###################################################


                ###################################################
                ##  6:00 AM  ######################################
                ###################################################


                ###################################################
                ##  7:00 AM  ######################################
                ###################################################


                ###################################################
                ##  8:00 AM  ######################################
                ###################################################
                
                #   8:30 AM
                #new_reminder( 8, 30, "out_kiwi"),

                ###################################################
                ##  9:00 AM  ######################################
                ###################################################

                #   9:30 AM
                new_reminder( 9, 30, "out_kiwi"),

                ###################################################
                ## 10:00 AM  ######################################
                ###################################################
                
                #  10:15 AM
                #new_reminder(10, 15, "out_ridley"),

                #  10:15 AM
                new_reminder(10, 15, "brush_teeth"),

                ###################################################
                ## 11:00 AM  ######################################
                ###################################################


                ###################################################
                ## 12:00 PM  ######################################
                ###################################################

                # 12:45 PM
                new_reminder(12, 45, "lunch"),

                ###################################################
                ##  1:00 PM  ######################################
                ###################################################

                #   1:45 PM
                new_reminder(13, 45, "brush_teeth"),

                ###################################################
                ##  2:00 PM  ######################################
                ###################################################

                #   2:15 PM
                new_reminder(14, 15, "out_ridley"),

                ###################################################
                ##  3:00 PM  ######################################
                ###################################################
                
                #   3:00 PM
                #new_reminder(15,  0, "out_kiwi"),

                ###################################################
                ##  4:00 PM  ######################################
                ###################################################
                
                #   4:00 PM
                #new_reminder(16,  0, "out_ridley"),

                ###################################################
                ##  5:00 PM  ######################################
                ###################################################
                
                #   5:00 PM
                new_reminder(17,  0, "out_kiwi"),

                ###################################################
                ##  6:00 PM  ######################################
                ###################################################
                
                #   6:00 PM
                #new_reminder(18,  0, "out_ridley"),

                #   6:00 PM
                new_reminder(18,  0, "dinner"),

                ###################################################
                ##  7:00 PM  ######################################
                ###################################################
                
                #   7:00 PM
                new_reminder(19,  0, "shower"),

                #   7:40 PM
                #new_reminder(19, 40, "dinner"),

                ###################################################
                ##  8:00 PM  ######################################
                ###################################################

                #   8:40 PM
                #new_reminder(20, 40, "melatonin"),

                ###################################################
                ##  9:00 PM  ######################################
                ###################################################

                #   9:00 PM
                #new_reminder(21,  0, "brush_teeth"),

                ###################################################
                ## 10:00 PM  ######################################
                ###################################################
                
                #  10:30 PM
                new_reminder(22, 30, "melatonin"),

                ###################################################
                ## 11:00 PM  ######################################
                ###################################################
                
    ]
    
    '''
    if (now.hour == 24 or now.hour == 0) and now.minute == 0:
        return
    '''

    global audio_queue
    audio_queue = []

    should_bing_bong = (now.minute % 15 == 0)

    #if now.minute == 0:
    #    audio_queue.append( "bing_bong.wav" )
    #elif now.minute == 30 or now.minute == 15 or now.minute == 45:
    #    audio_queue.append( "bing_bong.wav" )
    if should_bing_bong:
        audio_queue.append( "bing_bong.wav" )
        audio_queue.append((str(now.hour%12),"12")[now.hour==12 or now.hour==0 or now.hour==24] + ".wav")

        if now.minute == 0:
            audio_queue.append("o-clock.wav")
        else:
            # if now.minute == 30:
            audio_queue.append( str(now.minute) + ".wav" )

        '''
        if now.hour < 12:
            audio_queue.append( "am.wav" )
        else:
            audio_queue.append( "pm.wav" )
        '''
    
    if now.minute == 0: # or now.minute == 30:
        if now.weekday() == 0:
            audio_queue.append( "monday.wav" )
        elif now.weekday() == 1:
            audio_queue.append( "tuesday.wav" )
        elif now.weekday() == 2:
            audio_queue.append( "wednesday.wav" )
        elif now.weekday() == 3:
            audio_queue.append( "thursday.wav" )
        elif now.weekday() == 4:
            audio_queue.append( "friday.wav" )
        elif now.weekday() == 5:
            audio_queue.append( "saturday.wav" )
        else:
            audio_queue.append( "sunday.wav" )
        
        '''
        if now.minute == 0 and True:
            if now.month == 1:
                audio_queue.append( "january.wav" )
            elif now.month == 2:
                audio_queue.append( "february.wav" )
            elif now.month == 3:
                audio_queue.append( "march.wav" )
            elif now.month == 4:
                audio_queue.append( "april.wav" )
            elif now.month == 5:
                audio_queue.append( "may.wav" )
            elif now.month == 6:
                audio_queue.append( "june.wav" )
            elif now.month == 7:
                audio_queue.append( "july.wav" )
            elif now.month == 8:
                audio_queue.append( "august.wav" )
            elif now.month == 9:
                audio_queue.append( "september.wav" )
            elif now.month == 10:
                audio_queue.append( "october.wav" )
            elif now.month == 11:
                audio_queue.append( "november.wav" )
            else:
                audio_queue.append( "december.wav" )
            
            if now.day < 21:
                audio_queue.append( "date_" + str(now.day) + ".wav" )
            elif now.day < 30:
                audio_queue.append( "date_20_part.wav" )
                audio_queue.append( "date_" + str(now.day-20) + ".wav" )
            elif now.day == 30:
                audio_queue.append( "date_30.wav" )
            else:
                audio_queue.append( "date_30_part.wav" )
                audio_queue.append( "date_1.wav" )
        '''

    for reminder in schedule:
        if now.hour == reminder[_HOUR] and now.minute == reminder[_MINUTE]:
            if not should_bing_bong:
                audio_queue.append( "bing_bong.wav" )
            audio_queue.append(_TASK + "_" + reminder[_REMINDER] + ".wav")
        
        for i in range(0, _NUM_FOLLOWUPS):
            followup_time_hours = reminder[_HOUR]
            followup_time_minutes = reminder[_MINUTE] + ((i+1)*_FOLLOWUP_DELAY)
            if followup_time_minutes >= 60:
                followup_time_minutes -= 60
                followup_time_hours += 1
                if followup_time_hours >= 24:
                    followup_time_hours -= 24
        
            if now.hour == followup_time_hours and now.minute == followup_time_minutes:
                if not should_bing_bong:
                    audio_queue.append( "bing_bong.wav" )
                audio_queue.append(_FOLLOWUP + "_" + reminder[_REMINDER] + ".wav")

    log += play_audio_files(audio_queue)

    if len(log) > 0:
        print(get_timestamp() + log)

print(get_timestamp() + "Running. " + play_audio_files(["bing_bong.wav", "bing_bong.wav"]))

announce_time()
schedule.every(1).minutes.do(announce_time)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        exit()
    except Exception as error:
        print( get_timestamp() + "An error has occurred. Reinitializing.")
        print(error)
        play_audio_files(["error.wav"])
        time.sleep(5)
        pass