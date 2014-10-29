import urllib2

URLs = {"Watch an anime":None};

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
    
def getEventURL( name ):
    if URLs.has_key(name):
        return URLs[name];
    
    nameSplit = name.split(" ");
    firstWord = nameSplit[0].strip();
    
    if firstWord == "Watch":
        url = getWatchURL(sjoin(nameSplit[1:]));
    elif firstWord == "Play":
        url = getPlayURL(sjoin(nameSplit[1:]))
    else:
        url = None
    
    URLs[name] = url;
    
    return url;
    
def sjoin( arr ):
    result = "";
    for s in arr:
        result += s + " ";
    return result[:-1];
    
def getPage( URL ):
    response = urllib2.urlopen(URL)
    page = "";
    line = "";
    while True:
        line = response.readline();
        if len(line) == 0:
            break;
        page += line;
    return page;
    
def getWatchURL( name ):
    page = getPage("http://www.imdb.com/find?q=" + name.replace(" ","+"))
    search = '<a href="/title/'
    page = page[page.find(search)+9:]
    return "http://www.imdb.com" + page[0:page.find("?")-1];

def getPlayURL( name ):
    return None;

schedule = getSchedule();

js = "";

js = "schedule = ["
debug_js = "";
for day in schedule:
    debug_js = "";
    debug_js += '{date_morning:"' + day["date_morning"] + '",events_morning:[ ';

    for event in day["events_morning"]:
        name = event["name"]
        url = getEventURL(name);
        
        debug_js += '{name:"' + name + '",';
        debug_js += 'url:';
        if url is not None:
            debug_js += '"' + url + '"'
        else:
            debug_js += "undefined";
        debug_js += ','
        debug_js += 'start:"' + event["range"]["start"] + '",';
        debug_js += 'end:"' + event["range"]["end"] + '"},'
    debug_js = debug_js[:-1] + "],";
    
    debug_js += 'date_evening:"' + day["date_evening"] + '",'
    debug_js += "events_evening:[  ";
    for event in day["events_evening"]:
        name = event["name"]
        url = getEventURL(name);
        
        debug_js += '{name:"' + name + '",';
        debug_js += 'url:';
        if url is not None:
            debug_js += '"' + url + '"'
        else:
            debug_js += "undefined";
        debug_js += ','
        debug_js += 'start:"' + event["range"]["start"] + '",';
        debug_js += 'end:"' + event["range"]["end"] + '"},'    
    
    debug_js = debug_js[:-1] + "]},";
    js += debug_js;
    print debug_js;
js = js[:-1] + "];"
writer = open("calendar.js","w");
writer.write(js);
writer.flush();
writer.close();