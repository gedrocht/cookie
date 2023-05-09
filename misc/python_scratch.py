def getSchedule( filename="FULL_SCHEDULE.txt" ):
    result = "";
    
    f = open(filename,"r");
    line = "";
    while True:
        line = f.readline()
        if len(line) == 0:
            break;
        result += line;
    
    days = result.split("======================================================================")[1:-1];
    
    newDays = [];
    for day in days:
        newDay = [];
        dayLines = day.split("\n");
        for line in dayLines:
            if len(line.strip()) == 0:
                continue;
            newDay.append(line.strip());
        newDays.append(newDay);
    
    schedule = [];
    for day in newDays:
        scheduleDay = {"events_morning":[],"events_evening":[],"date_morning":""};
        for line in day:
            firstColon = line.find(":  ");
            if firstColon == -1:
                if line[0] == "|":
                    if line.find("Morning") != -1:
                        scheduleDay["date_morning"] = line[1:-1].strip();
                    else:
                        scheduleDay["date_evening"] = line[1:-1].strip();
                continue
            name = (line[0:firstColon]).strip();
            range = (line[firstColon+1:]).strip();
            
            rangeSplit = range.split("-");
            startTime = rangeSplit[0].strip();
            endTime   = rangeSplit[1].strip();
            
            range = {"start":startTime,"end":endTime};
            
            if scheduleDay.has_key("date_evening"):
                scheduleDay["events_evening"].append({"name":name,"range":range});
            else:
                scheduleDay["events_morning"].append({"name":name,"range":range});
        schedule.append(scheduleDay);
    
    return schedule;