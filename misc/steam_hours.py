from steam_shaymus22 import data

game = None
for g in data:
    game = data[g];
    if game["name"] == "Half-Life 2":
        break;
hours = 13.5;
print game["name"] + " hours: " + game["hours_forever"]
print game["name"] + " hours needed for completion: " + str(hours);
percentage = 
print "percentage complete: " + str(round(int(game["hours_forever"])/hours*100,2)) + " %"