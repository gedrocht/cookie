#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import math
import tweepy, time, sys
import datetime
from google_image_getter import downloadSearchImage
from tweepy import TweepError
 
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

NUMBER_OF_SEGMENTS = 3

def generateSentence(segments):
	sentence = ""
	for i in range(1,NUMBER_OF_SEGMENTS+1):
		sentence += segments[str(i)].strip() + " ";
	
	return sentence

def old_splitTweet(tweet):
	segments = {};
	step = (len(line)/float(NUMBER_OF_SEGMENTS))
	for i in range(1,NUMBER_OF_SEGMENTS+1):
		percentage = float(i)/float(NUMBER_OF_SEGMENTS)
		beginning = int(step*i-step)
		end = int(step*i)
		segments[str(i)] = tweet[beginning:end]
	#print segments
	return segments
	
def splitLine(line):
	segments = [];
	
	words = line.split(" ")
	step = len(words)/NUMBER_OF_SEGMENTS;
	
	for i in range(0,NUMBER_OF_SEGMENTS):
		if i == NUMBER_OF_SEGMENTS-1:
			segments.append(words[step*i:len(words)])
		else:
			segments.append(words[step*i:step*(i+1)])
	return segments;
	
for line in f:
	splitLine(line)
	lines.append(splitLine(line.strip()))

imageOverride = False

while True:
	tweet = "";
	
	indexes = [];
	while len(indexes) < NUMBER_OF_SEGMENTS:
		new_index = int(math.floor(random.random()*len(lines)));
		if not indexes.__contains__(new_index):
			indexes.append(new_index);
	
	for i in range(0,NUMBER_OF_SEGMENTS):
		tweet += " ".join(lines[indexes[i]][i]).strip();
		if i != NUMBER_OF_SEGMENTS - 1:
			tweet += " ";
	
	tweet = tweet.strip();
	tweet = tweet[:1].capitalize() + tweet[1:]
	tweet = tweet.replace("   "," ").replace("  "," ")
	
	if len(tweet) > 140:
		while len(tweet) > 137:
			tweet = tweet[0:tweet.rfind(" ")]
		tweet += "..."
	
	try:
		search_string = tweet;
		search_string_location = int(math.floor(random.random()*(len(search_string.split(" "))-5)))
		if len(search_string.split(" ")) > 5:
			search_string = " ".join(search_string.split(" ")[search_string_location:]);
		imageResult = downloadSearchImage(search_string)

		if random.random() < 0.33 and not imageOverride:
			print "{0}: TEXT: {1}".format(datetime.datetime.now(),tweet)
			api.update_status(tweet)
		elif imageResult is None:
			imageOverride = True;
			print "{0}: TRIED TO TWEET AN IMAGE BUT NO IMAGES FOUND, RETRYING".format(str(datetime.datetime.now()))
			continue
		else:
			print "{0}: IMAGE WITH TEXT: {1}".format(datetime.datetime.now(),tweet)
			imageOverride = False;
			api.update_with_media(imageResult[0], status=tweet)
		
		interval = int(round(random.random()*120*60)) + 90*60;
		#print '{0}: Sent tweet "{1}"'.format(str(datetime.datetime.now()), tweet)
		hour = datetime.datetime.now().hour
		while hour > 23 or hour < 7:
			hour = datetime.datetime.now().hour
			print "{0}: It's too late/early to tweet. Waiting for 15 minutes...".format(str(datetime.datetime.now()), tweet)
			time.sleep(60*15)
		time.sleep(interval)   
	except TweepError:
		print "burp"