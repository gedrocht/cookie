#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
import tweepy, time, sys
import datetime
 
#argfile = str(sys.argv[1])
 
#enter the corresponding information from your Twitter application:
CONSUMER_KEY = 'Yk661Vn3aLJ85bkgma7rbP3Cp'#keep the quotes, replace this with your consumer key
CONSUMER_SECRET = 'yHs3NHPlXFgWCsJycvjUXLCJNHWVBLUyra1ThI2uTD21R7IZmp'#keep the quotes, replace this with your consumer secret key
ACCESS_KEY = '821497350149566464-Cp8GhTsjpB98NFGtH9jqpeYtDsV5Ys1'#keep the quotes, replace this with your access token
ACCESS_SECRET = 'YfwPQNnO60tTiARh8hJPpWtBcWQHH2V8nDmLwlA81UHQj'#keep the quotes, replace this with your access token secret
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
 
#filename=open(argfile,'r')
#f=filename.readlines()
#filename.close()
 
#for line in f:

filename=open("twitter_bot_data.txt",'r')
f=filename.readlines()
filename.close()

lines = []

NUMBER_OF_SEGMENTS = 6

def generateSentence(line):
	step = (len(line)/float(NUMBER_OF_SEGMENTS))
	
	for i in range(1,NUMBER_OF_SEGMENTS+1):
		percentage = float(i)/float(NUMBER_OF_SEGMENTS)
		beginning = int(step*i-step)
		end = int(step*i)
		#print "=============\n{0}".format(words)
		#print "[{0}:{1}]".format(beginning, end)
		segments.append(" ".join(words[beginning:end]))
		print " ".join(words[beginning:end])

for line in f:
	segments = []
	words = line.split(" ");
	print "========"
	

while True:
	tweet = "";
	
	indexes = [];
	while len(indexes) <3:
		new_index = int(math.floor(random.random()*len(lines)));
		if not indexes.__contains__(new_index):
			indexes.append(new_index);
		
	tweet = generateSentence(indexes);
	
	print api.rate_limit_status()
	#api.update_status(tweet)
	interval = int(round(random.random()*10*60)) + 10*60;
	#print '{0}: Sent tweet "{1}"'.format(str(datetime.datetime.now()), tweet)
	time.sleep(interval)