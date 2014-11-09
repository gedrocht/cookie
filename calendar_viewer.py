import urllib2

URLs = {"Watch an anime":None};
Ratings = {};
Durations = {};

tv_shows = ["Watch Stargate: SG-1",\
            "Watch Stargate: Atlantis",\
            "Watch Star Trek",\
            "Watch Star Trek: The Next Generation",\
            "Watch Star Trek: Deep Space Nine",\
            "Watch Qi",\
            "Watch South Park",\
            "Watch Top Gear",
            "Watch Tim and Eric Awesome Show, Great Job!"];

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
    
def getStarRating( pageURL ):
    if pageURL is None or pageURL == "undefined":
        return 0;
    if Ratings.has_key(pageURL):
        return Ratings[pageURL];
    page = getPage(pageURL);
    search = '"titlePageSprite star-box-giga-star"'
    page = page[page.find(search)+38:]
    page = page[:3]
    if page[1] != '.':
        return 0;
    Ratings[pageURL] = float(page);
    return float(page);

def getDuration( pageURL ):
    if pageURL is None or pageURL == "undefined":
        return 0.0;
    if Durations.has_key(pageURL):
        return Durations[pageURL];
    page = getPage(pageURL);
    search = 'itemprop="duration"';
    
    page = page[page.find(search):]
    page = page[page.find('min')-5:]
    page = page[0:9].strip();
    page = page.split(" ")[0];
    
    if len(page) == 0:
        return 0.0;
    
    try:
        Durations[pageURL] = float(page);
    except Exception,e:
        return 0.0;
    return float(page);
    
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
        url  = getEventURL(name);
        rating   = getStarRating(url);
        duration = getDuration(url);
        
        if tv_shows.__contains__(name):
            url = "episode_viewer.html?" + sjoin(name.split(" ")[1:]).replace(" ","%20").replace(":","").replace(",","").replace("!","");
        
        debug_js += '{name:"' + name + '",';
        debug_js += 'url:';
        if url is not None:
            debug_js += '"' + url + '"'
        else:
            debug_js += "undefined";
        debug_js += ','
        debug_js += 'rating:' + str(rating) + ',';
        debug_js += 'duration:' + str(duration) + ',';
        debug_js += 'start:"' + event["range"]["start"] + '",';
        debug_js += 'end:"' + event["range"]["end"] + '"},'
    debug_js = debug_js[:-1] + "],";
    
    debug_js += 'date_evening:"' + day["date_evening"] + '",'
    debug_js += "events_evening:[  ";
    for event in day["events_evening"]:
        name = event["name"]
        url  = getEventURL(name);
        rating   = getStarRating(url);
        duration = getDuration(url);
        
        if tv_shows.__contains__(name):
            url = "episode_viewer.html?" + sjoin(name.split(" ")[1:]).replace(" ","%20").replace(":","");
        
        debug_js += '{name:"' + name + '",';
        debug_js += 'url:';
        if url is not None:
            debug_js += '"' + url + '"'
        else:
            debug_js += "undefined";
        debug_js += ','
        debug_js += 'rating:' + str(rating) + ',';
        debug_js += 'duration:' + str(duration) + ',';
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
