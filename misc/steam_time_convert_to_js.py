print "Building Steam + HowLongToBeat database..."

from steam_time_shaymus22 import data

remainingTime = {};

def conv(s):
    return s.replace('True','true').replace('False','false').replace("100%","100Percent")

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

output = "data=[";
for k in sorted_keys:
    for g in remainingTime[str(k)]:
        output += conv("new Object({appid:" + str(g["appid"]) + ",name:'" + g["name"].replace("'","").replace("100%","100Percent") + "',time:new Object(" + str(g["time_information"]) + ")}),");
        
output = output[:-1] + "];";

js = open("steam_time_js.js","w");
js.write(output);
js.flush();
js.close();

print "Done."