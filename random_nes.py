from os import walk
import random
import os
import time

romdir = "../ROMS/NES"
roms = [];
for (dirpath, dirnames, filenames) in walk(romdir):
    roms.extend(filenames);
    break;

random.seed()

game = None
while True:
    game = roms[random.randint(0,len(roms)-1)];
    print game
    time.sleep(3)
    os.system("../fceux-2.2.2-win32/fceux.exe " + romdir + "/\"" + game + "\"")