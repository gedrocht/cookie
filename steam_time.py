from steam_shaymus22 import data

game = None;
longest = 56;

times = open("steam_shaymus22_times.txt","w");

for g in data:
    game = data[g];
    times.write(game["name"].ljust(longest)+"\n")

times.flush();
times.close();