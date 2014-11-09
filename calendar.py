import time
import math
import random

#############################
morningStart =  "6:15";
morningEnd   =  "6:45";
eveningStart = "16:00";
eveningEnd   = "18:30";
#############################
newMorningEndTime =  "8:00"
newEveningEndTime = "21:00"
#############################
morningGapLength  =  "0:25"
morningGapTime    =  "6:50"
eveningGapLength  =  "1:25"
eveningGapTime    = "16:15"
#############################
numDaysToGenerate = 200;
#############################

blackoutDates = ["Thursday 10/23/2014 Morning", \
                 "Friday 10/24/2014 Morning", \
                 "Saturday 10/25/2014 Morning", \
                 "Saturday 10/25/2014 Evening", \
                 "Sunday 10/26/2014 Morning", \
                 "Sunday 10/26/2014 Evening", \
                 "Monday 10/27/2014 Morning", \
                 "Friday 10/31/2014 Evening", \
                 "Saturday 11/01/2014 Evening", \
                 "Thursday 11/27/2014 Evening", \
                 "Monday 12/08/2014 Evening", \
                 "Thursday 12/25/2014 Evening", \
                 "Thursday 01/01/2015 Evening" ];

random.seed("BEANS!")

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

DICT_MONTH  = "month"
DICT_DAY    = "day"
DICT_YEAR   = "year"

LABEL_MORNING  = "Morning"
LABEL_EVENING  = "Evening"
LABEL_REMOVE   = "REMOVE"
LABEL_GAP      = "UNSCHEDULED"
LABEL_BLACKOUT = "PRE-SCHEDULED EVENTS"
LABEL_SEQUEL   = "SEQUEL"

ERR_INVALID_TIME  = "Invalid time specification"
ERR_INVALID_LABEL = "Invalid label specification"

daysOfTheWeek = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];

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
    if event[DICT_NAME] == LABEL_BLACKOUT:
        return LABEL_BLACKOUT.rjust(rjust)
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
    allTimeframeEvents = getEventsInTimeframe( timeframe );
    for event in allTimeframeEvents:
        if event[DICT_NAME] == LABEL_BLACKOUT:
            return [];

    gaps = [];
    events_in_timeframe = getEventsInTimeframe( timeframe );
    if len(events_in_timeframe) == 0:
        return [newTimeRange( timeframe[DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_END] )];
    
    if len(events_in_timeframe) == 1:
        if areTimesEqual(events_in_timeframe[0][DICT_RANGE][DICT_START], timeframe[DICT_RANGE][DICT_START] ) and \
           areTimesEqual(events_in_timeframe[0][DICT_RANGE][DICT_END],   timeframe[DICT_RANGE][DICT_END] ):
            return [];
    
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
    
def scheduleEvent( event ):
    name    = None;
    minutes = None;
    
    if event[0] == LABEL_SEQUEL:
        name    = event[2]
        minutes = event[3]
    else:
        name    = event[0]
        minutes = event[1];
    
    gaps = getAllTimeframeGaps();
    event_time = secToTime(minutes*60.0);
    
    for gap in gaps:
        if timeGreaterThan( gap[DICT_DUR], event_time ) or areTimesEqual( gap[DICT_DUR], event_time ):
            if event[0] == LABEL_SEQUEL:
                if not validateSequel(event, gap[DICT_START]):
                    continue;
            events.append( newScheduledEvent_time( name, gap[DICT_START], addTimes(gap[DICT_START], event_time) ) );
            return True;
    return False;
    
def scheduleEventInTimeframe( timeframe, name, minutes ):
    allTimeframeEvents = getEventsInTimeframe( timeframe );
    for event in allTimeframeEvents:
        if event[DICT_NAME] == LABEL_BLACKOUT:
            return False;

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
    event[DICT_RANGE][DICT_DUR]   = getDuration( event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_START] );
        
def areEventsEqual( event_a, event_b ):
    return ( areTimesEqual(event_a[DICT_RANGE][DICT_START], event_b[DICT_RANGE][DICT_START]) and \
             areTimesEqual(event_a[DICT_RANGE][DICT_END],   event_b[DICT_RANGE][DICT_END])   and \
             event_a[DICT_NAME] == event_b[DICT_NAME] );
        
def getEventRightAfterwards( event ):
    for otherEvent in events:
        if areEventsEqual( event, otherEvent ):
            continue;
        if areTimesEqual( event[DICT_RANGE][DICT_END], otherEvent[DICT_RANGE][DICT_START] ):
            return otherEvent;
    return None;
    
def getAllBackToBackEventsAfterwards( event ):
    result = [];
    
    curEvent = event;
    nextEvent = None;
    
    while True:
        nextEvent = getEventRightAfterwards(curEvent);
        if nextEvent is None:
            break;
        result.append(nextEvent);
        curEvent = nextEvent;
    
    return result;
    
def roundAllEventStartTimes( multiple = 10 ):
    for event in events:
        if event[DICT_NAME] == LABEL_BLACKOUT:
            continue;
        min = event[DICT_RANGE][DICT_START][DICT_MIN];
        remainder = multiple - min % multiple;
        
        if not remainder == 0 and min != 0:
            eventsAfterwards = getAllBackToBackEventsAfterwards( event );
            shiftEvent( event, remainder );
            
            for otherEvent in eventsAfterwards:
                shiftEvent( otherEvent, remainder );
                
def roundAllEventEndTimes( multiple = 10 ):
    for event in events:
        if event[DICT_NAME] == LABEL_BLACKOUT:
            continue;
        min = event[DICT_RANGE][DICT_END][DICT_MIN];
        remainder = multiple - min % multiple;
        if not remainder == 0 and min != 0:
            eventsAfterwards = getAllBackToBackEventsAfterwards( event );
            event[DICT_RANGE][DICT_END] = addTimes( event[DICT_RANGE][DICT_END], secToTime(remainder*60) );
            event[DICT_RANGE][DICT_DUR] = getDuration( event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END] );
            
            for otherEvent in eventsAfterwards:
                shiftEvent( otherEvent, remainder );
        
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
    
def printPreparedEvents( daysToSkip=0 ):
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
    
    daysSkipped = 0;
    skippedMorning = False;
    justSkippedDay = False;
    havePrintedFirstLine = False;
    
    for pair in orderedPrintableEvents:
        if havePrintedFirstLine:
            print "\n"
        
        day = pair[0].split(" ")[1];
        if day != curDay:
            curDay = day;
            daysSkipped += 1;
            if daysSkipped >= daysToSkip:
                if not havePrintedFirstLine:
                    print "";
                print "======================================================================"
                if havePrintedFirstLine:
                    print ""
                havePrintedFirstLine = True;
            justSkippedDay = True;
        else:
            justSkippedDay = False;
        
        if havePrintedFirstLine:
            if skippedMorning:
                printBox(removeIndex(pair[0]),longestBoxLength+5);
        
        for event in pair[1]:
            if havePrintedFirstLine:
                if skippedMorning:
                    print eventToStr(event,longestEventLength+3)
                else:
                    if event[DICT_RANGE][DICT_START][DICT_HOURS] % 24 > time.localtime().tm_hour:
                        print eventToStr(event,longestEventLength+3)
        
        if havePrintedFirstLine and justSkippedDay:
            skippedMorning = True;
           
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
    
def clipOverRounding( eventPool ):
    timeframe = None;
    for event in events:
        if event[DICT_NAME] == LABEL_BLACKOUT:
            continue;
        timeframe = getEventTimeframe(event);
        if timeframe is None:
            event[DICT_NAME] = LABEL_REMOVE;
            continue;
        if timeGreaterThan( event[DICT_RANGE][DICT_END], timeframe[DICT_RANGE][DICT_END] ):
            if event[DICT_NAME] == LABEL_GAP and timeframe[DICT_NAME].split(" ")[-1] == LABEL_MORNING:
                event[DICT_RANGE][DICT_END] = timeframe[DICT_RANGE][DICT_END];
                updateEventDuration(event);
                continue;
            for poolEvent in eventPool:
                if poolEvent[0] == event[DICT_NAME]:
                    if poolEvent[2]:
                        event[DICT_RANGE][DICT_END] = timeframe[DICT_RANGE][DICT_END]
                        event[DICT_RANGE][DICT_DUR] = getDuration( event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END] );
                        if areTimesEqual(event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END]) or timeToSec(event[DICT_RANGE][DICT_DUR]) <= 300:
                            event[DICT_NAME] = LABEL_REMOVE;
                    else:
                        event[DICT_NAME] = LABEL_REMOVE;
                        
                        newEvent = None;
                        while True:
                            newEvent = eventPool[int(math.floor(random.random()*len(eventPool)))]
                            if newEvent[2]:
                                break;
                        if newEvent is not None:
                            event[DICT_NAME] = newEvent[0]
                            event[DICT_RANGE][DICT_END] = timeframe[DICT_RANGE][DICT_END];
                            event[DICT_RANGE][DICT_DUR] = getDuration( event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END] );
                            if areTimesEqual(event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END]) or timeToSec(event[DICT_RANGE][DICT_DUR]) <= 300:
                                event[DICT_NAME] = LABEL_REMOVE;
    for event in events:
        if event[DICT_NAME] == LABEL_REMOVE:
            continue;
        if areTimesEqual(event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END]):
            event[DICT_NAME] = LABEL_REMOVE;

def updateEventDuration( event ):
    event[DICT_RANGE][DICT_DUR] = getDuration( event[DICT_RANGE][DICT_START], event[DICT_RANGE][DICT_END] );

def extendExtendableEvents( eventPool ):
    for timeframe in timeframes:
        latestEvent = getLastEventInTimeframe(timeframe);
        if latestEvent is None:
            continue;
        if areTimesEqual( latestEvent[DICT_RANGE][DICT_END], timeframe[DICT_RANGE][DICT_END] ):
            continue;
        
        for poolEvent in eventPool:
            if not poolEvent[2]:
                continue;
            if poolEvent[0] != latestEvent[DICT_NAME]:
                continue;
            latestEvent[DICT_RANGE][DICT_END] = timeframe[DICT_RANGE][DICT_END];
            updateEventDuration( latestEvent );
            
def updateRemovedEvents():
    newEvents = [];
    for event in events:
        if event[DICT_NAME] == LABEL_REMOVE:
            continue;
        newEvents.append(event);
    return newEvents;

def getAllEventsInTimeframe(timeframe):
    result = [];
    
    for event in events:
        if isEventWithinTimeframe(event,timeframe):
            result.append(event);
    
    return result;

def getLatestEvent( eventList ):
    latestEvent = None;
    latestEventSec = 0;
    
    sec = 0;
    for event in eventList:
        sec = timeToSec(event[DICT_RANGE][DICT_END]);
        if sec > latestEventSec:
            latestEventSec = sec;
            latestEvent = event;
    
    return latestEvent;
    
def getLastEventInTimeframe( timeframe ):
    return getLatestEvent( getAllEventsInTimeframe(timeframe) );

def getNumDaysToSkip():
    result    = 1;
    localtime = getLocaltimeDate();
    
    for day in scheduleableDays:
        date = strToDate(day.split(" ")[1]);
        
        if dateLessThan( date, localtime ):
           result += 1;
    
    return result;
    
def newDate( month, day, year ):
    if len(str(year)) == 2:
        year = int(str(time.localtime().tm_year)[0:2] + str(year))
    
    return {DICT_MONTH:month, DICT_DAY:day, DICT_YEAR:year};
    
def strToDate( dateStr ):
    dateSplit = dateStr.split("/");
    
    if len(dateSplit) == 2:
        return newDate( int(dateSplit[0]), int(dateSplit[1]), time.localtime().tm_year );
    else:
        return newDate( int(dateSplit[0]), int(dateSplit[1]), int(dateSplit[2]) );
    
def dateToStr( date, numValues=2 ):
    if numValues == 2:
        return str(date[DICT_MONTH]).zfill(2) + "/" + str(date[DICT_DAY]).zfill(2);
    elif numValues == 3:
        return str(date[DICT_MONTH]).zfill(2) + "/" + str(date[DICT_DAY]).zfill(2) + "/" + str(date[DICT_YEAR]);
    else:
       raise Exception("Invalid number of values specified");

def getNumDaysInMonth( monthValue ):
    if monthValue == 2:
        return 28;
    elif monthValue == 9 or \
         monthValue == 4 or \
         monthValue == 6 or \
         monthValue == 11:
        return 30;
    else:
        return 31
       
def validateDate( date ):
    while date[DICT_MONTH] > 12:
        date[DICT_MONTH] -= 12;
        date[DICT_YEAR]  += 1;
    
    while date[DICT_DAY] > getNumDaysInMonth(date[DICT_MONTH]):
        date[DICT_DAY]  -= getNumDaysInMonth(date[DICT_MONTH]);
        date[DICT_MONTH] += 1;
        
        while date[DICT_MONTH] > 12:
            date[DICT_MONTH] -= 12;
            date[DICT_YEAR]  += 1;
       
def addDaysToDate( date, days ):
    date[DICT_DAY] += days;
    validateDate(date);
    
def dateToTotalDays( date ):
    totalDays = 0;
    
    totalDays += date[DICT_YEAR]*365;
    
    for i in range(1,date[DICT_MONTH]):
        totalDays += getNumDaysInMonth(i);
    totalDays += date[DICT_DAY]
    
    return totalDays;
    
def dateLessThan( date_a, date_b ):
    return (dateToTotalDays(date_a) < dateToTotalDays(date_b));
    
def pyTimeToDate( pyTime ):
    return newDate( pyTime.tm_mon, pyTime.tm_mday, pyTime.tm_year );

def getLocaltimeDate():
    return pyTimeToDate( time.localtime() );
    
def numDaysBetweenDates( date_a, date_b ):
    return dateToTotalDays(date_a) - dateToTotalDays(date_b);
    
def generateDays( startingDay, numDaysToGenerate ):
    days = [];
    
    numDaysToGenerate += numDaysBetweenDates( getLocaltimeDate(), strToDate(startingDay.split(" ")[1]) );
    
    dateSplit = startingDay.split(" ");
    dayOfWeek = dateSplit[0];
    date = strToDate(dateSplit[1]);
    
    dayIndex = 0;
    for dayName in daysOfTheWeek:
        if dayName == dayOfWeek:
            break;
        dayIndex += 1;
    
    for i in range(0,numDaysToGenerate):
        days.append( daysOfTheWeek[dayIndex] + " " + dateToStr(date,3) );
        dayIndex += 1;
        if dayIndex > 6:
            dayIndex = 0;
        addDaysToDate( date, 1 );
    
    return days;
    
def removeBlackoutDates():
    for timeframe in timeframes:
        removedIndex = removeIndex(timeframe[DICT_NAME]).strip();
        for date in blackoutDates:
            if date == removedIndex:
                scheduleEventInTimeframe( timeframe, LABEL_BLACKOUT, timeToSec(timeframe[DICT_RANGE][DICT_DUR])/60.0 );
                break;
    
def hasEventBeenScheduledBefore( event, time ):
    for e in events:
        if e[DICT_NAME] == event:
            return timeLessThan(e[DICT_RANGE][DICT_START], time);
    return False;
    
def validateSequel( sequel, time ):
    for prev in sequel[1]:
        if not hasEventBeenScheduledBefore( prev, time ):
            return False;
    return True;
    
def consolodateGaps():
    for event in events:
        if event[DICT_NAME] != LABEL_GAP:
            continue;
        nextEvent = getEventRightAfterwards(event);
        if nextEvent is None:
            continue;
        if nextEvent[DICT_NAME] != LABEL_GAP:
            continue;
        consolodateEvents( event, nextEvent );
            
def consolodateEvents( event_a, event_b ):
    event_a[DICT_RANGE][DICT_END] = event_b[DICT_RANGE][DICT_END]
    updateEventDuration(event_a);
    event_b[DICT_NAME] = LABEL_REMOVE;
    
moviesToSchedule = []

scheduleableDays = generateDays("Tuesday 10/21",numDaysToGenerate);

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

startDayIndex = 0;
for i in range(startDayIndex,len(scheduleableDays)):
    offset = i*24;
    dayOfWeekStr = " " + scheduleableDays[i];
    
    if i != startDayIndex:
        addTimeframe( str(i*2-1) + dayOfWeekStr + " " + LABEL_MORNING, str(offset+morningHours_start)+morningMinutes_start_str, str(offset+morningHours_end)+morningMinutes_end_str );
    addTimeframe( str(i*2)   + dayOfWeekStr + " " + LABEL_EVENING, str(offset+eveningHours_start)+eveningMinutes_start_str, str(offset+eveningHours_end)+eveningMinutes_end_str );
    
removeBlackoutDates();
    
moviesToSchedule.append(["Watch Aliens",137]);
moviesToSchedule.append(["Watch Saw",103]);
moviesToSchedule.append(["Watch The Exorcist",122]);
moviesToSchedule.append(["Watch 28 Days Later",113]);
moviesToSchedule.append(["Watch The Blair Witch Project",81]);
moviesToSchedule.append(["Watch Event Horizon",96]);
moviesToSchedule.append(["Watch The Texas Chainsaw Massacre",98]);

#moviesToSchedule.append(["Watch 28 Weeks Later",100]);
moviesToSchedule.append(["Watch The Grudge",92]);
moviesToSchedule.append(["Watch Silent Hill",125]);
moviesToSchedule.append(["Watch The Hills Have Eyes",107]);
moviesToSchedule.append(["Watch Pandorum",108]);
moviesToSchedule.append(["Watch Final Destination",98]);
moviesToSchedule.append(["Watch The Purge: Anarchy",103]);
moviesToSchedule.append(["Watch Children of the Corn",92]);

moviesToSchedule.append(["Watch Fight Club",139,8.9]);
moviesToSchedule.append(["Watch It's a Wonderful Life",130,8.7]);
moviesToSchedule.append(["Watch Casablanca",102,8.6]);
moviesToSchedule.append(["Watch Life is Beautiful",116,8.6]);
moviesToSchedule.append(["Watch City Lights",87,8.6]);
moviesToSchedule.append(["Watch The Intouchables",112,8.6]);
moviesToSchedule.append(["Watch Modern Times",87,8.6]);
moviesToSchedule.append(["Watch Sunset Blvd.",110,8.6]);
moviesToSchedule.append(["Watch Psycho",109,8.6]);
moviesToSchedule.append(["Watch The Pianist",150,8.5]);
moviesToSchedule.append(["Watch The Lives of Others",137,8.5]);
moviesToSchedule.append(["Watch Paths of Glory",88,8.5]);
moviesToSchedule.append(["Watch Witness for the Prosecution",116,8.5]);
moviesToSchedule.append(["Watch The Shining",144,8.5]);
moviesToSchedule.append(["Watch Vertigo",128,8.4]);
moviesToSchedule.append(["Watch A Clockwork Orange",136,8.4]);
moviesToSchedule.append(["Watch Taxi Driver",113,8.4]);
moviesToSchedule.append(["Watch Double Indemnity",107,8.4]);
moviesToSchedule.append(["Watch Singin' in the Rain",103,8.4]);
moviesToSchedule.append(["Watch The Sting",129,8.4]);
moviesToSchedule.append(["Watch Bicycle Thieves",93,8.4]);
moviesToSchedule.append(["Watch All About Eve",138,8.4]);
moviesToSchedule.append(["Watch Rashomon",88,8.4]);
moviesToSchedule.append(["Watch The Treasure of the Sierra Madre",126,8.4]);
moviesToSchedule.append(["Watch The Apartment",125,8.4]);
moviesToSchedule.append(["Watch The Third Man",93,8.4]);
moviesToSchedule.append(["Watch Die Hard",131,8.3]);
moviesToSchedule.append(["Watch Snatch.",102,8.3]);
moviesToSchedule.append(["Watch L.A. Confidential",138,8.3]);
moviesToSchedule.append(["Watch Some Like It Hot",120,8.3]);
moviesToSchedule.append(["Watch Good Will Hunting",126,8.2]);
moviesToSchedule.append(["Watch Cowboys & Aliens",50,8.1]);
moviesToSchedule.append(["Watch Evangelion: 2.0",112,8.1]);
moviesToSchedule.append(["Watch Citizenfour",114,8.1]);
moviesToSchedule.append(["Watch Moon",97,8]);
moviesToSchedule.append(["Watch Jurassic Park",127,8]);
moviesToSchedule.append(["Watch Outpost 37",100,8]);
moviesToSchedule.append(["Watch Dawn of the Planet of the Apes",130,8]);
moviesToSchedule.append(["Watch Night of the Living Dead",96,8]);
moviesToSchedule.append(["Watch The Caine Mutiny",124,7.9]);
moviesToSchedule.append(["Watch Predator",107,7.9]);
moviesToSchedule.append(["Watch Hot Fuzz",121,7.9]);
moviesToSchedule.append(["Watch Dark City",100,7.8]);
moviesToSchedule.append(["Watch 3:10 to Yuma",122,7.8]);
moviesToSchedule.append(["Watch The Machinist",101,7.8]);
moviesToSchedule.append(["Watch Vampire Hunter D: Bloodlust",103,7.8]);
moviesToSchedule.append(["Watch The Birds",119,7.8]);
moviesToSchedule.append(["Watch Enemy at the Gates",131,7.6]);
moviesToSchedule.append(["Watch Army of Darkness",81,7.6]);
moviesToSchedule.append(["Watch American Psycho",102,7.6]);
moviesToSchedule.append(["Watch The Maze Runner",113,7.4]);
moviesToSchedule.append(["Watch The Secret Life of Walter Mitty",114,7.4]);
moviesToSchedule.append(["Watch Limitless",105,7.4]);
moviesToSchedule.append(["Watch The Animatrix",102,7.4]);
moviesToSchedule.append(["Watch Eraserhead",89,7.4]);
moviesToSchedule.append(["Watch Dawn of the Dead",101,7.4]);
moviesToSchedule.append(["Watch The Rock",136,7.4]);
moviesToSchedule.append(["Watch Cube",91,7.3]);
moviesToSchedule.append(["Watch Face/Off",138,7.3]);
moviesToSchedule.append(["Watch Videodrome",87,7.3]);
moviesToSchedule.append(["Watch GoldenEye",130,7.2]);
moviesToSchedule.append(["Watch Timecrimes",92,7.2]);
moviesToSchedule.append(["Watch The Andromeda Strain",131,7.2]);
moviesToSchedule.append(["Watch Escape from New York",99,7.2]);
moviesToSchedule.append(["Watch Bull Durham",108,7.1]);
moviesToSchedule.append(["Watch Coherence",89,7.1]);
moviesToSchedule.append(["Watch The Patriot",165,7.1]);
moviesToSchedule.append(["Watch Super Troopers",100,7.1]);
moviesToSchedule.append(["Watch Safety Not Guaranteed",86,7.1]);
moviesToSchedule.append(["Watch The Adjustment Bureau",106,7.1]);
moviesToSchedule.append(["Watch 9",79,7.1]);
moviesToSchedule.append(["Watch The Spy Who Loved Me",125,7.1]);
moviesToSchedule.append(["Watch Pitch Black",109,7.1]);
moviesToSchedule.append(["Watch Phone Booth",81,7.1]);
moviesToSchedule.append(["Watch Primer",77,7]);
moviesToSchedule.append(["Watch Oblivion",124,7]);
moviesToSchedule.append(["Watch World War Z",116,7]);
moviesToSchedule.append(["Watch The Thirteenth Floor",100,7]);
moviesToSchedule.append(["Watch Thunderball",130,7]);
moviesToSchedule.append(["Watch The Island",136,6.9]);
moviesToSchedule.append(["Watch Pandorum",108,6.8]);
moviesToSchedule.append(["Watch The Transporter",92,6.8]);
moviesToSchedule.append(["Watch The Thieves",135,6.8]);
moviesToSchedule.append(["Watch Top Gun",110,6.8]);
moviesToSchedule.append(["Watch Pandorum",108,6.8]);
moviesToSchedule.append(["Watch NGE: The End of Evangelion",107,6.8]);
moviesToSchedule.append(["Watch Who Am I?",108,6.8]);
moviesToSchedule.append(["Watch In Time",109,6.7]);
moviesToSchedule.append(["Watch Godzilla",123,6.7]);
moviesToSchedule.append(["Watch Silent Hill",125,6.6]);
moviesToSchedule.append(["Watch The Fast and the Furious",106,6.6]);
moviesToSchedule.append(["Watch John Carter",132,6.6]);
moviesToSchedule.append(["Watch The Crazies",101,6.6]);
moviesToSchedule.append(["Watch The Purge: Anarchy",103,6.5]);
moviesToSchedule.append(["Watch The Rover",103,6.5]);
moviesToSchedule.append(["Watch John Dies at the End",99,6.5]);
moviesToSchedule.append(["Watch Europa Report",90,6.5]);
moviesToSchedule.append(["Watch Bad Boys II",147,6.5]);
moviesToSchedule.append(["Watch The Hills Have Eyes",107,6.4]);
moviesToSchedule.append(["Watch Alien 3",114,6.4]);
moviesToSchedule.append(["Watch Gardens of Stone",111,6.4]);
moviesToSchedule.append(["Watch Predators",107,6.4]);
moviesToSchedule.append(["Watch The Signal",97,6.2]);
moviesToSchedule.append(["Watch Reign of Fire",101,6.2]);
moviesToSchedule.append(["A Million Ways to Die in the West",116,6.2]);
moviesToSchedule.append(["Watch Cargo",112,6.2]);
moviesToSchedule.append(["Watch Moonraker",126,6.2]);
moviesToSchedule.append(["Watch Untraceable",101,6.2]);
moviesToSchedule.append(["Watch V/H/S/2",96,6.1]);
moviesToSchedule.append(["Watch Push",111,6.1]);
moviesToSchedule.append(["Watch The Amityville Horror",90,6]);
moviesToSchedule.append(["Watch The Grudge",92,5.9]);
moviesToSchedule.append(["Watch M",120,5.9]);
moviesToSchedule.append(["Watch Universal Soldier",102,5.9]);
moviesToSchedule.append(["Watch V/H/S",116,5.8]);
moviesToSchedule.append(["Watch Species",108,5.8]);
moviesToSchedule.append(["Watch Timecop",99,5.8]);
moviesToSchedule.append(["Watch Hollow Man",112,5.7]);
moviesToSchedule.append(["Watch Children of the Corn",92,5.6]);
moviesToSchedule.append(["Watch Cube 2: Hypercube",94,5.6]);
moviesToSchedule.append(["Watch AVP: Alien vs Predator",101,5.5]);
moviesToSchedule.append(["Watch White Noise",101,5.5]);
moviesToSchedule.append(["Watch Collateral Damage",108,5.4]);
moviesToSchedule.append(["Watch The Core",135,5.4]);
moviesToSchedule.append(["Watch Maximum Overdrive",97,5.4]);
moviesToSchedule.append(["Watch The Ring Two",110,5.3]);
moviesToSchedule.append(["Watch Frankenstein's Army",84,5.3]);
moviesToSchedule.append(["Watch Frankenstein",92,5.2]);
moviesToSchedule.append(["Watch Clockstoppers",94,5.2]);
moviesToSchedule.append(["Watch Quicksand",95,5.2]);
moviesToSchedule.append(["Watch Stealth",121,5]);
moviesToSchedule.append(["Watch The Anomaly",97,4.9]);
moviesToSchedule.append(["Watch V/H/S: Viral",82,4.7]);
moviesToSchedule.append(["Watch Left Behind",110,3.3]);
moviesToSchedule.append(["The Descent: Part 2",94,0]);
moviesToSchedule.append(["Watch Mr. & Mrs. Smith",51,0]);


destSequels = ["Watch Final Destination", "Watch Final Destination 2", "Watch Final Destination 3","Watch Final Destination 4","Watch Final Destination 5"];
moviesToSchedule.append( [LABEL_SEQUEL, [destSequels[0]], destSequels[1], 90] );
moviesToSchedule.append( [LABEL_SEQUEL, destSequels[0:2], destSequels[2], 93] );
moviesToSchedule.append( [LABEL_SEQUEL, destSequels[0:3], destSequels[3], 82] );
moviesToSchedule.append( [LABEL_SEQUEL, destSequels[0:4], destSequels[4], 92] );

alienSequels = ["Watch Alien 3", "Watch Alien: Resurrection"];
moviesToSchedule.append( [alienSequels[0], 114] );
moviesToSchedule.append( [LABEL_SEQUEL, [alienSequels[0]], alienSequels[1], 109] );

moviesToSchedule.append(["Watch The Amityville Horror",90]);
moviesToSchedule.append(["Watch V/H/S",116]);

sawSequels = ["Watch Saw", "Watch Saw II", "Watch Saw III", "Watch Saw IV", "Watch Saw V", "Watch Saw VI", "Watch Saw VII"];
moviesToSchedule.append( [LABEL_SEQUEL, [sawSequels[0]], sawSequels[1], 93] );
moviesToSchedule.append( [LABEL_SEQUEL, sawSequels[0:2], sawSequels[2], 108] );
moviesToSchedule.append( [LABEL_SEQUEL, sawSequels[0:3], sawSequels[3], 93] );
moviesToSchedule.append( [LABEL_SEQUEL, sawSequels[0:4], sawSequels[4], 92] );
moviesToSchedule.append( [LABEL_SEQUEL, sawSequels[0:5], sawSequels[5], 90] );
moviesToSchedule.append( [LABEL_SEQUEL, sawSequels[0:6], sawSequels[6], 90] );

for e in moviesToSchedule:
    scheduleEvent( e );

randomEventsPool = [];
'''
randomEventsPool.append(["Play TF2",45,True]);
randomEventsPool.append(["Play Halo: ODST",30,True]);
randomEventsPool.append(["Play a new Steam game",15,True]);
randomEventsPool.append(["Play CS:GO",45,False]);
randomEventsPool.append(["Play Worms: Revolution",30,True]);
randomEventsPool.append(["Play Left 4 Dead 2",30,False])
randomEventsPool.append(["Play Battleblock Theater",30,True]);
randomEventsPool.append(["Play Hitman: Blood Money",30,True]);
randomEventsPool.append(["Play Elder Scrolls V: Skyrim",30,True]);
randomEventsPool.append(["Play God of War",25,True]);
randomEventsPool.append(["Play GTA: V",30,True]);
randomEventsPool.append(["Play Katamari Damacy",20,True]);
'''
#randomEventsPool.append(["Watch an anime",22,False])

randomEventsPool.append([LABEL_GAP,15,True]);

randomEventsPool.append(["Watch Breaking Bad",47,False]);
randomEventsPool.append(["Watch The Walking Dead",44,False]);
randomEventsPool.append(["Watch The Office",22,False]);
randomEventsPool.append(["Watch Tim and Eric Awesome Show, Great Job!",11,False]);
randomEventsPool.append(["Watch Mad Men",45,False]);
randomEventsPool.append(["Watch Parks and Recreation",22,False]);
randomEventsPool.append(["Watch It's Always Sunny in Philadelphia",22,False]);
randomEventsPool.append(["Watch 30 Rock",21,False]);
randomEventsPool.append(["Watch The Legend of Korra",23,False]);
randomEventsPool.append(["Watch Arrested Development",22,False]);
randomEventsPool.append(["Watch House of Cards",55,False]);
randomEventsPool.append(["Watch Boardwalk Empire",55,False]);
randomEventsPool.append(["Watch Stargate: SG-1",44,False]);
randomEventsPool.append(["Watch Babylon 5",45,False]);
randomEventsPool.append(["Watch South Park",22,False]);
randomEventsPool.append(["Watch Stargate: Atlantis",45,False]);
randomEventsPool.append(["Watch Star Trek",50,False]);
randomEventsPool.append(["Watch Star Trek: The Next Generation",44,False]);
randomEventsPool.append(["Watch Star Trek: Deep Space Nine",45,False]);
randomEventsPool.append(["Watch Qi",30,False]);
randomEventsPool.append(["Watch Top Gear",60,False]);

maxNumRandomEvents = 999+int(math.ceil(len(randomEventsPool)/3));

eveningGapHours = int(eveningGapTime.split(":")[0]) + int(eveningGapTime.split(":")[1])/60.0;
morningGapHours = int(morningGapTime.split(":")[0]) + int(morningGapTime.split(":")[1])/60.0;

eveningGapLengthMinutes = timeToSec(strToTime(eveningGapLength))/60.0;
morningGapLengthMinutes = timeToSec(strToTime(morningGapLength))/60.0;

setNewTimeframeTime( newMorningEndTime, DICT_END, LABEL_MORNING );
setNewTimeframeTime( newEveningEndTime, DICT_END, LABEL_EVENING );
removeBlackoutDates();

randomEvent     = None;
eveningGapAdded = False;
morningGapAdded = False;
for timeframe in timeframes:
    eveningGapAdded = False;
    morningGapAdded = False;
    usedIndexes = [];
    timesFailed = 0;
    while True:
        if not eveningGapAdded and timeframe[DICT_NAME].split(" ")[-1] == LABEL_EVENING:
            lastEvent  = getLastEventInTimeframe(timeframe);
            if lastEvent is not None:
                endHours   = lastEvent[DICT_RANGE][DICT_END][DICT_HOURS] % 24 + lastEvent[DICT_RANGE][DICT_END][DICT_MIN]/60.0;
                if endHours >= eveningGapHours:
                    scheduleEventInTimeframe( timeframe, LABEL_GAP, eveningGapLengthMinutes );
                    eveningGapAdded = True;
                    continue;
        if not morningGapAdded and timeframe[DICT_NAME].split(" ")[-1] == LABEL_MORNING:
            lastEvent = getLastEventInTimeframe(timeframe);
            if lastEvent is not None:
                endHours   = lastEvent[DICT_RANGE][DICT_END][DICT_HOURS] % 24 + lastEvent[DICT_RANGE][DICT_END][DICT_MIN]/60.0;
                if endHours >= morningGapHours:
                    scheduleEventInTimeframe( timeframe, LABEL_GAP, morningGapLengthMinutes );
                    morningGapAdded = True;
                    continue;
        
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

clipOverRounding(randomEventsPool);
consolodateGaps();
events = updateRemovedEvents();
extendExtendableEvents(randomEventsPool);

orderedPrintableEvents = prepareEventsForPrinting();
printPreparedEvents(getNumDaysToSkip());




