import random
import math

swears = ["fuck", "shit", "cunt", "bitch", "whore", "testicle"];

swear = swears[int(math.floor(random.random() * len(swears)))]

while True:
	guess = raw_input("guess the swear!")
	if guess == swear:
		print "Naughty boy!";
		break;
	print "NOPE"