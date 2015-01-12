import sys
import math

def getFileName():
    if len(sys.argv) != 2:
        print "Please input a filename";
        sys.exit(1);
    else:
        return sys.argv[1];

def getLines( filename ):
    f = open(filename);
    
    lines = [];
    line = "";
    line_info = None;
    while True:
        line = f.readline();
        if len(line) == 0:
            break;
        line_info = analyzeLine(line);
        if line_info is not None:
            lines.append(line_info);
    
    f.close();
    return lines;
    
def analyzeLine( line ):
    #[9:07:56 AM] Snacrifice: FART
    timeIndex  = line.find("]")
    if timeIndex == -1:
        return None;
    
    colonIndex = line[timeIndex+1:].find(":")+timeIndex+1;
    
    time = line[1:timeIndex];
    name = line[timeIndex+2:colonIndex];
    message = line[colonIndex+2:-1];
    
    seconds = getSeconds(time);
    
    return [seconds, name, message];
    
def getSeconds( time ):
    space_split = time.split(" ");
    am_pm = space_split[1];
    
    colon_split = space_split[0].split(":");
    hours   = int(colon_split[0]);
    minutes = int(colon_split[1]);
    seconds = int(colon_split[2]);
    
    if am_pm == "PM":
        hours += 12;
    
    return seconds + (minutes + (hours * 60))*60;
    
def analyzeLines( lines ):
    otherName = "";
    otherTime = 0;
    
    waitingTime = {};
    messageCounts = {};
    
    otherName = lines[0][1];
    otherTime = lines[0][0];
    
    for line in lines[1:]:
        if line[1] == otherName:
            continue;
        gap = line[0]-otherTime;
        
        if waitingTime.has_key(otherName):
            wait = waitingTime[otherName];
            wait[1] = wait[1] + 1;
            wait[0] = wait[0] + gap;
        else:
            waitingTime[otherName] = [gap,1];
        otherName = line[1];
        otherTime = line[0];
        
    for line in lines:
        if messageCounts.has_key(line[1]):
            messageCounts[line[1]] = messageCounts[line[1]] + 1;
        else:
            messageCounts[line[1]] = 1;
        
    print "Average Waiting Time: ";
    wait = None;
    
    longestNameLength = 0;
    
    for key in waitingTime:
        if len(key) > longestNameLength:
            longestNameLength = len(key);
    longestNameLength += 2;
    
    for key in waitingTime:
        wait = waitingTime[key];
        print (key + ": ").ljust(longestNameLength) + str(wait[0]/wait[1]).rjust(3) + " seconds";
    
    totalMessages = 0.0;
    for key in messageCounts:
        totalMessages += messageCounts[key];
    
    print "\nMessages Sent Ratios: ";
    for key in messageCounts:
        print (key + ": ").ljust(longestNameLength) + str(round(messageCounts[key]/totalMessages,2)*100)[:-2].ljust(2) + "%";
    
lines = analyzeLines(getLines(getFileName()));