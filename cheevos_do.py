import sys

if len(sys.argv) != 2:
    print "Please input a steam ID"
    sys.exit(1);
    
id = sys.argv[1];

exec("from data_"+id+" import data");

cheevos = []
most = 0;
percent = 0;

game = None
for gameID in data:
    game = data[gameID]
    if len(game["achievements"]) == 0:
        continue;
    
    not_unlocked = 0;
    
    for achievement in game["achievements"]:
        if not achievement["unlocked"]:
            not_unlocked += 1;
    
    percent = int(round((1-not_unlocked/float(len(game["achievements"])))*100));
    
    cheevos.append([100-percent,game,not_unlocked]);
    if percent > most:
        most = percent;
        
for i in range(0,int(most+1)):
    for pair in cheevos:
        game = pair[1];
        if pair[0] == i:
            numCheevos = len(game["achievements"]);
            #print str(100-pair[0]).rjust(4) + " % (" + str(numCheevos-pair[2]).rjust(3) +  "/" + str(numCheevos).ljust(3) + " - " + str(pair[2]).rjust(3) + " ) " + game["name"];
    
    
xml = open("cheevos_"+id+".xml","w");
xml.write('<?xml version="1.0" encoding="UTF-8"?>\n');
#xml.write('<?xml-stylesheet type="text/xsl" href="file:///L:/Downloads/cheevos_'+id+'.xml" ?>\n');

count = 0;

xml.write("<games>\n");
game = None
for gameID in data:
    game = data[gameID]
    xml.write("<game>\n");
    xml.write("\t<name>\n\t\t" + game["name"].replace("&","&amp;") + "\n\t</name>\n");
    xml.write("\t\t<achievements>\n");
    for achievement in game["achievements"]:
        if achievement["unlocked"]: continue;
        xml.write("\t\t\t<achievement>\n");
        xml.write("\t\t\t\t<name>\n");
        xml.write("\t\t\t\t\t" + achievement["name"].replace("&","&amp;") + "\n");
        xml.write("\t\t\t\t</name>\n");
        xml.write("\t\t\t\t<description>\n");
        xml.write("\t\t\t\t\t" + achievement["description"].replace("&","&amp;") + "\n");
        xml.write("\t\t\t\t</description>\n");
        xml.write("\t\t\t</achievement>\n");
    xml.write("\t\t</achievements>\n");
    xml.write("</game>\n");
    xml.flush();
    count += 1;
    if count > 10:
        break;
xml.write("</games>\n");
xml.flush();
xml.close();

totalUnlockedCheevos = 0;

game = None
for gameID in data:
    game = data[gameID]
    for cheevo in game["achievements"]:
        if cheevo["unlocked"]: totalUnlockedCheevos += 1;

show = open("allcheevos_" + id + ".html", "w");

show.write('<head><title>' + str(totalUnlockedCheevos) + ' Achievables!</title></head>\n');
show.write('<body link="#aaaaaa" alink="#cccccc" vlink="#aaaaaa" style="background-color:#2d2d2b; background-position:0px 0px; background-repeat: no-repeat;">\n');
show.write('<font face="Arial" color="#bababa"><center>\n');

for gameID in data:
    game = data[gameID]
    for cheevo in game["achievements"]:
        if cheevo["unlocked"]:
            show.write('<a href="steam://run/' + str(game["appid"]) + '">\n');
            show.write('<img width="64px" height="64px" src="' + cheevo["image"] + '" title="' + game["name"] + ': ' + cheevo["name"] + ': ' + cheevo["description"] + '"></img></a>\n');
            

show.flush();
show.close();

def startHTML( cheevoListFile, startIndex, endIndex ):
    cheevoListFile.write('<html>\n');
    cheevoListFile.write('<head>\n');
    cheevoListFile.write('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n');
    cheevoListFile.write('<style type="text/css">\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('body{\n');
    cheevoListFile.write('    background-color: #2d2d2b;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.gameText{\n');
    cheevoListFile.write('    width: 700px; \n');
    cheevoListFile.write('    margin-top: 16px;\n');
    cheevoListFile.write('    margin-left: 195px;\n');
    cheevoListFile.write('    color: #eee;\n');
    cheevoListFile.write('    font-family: Arial;\n');
    cheevoListFile.write('    font-size: 38px;\n');
    cheevoListFile.write('    text-shadow: #262627 0px 0px 6px;\n');
    cheevoListFile.write('    overflow: hidden;\n');
    cheevoListFile.write('    white-space: nowrap;\n');
    cheevoListFile.write('    -webkit-user-select: none;\n');
    cheevoListFile.write('    -moz-user-select: none;\n');
    cheevoListFile.write('    -ms-user-select: none;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievement-container{\n');
    cheevoListFile.write('    width: 900px;\n');
    cheevoListFile.write('    height: 75px;\n');
    cheevoListFile.write('    margin-top: -3px;\n');
    cheevoListFile.write('    margin-left: auto;\n');
    cheevoListFile.write('    margin-right: auto;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievement{\n');
    cheevoListFile.write('    width: 900px;\n'); #800
    cheevoListFile.write('    height: 75px;\n');
    cheevoListFile.write('    margin-left: -1px;\n'); #99
    cheevoListFile.write('    margin-top: 3px;\n');
    cheevoListFile.write('    background-color:#191919;\n');
    cheevoListFile.write('    border: 1px solid #a8a8a8;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievementImageContainer{\n');
    cheevoListFile.write('    width: 80px;\n');
    cheevoListFile.write('    height: 75px;\n');
    cheevoListFile.write('    float: left;\n');
    cheevoListFile.write('    padding: 0px;\n');
    cheevoListFile.write('    margin: 0px;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievementImageContainer{\n');
    cheevoListFile.write('    width: 64px;\n');
    cheevoListFile.write('    height: 64px;\n');
    cheevoListFile.write('    padding: 5px;\n');
    cheevoListFile.write('    margin-right: 3px;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievementTextContainer{\n');
    cheevoListFile.write('    width: 900px;\n'); #720
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievementText{\n');
    cheevoListFile.write('    margin: 3px;\n');
    cheevoListFile.write('    padding: 3px;\n');
    cheevoListFile.write('    padding-left: 6px;\n');
    cheevoListFile.write('    padding-top: 11px;\n');
    cheevoListFile.write('    font-family: Arial;\n');
    cheevoListFile.write('    color: #bebebe;\n');
    cheevoListFile.write('    overflow: hidden;\n');
    cheevoListFile.write('    white-space: nowrap;n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.write('.achievementTitle{\n');
    cheevoListFile.write('    font-size:22;\n');
    cheevoListFile.write('    font-family: Arial;\n');
    cheevoListFile.write('    font-weight: normal;\n');
    cheevoListFile.write('}\n');
    cheevoListFile.write('\n');
    cheevoListFile.flush();
        
    #for game in data:
    game = None;
    if endIndex > len(orderedList):
        endIndex = len(orderedList);
    
    for i in range(startIndex, endIndex):
        game = orderedList[i][0];
        
        cheevoListFile.write('.game-' + str(game["appid"]) + '{\n');
        cheevoListFile.write('    background-image: url(http://steamcommunity-a.akamaihd.net/public/images/skin_1/achievementProgressBar.gif);\n');
        cheevoListFile.write('    background-position: 190px 3px;\n');
        cheevoListFile.write('    background-repeat: no-repeat;\n');
        cheevoListFile.write('    width: 900px;\n');
        cheevoListFile.write('    height: 75px;\n');
        cheevoListFile.write('    border: 1px solid #eee;\n');
        cheevoListFile.write('    border-bottom: 1px solid #eee;\n');
        cheevoListFile.write('    margin-left: auto;\n');
        cheevoListFile.write('    margin-right: auto;\n');
        cheevoListFile.write('    margin-top: 20px;\n');
        cheevoListFile.write('    display: block;\n');
        cheevoListFile.write('    position: relative;\n');
        cheevoListFile.write('}\n');
        cheevoListFile.write('\n');
        cheevoListFile.write('.game-' + str(game["appid"]) + '::after{\n');
        cheevoListFile.write('    content: "";\n');
        cheevoListFile.write('    background: url(http://cdn.akamai.steamstatic.com/steam/apps/' + str(game["appid"]) + '/capsule_184x69.jpg);\n');
        cheevoListFile.write('    opacity: 1;\n');
        cheevoListFile.write('    top: 0;\n');
        cheevoListFile.write('    left: 0;\n');
        cheevoListFile.write('    bottom: 0;\n');
        cheevoListFile.write('    right: 0;\n');
        cheevoListFile.write('    position: absolute;\n');
        cheevoListFile.write('    z-index: -1;\n');
        cheevoListFile.write('    background-position: 3px 3px;\n');
        cheevoListFile.write('    background-repeat: no-repeat;\n');
        cheevoListFile.write('}\n');
        cheevoListFile.write('.game-' + str(game["appid"]) + '::before{\n');
        cheevoListFile.write('    content: "";\n');
        cheevoListFile.write('    background: url(http://i.imgur.com/IF9rup9.jpg);\n');
        cheevoListFile.write('    opacity: 1;\n');
        cheevoListFile.write('    top: 0;\n');
        cheevoListFile.write('    left: 0;\n');
        cheevoListFile.write('    bottom: 0;\n');
        cheevoListFile.write('    right: 0;\n');
        cheevoListFile.write('    position: absolute;\n');
        cheevoListFile.write('    z-index: -1;\n');
        cheevoListFile.write('    background-position: 190px 3px;\n');
        cheevoListFile.write('    background-repeat: no-repeat;\n');
        cheevoListFile.write('}\n');
        cheevoListFile.flush();

    cheevoListFile.write('</style>\n');
    cheevoListFile.write('</head>\n');
    cheevoListFile.write('<body vlink="#cdcdcd" alink="#e2e2e2" link="#dfdfdf">\n');

def finishHTML( cheevoListFile, areThereMoreGames ):
    cheevoListFile.write('<br><br>\n');
    cheevoListFile.write('<font face="Arial" size="+4">\n');
    if numPages != 1:
        cheevoListFile.write('<div style="margin-left:auto; margin-right:auto; text-align:center;">\n');
        cheevoListFile.write('<a style="text-decoration:none" href="cheevoList_'+id+'_page1.html">FIRST</a>');
        cheevoListFile.write(' &nbsp; &nbsp; &nbsp; ');
        cheevoListFile.write('<a style="text-decoration:none" href="cheevoList_'+id+'_page'+str(numPages-1)+'.html">PREV</a>');
        if areThereMoreGames:
            cheevoListFile.write(' &nbsp; &nbsp; &nbsp; ');
        else:
            cheevoListFile.write('\n</div>\n');
        
    
    if areThereMoreGames:
        if numPages == 1:
            cheevoListFile.write('<div style="margin-left:auto; margin-right:auto; text-align:center;">\n');
        cheevoListFile.write('<a style="text-decoration:none" href="cheevoList_'+id+'_page'+str(numPages+1)+'.html">NEXT</a>\n');
        cheevoListFile.write('\n</div>\n');
                         
    cheevoListFile.write('</font>\n<br><br><br><br><br><br>\n');
    cheevoListFile.flush();
    cheevoListFile.close();
    
lockedCheevoGames = []

mostLockedCheevos = 0;

game = None
for gameID in data:
    game = data[gameID]
    if len(game["achievements"]) == 0:
        continue;

    lockedCheevos = [];
    
    for cheevo in game["achievements"]:
        if not cheevo["unlocked"]:
            lockedCheevos.append(cheevo);
            
    if len(lockedCheevos) > mostLockedCheevos:
        mostLockedCheevos = len(lockedCheevos);
    
    if len(lockedCheevos) == 0: continue;
    
    percentage = int((1-float(len(lockedCheevos))/float(len(game["achievements"])))*100.0);
    
    lockedCheevoGames.append([game,lockedCheevos,percentage]);

numPages = 1;
numGames = 0;
gamesPerPage = 10;
numGamesTotal = 0;

orderedList = []

i = 101;
while True:
    if i < 0: break;
    i -= 1;
    
    for datum in lockedCheevoGames:
        if datum[2] != i: continue;
    
        orderedList.append(datum);
    

cheevoList = open("cheevoList_"+id+"_page1.html","w");
startHTML(cheevoList,0,gamesPerPage);
areThereMoreGames = True;

for datum in orderedList:
    if not areThereMoreGames:
        break;
    game = datum[0];
    cheevos = datum[1];

    gameNameStr = game["name"];
    if len(gameNameStr) > 60:
        gameNameStr = gameNameStr[:60];

    
    width = int((float(datum[2])/100) * 707.0)
    
    #cheevoList.write('<a style="text-decoration:none;" href="steam://run/' + str(game["appid"]) + '">\n');
    cheevoList.write('<div class="game-' + str(game["appid"]) + '" style="background-size: ' + str(width) + 'px 69px;" ' + 
                     'onclick="x=document.getElementById(' + str(game["appid"]) + '); if(x.style.display==\'block\'){x.style.display=\'none\'; this.style.borderBottom=\'1px solid #eee\';\n}else{x.style.display=\'block\'; this.style.borderBottom=\'0px solid #eee\';}">\n');
    cheevoList.write('\t<div class="gameText">' + gameNameStr + '</div>\n');
    cheevoList.write('</div>\n');
    #cheevoList.write('</a>\n');
    
    for cheevo in cheevos:
        cheevoList.write('<div style="display:none; background-image:url(' + cheevo["unlocked_image"] + ');"></div>\n');
        cheevoList.write('<div style="display:none; background-image:url(' + cheevo["image"] + ');"></div>\n');
    
    cheevoList.write('<div style="display:none;" id="' + str(game["appid"]) + '">\n');
    for cheevo in cheevos:
        '''
        cheevoList.write('<div style="display:none; background-image:url(' + cheevo["unlocked_image"] + ');"></div>\n');
        '''
        cheevoList.write('<div class="achievement-container" ' +
        #x = document.getElementsByTagName("div")[2].childNodes[1].childNodes[1].childNodes[1].childNodes[1].parentNode.nextSibling.nextSibling.childNodes[1]
                         'onmouseover="var tmp=this.childNodes[1].childNodes[1].childNodes[1].childNodes[1]; tmp.parentNode.nextSibling.nextSibling.childNodes[1].style.color=\'#e0e0e0\'; tmp.src=\'' + cheevo["unlocked_image"] + '\';" ' +
                          'onmouseout="var tmp=this.childNodes[1].childNodes[1].childNodes[1].childNodes[1]; tmp.parentNode.nextSibling.nextSibling.childNodes[1].style.color=\'#bebebe\'; tmp.src=\'' + cheevo["image"]          + '\';">\n');
        cheevoList.write('<a style="text-decoration:none;" href="steam://run/' + str(game["appid"]) + '">\n');
        cheevoList.write('\t<div class="achievement">\n');
        cheevoList.write('\t\t<div class="achievementImageContainer">\n');
        cheevoList.write('\t\t\t<img class="achievementImage" src="' + cheevo["image"] + '" ' + 
                         #'onmouseover="this.src=\'' + cheevo["unlocked_image"] + '\';" ' + 
                         #'onmouseout="this.src=\'' + cheevo["image"] + '\';"' +
                         '></img>\n');
        cheevoList.write('\t\t</div>\n');
        cheevoList.write('\t\t<div class="achievementTextContainer">\n');
        cheevoList.write('\t\t\t<div class="achievementText">\n');
        cheevoList.write('\t\t\t\t<span class="achievementTitle">' + cheevo["name"] + '</span><br>\n');
        cheevoList.write('\t\t\t\t' + cheevo["description"] + '\n');
        cheevoList.write('\t\t\t</div>\n');
        cheevoList.write('\t\t</div>\n');
        cheevoList.write('\t</div>\n');
        cheevoList.write('</a></div>\n\n');
    cheevoList.write('</div>\n');
    cheevoList.flush();
    
    numGamesTotal += 1;
    numGames += 1;
    if numGames == gamesPerPage:
        areThereMoreGames = (numGamesTotal < len(orderedList)-1);
        finishHTML( cheevoList, areThereMoreGames );
        numGames = 0;
        numPages += 1;
        if areThereMoreGames:
            cheevoList = open("cheevoList_"+id+"_page" + str(numPages) + ".html","w");
            startHTML( cheevoList, numGamesTotal, numGamesTotal + gamesPerPage );

#finishHTML( cheevoList, False );


##############################

gameDB_js = open("gameDB_"+id+".js","w");
gameDB_js.write('game_db = \n')

gameDB_js.write( str(orderedList).replace("True","true").replace("False","false").replace("100%","100Percent") );
gameDB_js.close();


##############################

'''
<div class="game" style="background-size: 898px 73px;">
    <div class="gameText">Garry's Mod</div> <!--23 chars max-->
</div>
<div class="achievement-container">
    <div class="achievement">
        <div class="achievementImageContainer">
            <img class="achievementImage" src="error.jpg"></img>
        </div>
        <div class="achievementTextContainer">
            <div class="achievementText">
                <span class="achievementTitle">Superman</span><br>
                You saved da city
            </div>
        </div>
    </div>
</div>
'''























