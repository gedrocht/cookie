from steam_shaymus22 import data

game = None;
longest = 56;

times = open("steam_shaymus22_times.txt","r");

gameTimes = {}

line = None
while True:
    line = times.readline()
    if len(line) == 0:
        break;
    line = line.strip();
    hours = line.split(" ")[-1];
    gameName = line[0:-len(hours)-1].strip()
    gameTimes[gameName] = float(hours);

times.close();
    
remainingTime = {}

for g in data:
    game = data[g];
    gameName = game["name"].strip();
    timeNeeded = gameTimes[gameName];
    
    if timeNeeded == 0:
        remainingTime[gameName] = None;
        continue;
    
    timePlayed = 0;
    if game.keys().__contains__("hours_forever"):
        timePlayed = float(game["hours_forever"]);
    
    time = {};
    time["hours_played"]    = timePlayed;
    time["hours_remaining"] = timeNeeded - timePlayed;
    time["hours_required"]  = timeNeeded;
    
    remainingTime[gameName] = time;

progress_offset = 0;
highest = 0;
for g in remainingTime:
    if remainingTime[g] is None:
        progress_offset += 1;
        continue;
    if remainingTime[g]["hours_remaining"] > highest:
        highest = remainingTime[g]["hours_remaining"];
    
sorted = [];
t = 0.0;
while True:
    if not t < (highest + 1):
        break;
    t += 0.01;
    for g in remainingTime:
        if remainingTime[g] is None:
            continue;
        if str(remainingTime[g]["hours_remaining"]) == str(t):
            print "Sorting " + str(len(sorted)+progress_offset).rjust(3) + "/" + str(len(remainingTime)-(progress_offset-1))
            sorted.append({'name':g,'time':remainingTime[g]});
    
ljust_amount = len(str(highest))+1;
#for g in sorted:
    #print " " + str(g["hours_remaining"]).ljust(ljust_amount) + " " + g["name"];

steam_time = open("steam_time_shaymus22.py","w");
    
for s in sorted:
    for g in data:
        game = data[g];
        if game["name"].strip() == s["name"]:
            game["time_information"] = s["time"]


steam_time.write("data = " + str(data));
steam_time.flush();
steam_time.close();





















