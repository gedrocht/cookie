import urllib;
import sys;

if len(sys.argv) < 3:
    print "Please input a Steam ID and tag request";
    sys.exit(1);

def getID():
    return sys.argv[1];

def getTags():
    if len(sys.argv) == 3:
        return [sys.argv[2]];
    else:
        tags = [];
        for i in range(2,len(sys.argv)):
            tags.append(sys.argv[i]);
        return tags;
        
id = getID();
tags = getTags();
exec("from data_"+id+" import data");

game = None;
for key in data:
    game = data[key];
    if not game.has_key("tags"):
        continue;
        
    containsAll = True;
    
    for g in tags:
        if not game["tags"].__contains__(g):
            containsAll = False;
            break;
    
    if not containsAll:
        continue;
    
    print game["name"]

