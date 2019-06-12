import schedule
import datetime
import time
from playsound import playsound

def play_sound( soundfile ):
    playsound( soundfile )
    return soundfile + " "

def pad( string ):
    if len(string) < 2:
        return "0" + string
    else:
        return string

def get_timestamp():
    now = datetime.datetime.now()
    return "[" + str(now.year) + "." + pad(str(now.month)) + "." + pad(str(now.day)) + "." + pad(str(now.hour)) + ":" + pad(str(now.minute)) + ":" + pad(str(now.second)) + "] "
        
def announce_time():
    now = datetime.datetime.now()
    
    log = get_timestamp()
    
    if (now.hour == 24 or now.hour == 0) and now.minute == 0:
        return
    
    if now.minute == 0:
        log += play_sound( "bell.mp3" )
    elif now.minute == 30 or now.minute == 15 or now.minute == 45:
        log += play_sound( "chime.mp3" )
    
    log += play_sound((str(now.hour%12),"12")[now.hour==12 or now.hour==0 or now.hour==24] + ".mp3")
    
    if not now.minute == 0:
        log += play_sound( str(now.minute) + ".mp3" )
        
    if now.hour < 12:
        log += play_sound( "am.mp3" )
    else:
        log += play_sound( "pm.mp3" )
    
    if now.minute == 0 or now.minute == 30:
        if now.weekday() == 0:
            log += play_sound( "monday.mp3" )
        elif now.weekday() == 1:
            log += play_sound( "tuesday.mp3" )
        elif now.weekday() == 2:
            log += play_sound( "wednesday.mp3" )
        elif now.weekday() == 3:
            log += play_sound( "thursday.mp3" )
        elif now.weekday() == 4:
            log += play_sound( "friday.mp3" )
        elif now.weekday() == 5:
            log += play_sound( "saturday.mp3" )
        else:
            log += play_sound( "sunday.mp3" )
        
        if now.month == 1:
            log += play_sound( "january.mp3" )
        elif now.month == 2:
            log += play_sound( "february.mp3" )
        elif now.month == 3:
            log += play_sound( "march.mp3" )
        elif now.month == 4:
            log += play_sound( "april.mp3" )
        elif now.month == 5:
            log += play_sound( "may.mp3" )
        elif now.month == 6:
            log += play_sound( "june.mp3" )
        elif now.month == 7:
            log += play_sound( "july.mp3" )
        elif now.month == 8:
            log += play_sound( "august.mp3" )
        elif now.month == 9:
            log += play_sound( "september.mp3" )
        elif now.month == 10:
            log += play_sound( "october.mp3" )
        elif now.month == 11:
            log += play_sound( "november.mp3" )
        else:
            log += play_sound( "december.mp3" )
        
        if now.day < 21:
            log += play_sound( "date_" + str(now.day) + ".mp3" )
        elif now.day < 30:
            log += play_sound( "date_20_part.mp3" )
            log += play_sound( "date_" + str(now.day-20) + ".mp3" )
        elif now.day == 30:
            log += play_sound( "date_30.mp3" )
        else:
            log += play_sound( "date_30_part.mp3" )
            log += play_sound( "date_1.mp3" )
    print log
    

schedule.every().hour.at(":00").do(announce_time)
schedule.every().hour.at(":15").do(announce_time)
schedule.every().hour.at(":30").do(announce_time)
schedule.every().hour.at(":45").do(announce_time)

print get_timestamp() + "Running."

while True:
    try:
        schedule.run_pending()
        time.sleep(10);
    except:
        print get_timestamp() + "An error has occurred. Reinitializing."
        pass