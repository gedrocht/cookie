import urllib;
import sys;

def getID():
    if len(sys.argv) != 2:
        print "Please input a Steam ID";
        sys.exit(1);
    else:
        return sys.argv[1];
        
id = getID();
print "Generating tagdb_"+str(id)+".js";
exec("from data_"+str(id)+" import data");

uniqueTags = [];

game = None;
for key in data:
    game = data[key];
    if not game.has_key("tags"):
        continue;
    for tag in game["tags"]:
        if not uniqueTags.__contains__(tag):
            uniqueTags.append(tag);

pairs = [];
highest = 0;

for tag in uniqueTags:
    count = 0;
    game = None;
    for key in data:
        game = data[key];
        if not game.has_key("tags"):
            continue;
        if( game["tags"].__contains__(tag) ):
            count += 1;
            
    if count > highest:
        highest = count;
        
    pairs.append([count,tag]);
    

def convertTag( tag ):
    return tag.replace(" ","_").replace("-","").replace("&","").replace(".","").replace("'","").replace("#","").replace(";","").replace(":","").replace("!","").replace(",","").replace("(","").replace(")","").replace("+","").replace("?","");
    
js = open("tagdb_"+str(id)+".js","w");
js.write("tags = {};\n");

'''    
i = highest;
while i > -1:
    for pair in pairs:
        if pair[0] == i:
            tagName = convertTag(pair[1]);
            js.write("var tag_" + tagName + " = [];\n");
            game = None;
            for key in data:
                game = data[key];
                if not game.has_key("tags"):
                    continue;
                if game["tags"].__contains__(pair[1]):
                    js.write("tag_" + tagName + ".push(\"" + convertTag(str(game["name"])) + "\");\n");
            js.write("tags[\"" + tagName + "\"] = tag_" + tagName + ";\n");
            js.flush();
    
    js.flush();
    i -= 1;
'''
sortedGames = {};
for key in data:
    sortedGames[str(data[key]["name"])] = key

game = None;
for tag in sorted(uniqueTags):
    tagName = convertTag(tag);
    js.write("var tag_" + str(tagName) + " = [];\n");
    for key in sorted(sortedGames):
        game = data[sortedGames[key]];
        if not game.has_key("tags"):
            continue;
        if game["tags"].__contains__(tag):
            js.write("tag_" + tagName + ".push(\"" + convertTag(str(game["name"])) + "\");\n");
    js.write("tags[\"" + tagName + "\"] = tag_" + tagName + ";\n");
    js.flush();
    
js.write("games = {};\n");
js.flush();

game = None;
for key in data:
    game = data[key];
    gameName = convertTag(str(game["name"]));
    js.write("var game_" + gameName + " = [];\n");
    if game.has_key("tags"):
        for tag in game["tags"]:
            js.write("game_" + gameName + ".push(\"" + convertTag(str(tag)) + "\");\n");
    js.write("games[\"" + gameName + "\"] = game_" + gameName + ";\n");
    js.flush();

js.write("appids = {};\n");
js.flush();

game = None;
for key in data:
    game = data[key];
    gameName = convertTag(str(game["name"]));
    appid = str(key);
    js.write("appids['"+gameName+"'] = '" + appid +"';\n");
    js.flush();
    
js.write("games_realNames = {};\n");
js.flush();

game = None;
for key in data:
    game = data[key];
    jsName = convertTag(str(game["name"]));
    gameName = str(game["name"]).replace("'","\\'").replace("\"","\\\"");
    js.write("games_realNames['" + jsName + "'] = '" + gameName + "';\n");
    js.flush();

js.write("tags_realNames = {};\n");
js.flush();

for i in range(0,len(uniqueTags)):
    jsName = convertTag(uniqueTags[i]);
    realName = str(uniqueTags[i]).replace("'","\\'").replace("\"","\\\"");
    js.write("tags_realNames['" + jsName + "'] = '" + realName + "';\n");
    js.flush();
    
js.flush();
js.close();

print "Done.";












