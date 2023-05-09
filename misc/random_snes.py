from os import walk
import random
import os
import time

romdir = "../ROMS/SNES"
roms = [];
for (dirpath, dirnames, filenames) in walk(romdir):
    roms.extend(filenames);
    break;

random.seed()

game = None
while True:
    game = roms[random.randint(0,len(roms)-1)];
    print game
    time.sleep(6)
    os.system("../zsnesw142/zsnesw.exe " + romdir + "/\"" + game + "\"")