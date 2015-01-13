from steam_time_shaymus22 import data

remainingTime = {};

def conv(s):
    return s.replace('True','true').replace('False','false');

game = None
for g in data:
    game = data[g];
    if game.has_key("time_information"):
        hours = str(game["time_information"]["hours_remaining"]);
        if remainingTime.has_key(hours):
            remainingTime[hours].append(game);
        else:
            remainingTime[hours] = [game];

sorted_keys = remainingTime.keys();
for i in range(0,len(sorted_keys)):
    sorted_keys[i] = float(sorted_keys[i]);
sorted_keys.sort();

for k in sorted_keys:
    for g in remainingTime[str(k)]:
        print str(k).rjust(8) + " " + g["name"]