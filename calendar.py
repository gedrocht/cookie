import time
import math

timeframes = [];
events = [];

DICT_HOURS  = "hours"
DICT_MIN    = "minutes"
DICT_SEC    = "seconds"

DICT_START  = "start"
DICT_END    = "end"
DICT_DUR    = "duration"

DICT_NAME   = "name"
DICT_RANGE  = "range"
DICT_LENGTH = "length"

def timeToSec( time ):
    return time[DICT_SEC] + (time[DICT_MIN] + time[DICT_HOURS]*60.0) * 60.0;
    
def secToTime( totalSeconds ):
    t = {};
    hours = totalSeconds/(60.0*60.0)
    min   = (hours-math.floor(hours))*60.0
    sec   = (min-math.floor(min))*60.0
    
    hours = math.floor(hours)
    min   = math.floor(min)
    sec   = math.floor(sec)
    
    if sec == 60 or sec == 59:
        sec = 0;
        min += 1;
    
    if min == 60:
        hours += 1;
        min = 0;
    
    t[DICT_HOURS] = hours;
    t[DICT_MIN]   = min;
    t[DICT_SEC]   = sec;
    return t

def newTime( hours=0, minutes=0, seconds=0 ):
    return { DICT_HOURS:hours, DICT_MIN:minutes, DICT_SEC:seconds };
    
def newTimeRange( time_start, time_end ):
    range = {};
    range[DICT_START] = time_start;
    range[DICT_END]   = time_end;
    range[DICT_DUR]   = getDuration( time_start, time_end );
    
    return range;
    
def getDuration( time_start, time_end ):
    start_sec = timeToSec(time_start);
    end_sec   = timeToSec(time_end);
    return secToTime(end_sec - start_sec);

def timeRangeToStr( time_range ):
    return timeToStr(time_range[DICT_START]) + " - " + timeToStr(time_range[DICT_END]) + " (duration: " + timeToStr(time_range[DICT_DUR]) + ")";
    
def strToTime( timeString ):
    arr = timeString.split(":");
    if len(arr) == 3:
        return newTime(int(arr[0]),int(arr[1]),int(arr[2]));
    elif len(arr) == 2:
        return newTime(int(arr[0]),int(arr[1]),0);
    elif len(arr) == 1:
        return newTime(int(arr[0]),0,0);
    return None

def timeToStr( timeObj ):
    hourValue = int(timeObj[DICT_HOURS]);
    pm = False
    
    while hourValue > 12:
        hourValue -= 12;
        pm = not pm;

    pmStr = " ";
    if pm:
        pmStr += "pm";
    else:
        pmStr += "am";
    
    hourString = str(int(hourValue)).zfill(2);
    minString = str(int(timeObj[DICT_MIN])).zfill(2);
    secString = str(int(timeObj[DICT_SEC])).zfill(2);
    if secString != "00":
        return hourString + ":" + minString + ":" + secString + pmStr;
    else:
        return hourString + ":" + minString + pmStr;
        
def newScheduledEvent( name, startString, endString ):
    start_time = strToTime(startString);
    end_time   = strToTime(endString);
    return newScheduledEvent_time(name, start_time, end_time);

def newScheduledEvent_time( name, start_time, end_time ):
    return {DICT_NAME:name, DICT_RANGE:newTimeRange(start_time, end_time)};
    
def addTimeframe( name, startString, endString ):
    timeframes.append( {DICT_NAME:name, DICT_RANGE:newTimeRange( strToTime(startString), strToTime(endString) )} );

def eventToStr( event, rjust = 0 ):
    return timeframeToStr(event,rjust);
    
def timeframeToStr( timeframe, rjust = 0 ):
    return (timeframe[DICT_NAME] + ": ").rjust(rjust) + timeToStr(timeframe[DICT_RANGE][DICT_START]) + " - " + timeToStr(timeframe[DICT_RANGE][DICT_END]);

def isTimeWithinTwoTimes( solo_time, start_time, end_time ):
    solo_secs  = timeToSec(solo_time);
    start_secs = timeToSec(start_time);
    end_secs   = timeToSec(end_time);
    
    return (solo_secs >= start_secs and solo_secs <= end_secs);
    
def isEventWithinTwoTimes( event, start_time, end_time ):
    return (isTimeWithinTwoTimes(event[DICT_RANGE][DICT_START], start_time, end_time) or \
            isTimeWithinTwoTimes(event[DICT_RANGE][DICT_END]  , start_time, end_time));
    
def isEventWithinTimeframe( event, timeframe ):
    return isEventWithinTwoTimes( event, timeframe[DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_END] );
    
def getEventsInTimeframe( timeframe ):
    events_in_timeframe = [];

    for event in events:
        if isEventWithinTimeframe( event, timeframe ):
            events_in_timeframe.append(event);
        
    return events_in_timeframe;
    
def areTimesEqual( time_a, time_b ):
    return timeToSec(time_a) == timeToSec(time_b);
    
def timeGreaterThan( time_a, time_b ):
    return timeToSec(time_a) > timeToSec(time_b);

def timeLessThan( time_a, time_b ):
    return timeToSec(time_a) < timeToSec(time_b);
    
def addTimes( time_a, time_b ):
    return secToTime( timeToSec(time_a) + timeToSec(time_b) );
    
def getGapsInTimeframe( timeframe ):
    gaps = [];
    events_in_timeframe = getEventsInTimeframe( timeframe );
    if len(events_in_timeframe) == 0:
        return [newTimeRange( timeframe[DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_END] )];
    
    if len(events_in_timeframe) == 1:
        if areTimesEqual(events_in_timeframe[0][DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_START] ) and \
           areTimesEqual(events_in_timeframe[0][DICT_RANGE][DICT_END],   timeframe[DICT_RANGE][DICT_END] ):
            return None;
    
    if not areTimesEqual(events_in_timeframe[0][DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_START]):
        gaps.append( newTimeRange( timeframe[DICT_RANGE][DICT_START], events_in_timeframe[0][DICT_RANGE][DICT_START] ) );
    
    for i in range(1,len(events_in_timeframe)):
        if not areTimesEqual( events_in_timeframe[i-1][DICT_RANGE][DICT_END], events_in_timeframe[i][DICT_RANGE][DICT_START] ):
            gaps.append( events_in_timeframe[i-1][DICT_RANGE][DICT_END], events_in_timeframe[i][DICT_RANGE][DICT_START] );
    
    if not areTimesEqual(events_in_timeframe[len(events_in_timeframe)-1][DICT_RANGE][DICT_END], timeframe[DICT_RANGE][DICT_END]):
        gaps.append( newTimeRange( events_in_timeframe[len(events_in_timeframe)-1][DICT_RANGE][DICT_END], timeframe[DICT_RANGE][DICT_END] ) );
    
    return gaps;
    
def getAllTimeframeGaps():
    gaps = [];
    for timeframe in timeframes:
        gaps.extend(getGapsInTimeframe(timeframe));
    return gaps;
    
def scheduleEvent( name, minutes ):
    gaps = getAllTimeframeGaps();
    event_time = secToTime(minutes*60.0);
    
    for gap in gaps:
        if timeGreaterThan( gap[DICT_DUR], event_time ) or areTimesEqual( gap[DICT_DUR], event_time ):
            events.append( newScheduledEvent_time( name, gap[DICT_START], addTimes(gap[DICT_START], event_time) ) );
            return True;
    return False;
    
def getEventTimeframe( event ):
    for timeframe in timeframes:
        if isEventWithinTimeframe(event,timeframe):
            return timeframe;
    return None;
    
def printAllEvents():
    longestStrLength = 0;
    for event in events:
        if len(event[DICT_NAME]) > longestStrLength:
            longestStrLength = len(event[DICT_NAME]);
    
    curTimeframe = "";
    timeframe = "";
    
    for event in events:
        timeframe = getEventTimeframe(event)
        if curTimeframe != timeframe:
            curTimeframe = timeframe;
            print "\n==========================================================================="
            print timeframeToStr(timeframe);
            print "==========================================================================="
        print eventToStr(event,longestStrLength+3);
    
    
eventsToSchedule = []

daysOfTheWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

#addTimeframe( "Morning",  "5:30",  "8:00" );
addTimeframe( "Monday Evening", "15:30", "21:00" );

for i in range(1,5):
    addTimeframe( daysOfTheWeek[i] + " Morning",  str(i*24+5)+":45",  str(i*24+8)+":00" );
    addTimeframe( daysOfTheWeek[i] + " Evening", str(i*24+15)+":30", str(i*24+21)+":00" );
    
eventsToSchedule.append(["Watch Alien",117]);
eventsToSchedule.append(["Watch Aliens",137]);
eventsToSchedule.append(["Watch Saw",103]);
eventsToSchedule.append(["Watch The Exorcist",122]);
eventsToSchedule.append(["Watch 28 Days Later",113]);
eventsToSchedule.append(["Watch A Nightmare on Elm Street",91]);
eventsToSchedule.append(["Watch The Ring",115]);
eventsToSchedule.append(["Watch Poltergeist",114]);
eventsToSchedule.append(["Watch The Blair Witch Project",81]);
eventsToSchedule.append(["Watch Event Horizon",96]);
eventsToSchedule.append(["Watch The Texas Chainsaw Massacre",98]);

for e in eventsToSchedule:
    scheduleEvent( e[0], e[1] )

printAllEvents();