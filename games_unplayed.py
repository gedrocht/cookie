from data_shaymus22 import data

unplayed = [];

for d in data:
    game = data[d];
    if game.has_key("hours_forever"):
        continue;
    unplayed.append(game);

print len(unplayed);