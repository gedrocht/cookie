import time
import math
import random
random.seed("BEANS!!")

timeframes = [];
events = [];
orderedPrintableEvents = [];

DICT_HOURS  = "hours"
DICT_MIN    = "minutes"
DICT_SEC    = "seconds"

DICT_START  = "start"
DICT_END    = "end"
DICT_DUR    = "duration"

DICT_NAME   = "name"
DICT_RANGE  = "range"
DICT_LENGTH = "length"

LABEL_MORNING = "Morning"
LABEL_EVENING = "Evening"

ERR_INVALID_TIME  = "Invalid time specification"
ERR_INVALID_LABEL = "Invalid label specification"

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
    
    hourString = str(int(hourValue)).rjust(2);
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
    
def subtractTimes( time_a, time_b ):
    return secToTime( timeToSec(time_a) - timeToSec(time_b) );
    
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
            gaps.append( newTimeRange( events_in_timeframe[i-1][DICT_RANGE][DICT_END], events_in_timeframe[i][DICT_RANGE][DICT_START] ) );
    
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
    
def scheduleEventInTimeframe( timeframe, name, minutes ):
    gaps = getGapsInTimeframe(timeframe);
    event_time = secToTime(minutes*60.0);
    
    if gaps == None:
        return False;
    
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

def shiftEvent( event, minutes ):
    event[DICT_RANGE][DICT_START] = addTimes( event[DICT_RANGE][DICT_START], secToTime(minutes*60.0) );
    event[DICT_RANGE][DICT_END]   = addTimes( event[DICT_RANGE][DICT_END]  , secToTime(minutes*60.0) );
        
def roundAllEventStartTimes( multiple = 10 ):
    for event in events:
        min = event[DICT_RANGE][DICT_START][DICT_MIN];
        remainder = multiple - min % multiple;
        if not remainder == 0 and min != 0:
            eventAtEnd = None;
            for otherEvent in events:
                if otherEvent[DICT_NAME] == event[DICT_NAME]:
                    continue;
                
                if areTimesEqual( event[DICT_RANGE][DICT_END], otherEvent[DICT_RANGE][DICT_START] ):
                    eventAtEnd = otherEvent;
                    break;
            shiftEvent( event, remainder );
            if eventAtEnd is not None:
                shiftEvent( eventAtEnd, remainder );
                
def roundAllEventEndTimes( multiple = 10 ):
    for event in events:
        min = event[DICT_RANGE][DICT_END][DICT_MIN];
        remainder = multiple - min % multiple;
        if not remainder == 0 and min != 0:
            eventAtEnd = None;
            for otherEvent in events:
                if otherEvent[DICT_NAME] == event[DICT_NAME]:
                    continue;
                
                if areTimesEqual( event[DICT_RANGE][DICT_END], otherEvent[DICT_RANGE][DICT_START] ):
                    eventAtEnd = otherEvent;
                    break;
            event[DICT_RANGE][DICT_END] = addTimes( event[DICT_RANGE][DICT_END], secToTime(remainder*60) );
            if eventAtEnd is not None:
                eventAtEnd[DICT_RANGE][DICT_START] = addTimes( event[DICT_RANGE][DICT_START], secToTime(remainder*60) );
        
def prepareEventsForPrinting():
    printableEvents = {};
    
    timeframe = None;
    
    for event in events:
        timeframe = getEventTimeframe(event);
        if not printableEvents.has_key(timeframe[DICT_NAME]):
            printableEvents[timeframe[DICT_NAME]] = [];
        printableEvents[timeframe[DICT_NAME]].append(event);
    
    orderedPrintableEvents = [];
    
    index = 0;
    while True:
        for timeframe in printableEvents:
            timeframe_index = int(timeframe.split(" ")[0])
            if timeframe_index == index:
                if len(orderedPrintableEvents) != 0 and orderedPrintableEvents[len(orderedPrintableEvents)-1][0] == timeframe:
                    orderedPrintableEvents[len(orderedPrintableEvents)-1][1].append(printableEvents[timeframe]);
                else:
                    orderedPrintableEvents.append([timeframe,printableEvents[timeframe]]);
        if len(orderedPrintableEvents) == len(printableEvents):
            break;
        index += 1;
    
    return orderedPrintableEvents;
        
def removeIndex( preparedEventTimeframe ):
    newStr = "";
    split = preparedEventTimeframe.split(" ");
    for i in range(1,len(split)):
        newStr += split[i] + " ";
    return newStr;

def printBox( text, rjust=0 ):
    topLeft  = "+";
    topRight = "+";
    botLeft  = "+";
    botRight = "+";
    vert     = "|";
    horiz    = "-";
    indent   = " ";
    Lpadding = " ";
    Rpadding = "";
    
    text = Lpadding + text + Rpadding;
    
    topStr = indent + topLeft;
    for i in range(0,len(text)):
        topStr += horiz;
    topStr += topRight
    
    midStr = indent + vert + text + vert
    
    botStr = indent + botLeft;
    for i in range(0,len(text)):
        botStr += horiz;
    botStr += botRight;
    
    print topStr.rjust(rjust);
    print midStr.rjust(rjust);
    print botStr.rjust(rjust);
    
    
def printPreparedEvents():
    longestEventLength = 0;
    longestBoxLength   = 0;
    
    for pair in orderedPrintableEvents:
        boxLen = len(removeIndex(pair[0]));
        if boxLen > longestBoxLength:
            longestBoxLength = boxLen;
        
        for event in pair[1]:
            if len(event[DICT_NAME]) > longestEventLength:
                longestEventLength = len(event[DICT_NAME])
    
    curDay = "";
    
    for pair in orderedPrintableEvents:
        print "\n"
        
        day = pair[0].split(" ")[1];
        if day != curDay:
            curDay = day;
            print "======================================================================\n"
        
        printBox(removeIndex(pair[0]),longestBoxLength+5);
        
        for event in pair[1]:
            print eventToStr(event,longestEventLength+3)
    print "\n\n======================================================================\n"

def setNewTimeframeTime( new_time, start_or_end, morning_or_evening ):
    newTime = strToTime(new_time);
    
    oldTime = None;
    
    if morning_or_evening == LABEL_MORNING:
        if start_or_end == DICT_START:
            oldTime = strToTime(morningStart);
        elif start_or_end == DICT_END:
            oldTime = strToTime(morningEnd);
        else:
            raise Exception(ERR_INVALID_TIME);
    elif morning_or_evening == LABEL_EVENING:
        if start_or_end == DICT_START:
            oldTime = strToTime(eveningStart);
        elif start_or_end == DICT_END:
            oldTime = strToTime(eveningEnd);
        else:
            raise Exception(ERR_INVALID_TIME);
    else:
        raise Exception(ERR_INVALID_LABEL);
        
    timeDifference = subtractTimes( newTime, oldTime );

    for timeframe in timeframes:
        if timeframe[DICT_NAME].split(" ")[-1] == morning_or_evening:
            timeframe[DICT_RANGE][start_or_end] = addTimes( timeframe[DICT_RANGE][start_or_end], timeDifference );
            timeframe[DICT_RANGE][DICT_DUR] = getDuration( timeframe[DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_END] );
    
moviesToSchedule = []

daysOfTheWeek = ["Wednesday 10/22", "Thursday 10/23", "Friday 10/24", "Saturday 10/25", "Sunday 10/26",\
                 "Monday 10/27", "Tuesday 10/28", "Wednesday 10/29", "Thursday 10/30" ];


##########################################
morningStart =  "6:00";
morningEnd   =  "7:45";
eveningStart = "16:00";
eveningEnd   = "19:15";
##########################################

morningMinutes_start_str = morningStart.split(":")[1];
morningMinutes_end_str   = morningEnd.split(":")[1];
eveningMinutes_start_str = eveningStart.split(":")[1];
eveningMinutes_end_str   = eveningEnd.split(":")[1];

morningMinutes_start = int(morningMinutes_start_str);
morningMinutes_end   = int(morningMinutes_end_str);
eveningMinutes_start = int(eveningMinutes_start_str);
eveningMinutes_end   = int(eveningMinutes_end_str);

morningMinutes_start_str = ":" + morningMinutes_start_str;
morningMinutes_end_str   = ":" + morningMinutes_end_str;
eveningMinutes_start_str = ":" + eveningMinutes_start_str;
eveningMinutes_end_str   = ":" + eveningMinutes_end_str;

morningHours_start_str = morningStart.split(":")[0];
morningHours_end_str   = morningEnd.split(":")[0];
eveningHours_start_str = eveningStart.split(":")[0];
eveningHours_end_str   = eveningEnd.split(":")[0];

morningHours_start = int(morningHours_start_str);
morningHours_end   = int(morningHours_end_str);
eveningHours_start = int(eveningHours_start_str);
eveningHours_end   = int(eveningHours_end_str);

addTimeframe( str(0) + " " + "Tuesday 10/21 Evening", eveningHours_start_str + eveningMinutes_start_str, eveningHours_end_str + eveningMinutes_end_str );

for i in range(1,len(daysOfTheWeek)):
    offset = i*24;
    dayOfWeekStr = " " + daysOfTheWeek[i];
    
    addTimeframe( str(i*2-1) + dayOfWeekStr + " " + LABEL_MORNING, str(offset+morningHours_start)+morningMinutes_start_str, str(offset+morningHours_end)+morningMinutes_end_str );
    addTimeframe( str(i*2)   + dayOfWeekStr + " " + LABEL_EVENING, str(offset+eveningHours_start)+eveningMinutes_start_str, str(offset+eveningHours_end)+eveningMinutes_end_str );
    
moviesToSchedule.append(["Watch Aliens",137]);
moviesToSchedule.append(["Watch Saw",103]);
moviesToSchedule.append(["Watch The Exorcist",122]);
moviesToSchedule.append(["Watch 28 Days Later",113]);
moviesToSchedule.append(["Watch A Nightmare on Elm Street",91]);
moviesToSchedule.append(["Watch The Ring",115]);
moviesToSchedule.append(["Watch Poltergeist",114]);
moviesToSchedule.append(["Watch The Blair Witch Project",81]);
moviesToSchedule.append(["The Descent",99]);
moviesToSchedule.append(["Watch Event Horizon",96]);
moviesToSchedule.append(["Watch The Texas Chainsaw Massacre",98]);

moviesToSchedule.append(["Watch Saw II",93]);
moviesToSchedule.append(["Watch 28 Weeks Later",100]);
moviesToSchedule.append(["Watch The Grudge",92]);
moviesToSchedule.append(["Watch Silent Hill",125]);
moviesToSchedule.append(["Watch Jeepers Creepers",90]);
moviesToSchedule.append(["Watch [Rec]",78]);
moviesToSchedule.append(["Watch The Hills Have Eyes",107]);
moviesToSchedule.append(["Watch Pandorum",108]);
moviesToSchedule.append(["Watch Final Destination",98]);
moviesToSchedule.append(["Watch The Purge: Anarchy",103]);
moviesToSchedule.append(["Watch Children of the Corn",92]);
moviesToSchedule.append(["Watch The Amityville Horror",90]);
moviesToSchedule.append(["Watch V/H/S",116]);


for e in moviesToSchedule:
    scheduleEvent( e[0], e[1] )

randomEventsPool = []
randomEventsPool.append(["Play TF2",45]);
randomEventsPool.append(["Play Halo: ODST",30]);
randomEventsPool.append(["Play CS:GO",45]);
randomEventsPool.append(["Play Worms: Revolution",45]);
randomEventsPool.append(["Play Left 4 Dead 2",30])
randomEventsPool.append(["Play Battleblock Theater",30]);
randomEventsPool.append(["Play a new Steam game",20]);
randomEventsPool.append(["Watch an anime",22])
randomEventsPool.append(["Watch Breaking Bad",47]);
randomEventsPool.append(["Watch The Walking Dead",44]);
randomEventsPool.append(["Watch The Office",22]);
randomEventsPool.append(["Watch Tim and Eric",11]);
randomEventsPool.append(["Watch Mad Men",45]);
randomEventsPool.append(["Watch Parks and Recreation",22]);
randomEventsPool.append(["Watch It's Always Sunny in Philadelphia",22]);
randomEventsPool.append(["Watch 30 Rock",21]);
randomEventsPool.append(["Watch The Legend of Korra",23]);

#############################
newMorningEndTime =  "8:00"
newEveningEndTime = "20:40"
#############################

setNewTimeframeTime( newMorningEndTime, DICT_END, LABEL_MORNING );
setNewTimeframeTime( newEveningEndTime, DICT_END, LABEL_EVENING );



maxNumRandomEvents = 999+int(math.ceil(len(randomEventsPool)/3));

randomEvent = None;
for timeframe in timeframes:
    usedIndexes = [];
    timesFailed = 0;
    while True:
        if len(usedIndexes) >= len(randomEventsPool) or len(usedIndexes) >= maxNumRandomEvents:
            break;
        randomIndex = -1;
        while True:
            randomIndex = int(math.floor(random.random()*len(randomEventsPool)));
            if not usedIndexes.__contains__(randomIndex):
                usedIndexes.append(randomIndex);
                break;
        randomEvent = randomEventsPool[randomIndex];
        if not scheduleEventInTimeframe( timeframe, randomEvent[0], randomEvent[1] ):
            continue;

roundAllEventStartTimes(10);
roundAllEventEndTimes(5);
orderedPrintableEvents = prepareEventsForPrinting();
printPreparedEvents();












