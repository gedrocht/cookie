import math


i = 0;
while i < 360:
    print str(i) + " degrees! x = " + str(math.cos(math.radians(i))) + "\t" + str(math.sin(math.radians(i)))
    i += 1
