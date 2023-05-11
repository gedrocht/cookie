import urllib;
import sys;

if len(sys.argv) < 3:
    print "Please input a Steam ID and genre request";
    sys.exit(1);

def getID():
    return sys.argv[1];

def getGenres():
    if len(sys.argv) == 3:
        return [sys.argv[2]];
    else:
        genres = [];
        for i in range(2,len(sys.argv)):
            genres.append(sys.argv[i]);
        return genres;
        
id = getID();
genres = getGenres();
exec("from data_"+id+" import data");

game = None;
for key in data:
    game = data[key];
    if not game.has_key("genres"):
        continue;
        
    containsAll = True;
    
    for g in genres:
        if not game["genres"].__contains__(g):
            containsAll = False;
            break;
    
    if not containsAll:
        continue;
    
    print game["name"]

