import urllib;
import sys;
import time;

def init():
    gameName = getGameName();

def getGameName():
    if len(sys.argv) != 2:
        print "Please input a game name";
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
    
