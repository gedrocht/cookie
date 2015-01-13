def getID():
    if len(sys.argv) != 2:
        print "Please input a Steam ID";
        sys.exit(1);
    else:
        return sys.argv[1];
        
id = getID();
exec("from data_"+str(id)+" import data");

unplayed = [];

for d in data:
    game = data[d];
    if game.has_key("hours_forever"):
        continue;
    unplayed.append(game);

print len(unplayed);