import urllib

from steam_shaymus22 import data

def getPage( url ):
    page = ""
    while True:
        try:
            http = urllib.urlopen(url);
            line = ""
            while True:
                line = http.readline();
                if len(line) == 0:
                    break;
                page += line
        except Exception,e:
            continue;
        break;
    return page;
    
for appid in data:
    if data[appid].has_key("rating"):
        continue;

    page = getPage("http://store.steampowered.com/app/" + appid);
    index = page.find("game_area_metascore");
    if index != -1:
        page = page[index:];
        index = page.find("<span>");
        if index != -1:
            index += 6;
            page = page[index:];
            index = page.find("</span>");
            if index != -1:
                page = page[:index];
    page = page.strip();
    
    rating = 0;
    
    if len(page) > 1 and len(page) < 4:
        rating = int(page);
    data[appid]["rating"] = rating;
    print data[appid]["name"] + " " + str(rating);

f = open("steam_shaymus22.py","w");
f.write( "data=" + str(data) );
f.flush();
f.close();