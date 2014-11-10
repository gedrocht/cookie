import urllib;
import sys;

def getID():
    if len(sys.argv) != 2:
        print "Please input a Steam ID";
        sys.exit(1);
    else:
        return sys.argv[1];
        
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

def getURL_games( id ):
    return "http://steamcommunity.com/id/" + id + "/games/?tab=all&sort=playtime";

def getURL_playerAchievements( id, game ):
    return "http://steamcommunity.com/id/" + id + "/stats/" + str(game) + "/?tab=achievements";
    
def getURL_gameAchievements( game ):
    return "http://steamcommunity.com/stats/" + str(game) + "/achievements/";

def convertToSymbol( s ):
    if s.__contains__("\\"):
        text = s
        index = text.find("\\")
        segment = text[index:index+6]
        exec("x = u'" + segment + "'")
        text = text.replace(segment,x.encode('ascii', 'xmlcharrefreplace'))
        #print s
        #print text
        #print ""
        return text
    return s
    
def getGames( id ):
    print "Loading " + id + "'s games:";
    page = getPage( getURL_games(id) );
    indexA = page.find("rgGames");
    if indexA == -1:
        return None;
    indexB = page.find("}];");
    page = page[indexA:indexB+2];
    true = True
    false = False
    exec(page);
    print str(len(rgGames)) + " games loaded.";
    
    games = {}
    
    name = ""
    index = -1
    segment = ""
    x = None
    
    for game in rgGames:
        game["name"] = convertToSymbol(game["name"])
        games[str(game["appid"])] = game
    
    return games
    
def getPlayerAchievements( id, games ):
    newIndex = 0;
    indexA = 0;
    indexB = 0;
    image = "";
    name = "";
    description = "";
    page = "";
    gameIndex = 0;
    achievements = None;
    numAchievementsUnlocked = 0;
    unlocked = False;
    
    debug_count = 0;
    games_length = str(len(games));
    print "Loading all unlocked achievements for all of " + id + "'s games:";
    
    game = None
    for gameID in games:
        game = games[gameID]
        debug_count += 1;
        
        if data is not None and data.has_key(gameID):
            if not game.has_key("hours_forever") or not game.has_key("last_played"):
                games[gameID] = data[gameID]
                continue;
            
            if data.has_key(gameID):
                if game["last_played"] == data[gameID]["last_played"]:
                    games[gameID] = data[gameID]
                    continue;
    
        if str(game["friendlyURL"]) == "False":
            game["achievements"] = [];
            continue;
            
        page = getPage( getURL_playerAchievements(id,game["friendlyURL"]) );
        
        if page.find("No stats are available at this time.") != -1:
            game["achievements"] = [];
            continue;
        
        print str(debug_count).rjust(4) + " of " + games_length + " - " + game["name"];
        
        numAchievementsUnlocked = page.count("achieveUnlockTime");
        
        newIndex = page.find(".jpg")+4;
        page = page[newIndex:];
        newIndex = page.find(".jpg")+4;
        page = page[newIndex:];
        
        achievements = []
        game["achievements"] = achievements;
        
        while True:
            indexA = page.find("http://cdn.akamai.steamstatic.com/steamcommunity/public/images/");
            if indexA == -1: break;
            indexB = page.find(".jpg")+4;
            image = page[indexA:indexB];
            
            page = page[indexB:]
        
            indexA = page.find("<h3>");
            if indexA == -1: break;
            indexA += 4;
            indexB = page[indexA:].find("</h3>");
            newIndex = indexA+indexB;
            name = page[indexA:newIndex];
            
            page = page[newIndex:]
            
            indexA = page.find("<h5>");
            if indexA == -1: break;
            indexA += 4;
            indexB = page[indexA:].find("</h5>");
            newIndex = indexA+indexB;
            description = page[indexA:newIndex];
            
            page = page[newIndex:];
            
            unlocked = (len(achievements) < numAchievementsUnlocked);
            
            achievements.append({
                "name":convertToSymbol(name),
                "description":convertToSymbol(description),
                "image":image,
                "unlocked":unlocked});
    print "Done.";
    return games;
        
def getGameAchievements( id ):
    games = getPlayerAchievements(id,getGames(id));
    
    debug_count = 0;
    games_length = str(len(games));
    
    print "Loading all LOCKED achievements for all of " + id + "'s games:";
    
    game = None
    for gameID in games:
        game = games[gameID]
        debug_count += 1;
        
        if data is not None and data.has_key(gameID):
            if not game.has_key("hours_forever") or not game.has_key("last_played"):
                games[gameID] = data[gameID]
                continue;
            
            if data.has_key(gameID):
                if game["last_played"] == data[gameID]["last_played"]:
                    games[gameID] = data[gameID]
                    continue;
        
        page = getPage( getURL_gameAchievements(game["friendlyURL"]) );
        
        print str(debug_count).rjust(4) + " of " + games_length + " - " + game["name"];
        
        newIndex = page.find(".jpg")+4;
        page = page[newIndex:];
        
        gameAchievements = [];
        
        while True:
            indexA = page.find("http://cdn.akamai.steamstatic.com/steamcommunity/public/images/");
            if indexA == -1: break;
            indexB = page.find(".jpg")+4;
            image = page[indexA:indexB];
            
            page = page[indexB:]
        
            indexA = page.find("<h3>");
            if indexA == -1: break;
            indexA += 4;
            indexB = page[indexA:].find("</h3>");
            newIndex = indexA+indexB;
            name = page[indexA:newIndex];
            
            page = page[newIndex:]
            
            indexA = page.find("<h5>");
            if indexA == -1: break;
            indexA += 4;
            indexB = page[indexA:].find("</h5>");
            newIndex = indexA+indexB;
            description = page[indexA:newIndex];
            
            gameAchievements.append({
                "name":convertToSymbol(name),
                "description":convertToSymbol(description),
                "image":image});
        
        for achievement in game["achievements"]:
            if achievement["unlocked"]:
                achievement["unlocked_image"] = achievement["image"];
                continue;
            achievement["unlocked_image"] = "ERROR.jpg";
            for gameAchievement in gameAchievements:
                if gameAchievement["name"] == achievement["name"]:
                    achievement["unlocked_image"] = gameAchievement["image"];
                    break;
    print "Done.";
    return games;

def getGenres( appid ):
    page = getPage("http://store.steampowered.com/app/" + str(appid));
    index = page.find('<div class="details_block">');
    page = page[index:];
    index = page.find('<!-- End Right Column -->');
    page = page[0:index];
    genres = [];
    while True:
        index = page.find("http://store.steampowered.com/genre/")
        if index == -1:
            break;
        index += 36;
        page = page[index:];
        index = page.find(">");
        index += 1;
        page = page[index:];
        index = page.find("<");
        genre = page[0:index];
        genres.append(genre);
    return genres;

def getGameTags( appid ):
    page = getPage("http://store.steampowered.com/app/"+str(appid));
    tags = [];
    findStr = "http://store.steampowered.com/tag/en/";
    page = page[page.find("glance_tags popular_tags"):];
    while True:
        index = page.find(findStr);
        if index == -1:
            break;
        page = page[index+len(findStr):];
        newTag = page[0:page.find("/")];
        newTag = newTag.replace("%20"," ");
        newTag = newTag.replace("%26","&");
        newTag = newTag.replace("%27","'");
        tags.append(newTag);
    return tags;
    
id = getID();

data = None
import os.path
if os.path.isfile("data_"+id+".py"):
    exec("from data_"+id+" import data");
if type(data) == list:
    data = None;
    
games = getGameAchievements(id);

print "Loading Genres...";
game = None;
for key in games:
    game = games[key];
    if game.has_key("genres"):
        continue;
    game["genres"] = getGenres(game["appid"]);
    if len(game["genres"]) == 0:
        print game["name"] + " has no listed genres.";
    elif len(game["genres"]) == 1:
        print game["name"] + "'s genre: " + str(game["genres"][0]);
    else:
        genre_str = "";
        for i in range(0,len(game["genres"])-1):
            genre_str += str(game["genres"][i]);
            genre_str += ", ";
        genre_str += "and " + str(game["genres"][len(game["genres"])-1]);
        print game["name"] + " has " + str(len(game["genres"])) + " genres: " + genre_str;

print "Done.";
        
print "Loading Tags...";

game = None;
for key in games:
    game = games[key];
    if not game.has_key("tags"):
        game["tags"] = getGameTags(game["appid"]);
    else:
        continue;
        
    if len(game["tags"]) == 0:
        print game["name"] + " has no listed tags.";
    else:
        tag_str = "";
        for i in range(0,len(game["tags"])-1):
            tag_str += str(game["tags"][i]);
            tag_str += ", ";
        tag_str += "and " + str(game["tags"][len(game["tags"])-1]);
        print game["name"] + " has " + str(len(game["tags"])) + " tags: " + tag_str;
        
print "Done.";
        
data_file = open( "data_" + id + ".py", "w" );
data_file.write("data = " + str(games));
data_file.flush();
data_file.close();

'''
handle = open( "handle_cheevos_" + id + ".py", "w" );
handle.write("from data_" + id + " import data\n");
handle.write("id = \"" + id + "\";\n" );
handle.flush();
template = open( "handle_cheevos.py", "r" );
line = "";
while True:
    line = template.readline();
    if len(line) == 0:
        break;
    handle.write(line);
    handle.flush();
    

handle.flush();
handle.close();
template.close();
'''
    






















