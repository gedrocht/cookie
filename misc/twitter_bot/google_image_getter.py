import urllib
import urllib2
import time

def searchGoogle(search):
	user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
	
	url = "http://www.google.com/search?hl=en&tbm=isch&safe=on=Monkey"
	headers={'User-Agent':user_agent,} 
	
	request=urllib2.Request(url,None,headers)
	response = urllib2.urlopen(request)
	data = response.read()
	return data

'''	
def getImageResult(index=1):
	index = 0;
	for i in range(0,i):
		if 
'''
def getFirstImage(searchResults):
	clipAmount = 5;
	index = searchResults.find(".jpeg")
	if index == -1:
		index = searchResults.find(".jpg")
		clipAmount = 4
	if index == -1:
		index = searchResults.find(".png")
		clipAmount = 4
	if index == -1:
		return None;
	index += clipAmount
	searchResults = searchResults[:index]
	index = searchResults.rfind("\"")+1
	searchResults = searchResults[index:]
	return searchResults

def getSearchURL(search):
	#return "http://www.google.com/search?site=&tbm=isch&q={0}".format(search);
	return "https://www.bing.com/images/search?q={0}".format(clean(search));
	
def getSite(url):
	response = urllib2.urlopen(url)
	return response.read()
	
def clean(text):
	return text.replace(" ","%20").replace("&","").replace("!","").replace("?","").replace("#","").replace("<","").replace(">","").replace("@","").replace(":","").replace("|","").replace("*","").replace("\\","").replace("/","")
	
def downloadSearchImage(search):
	#return urllib.urlretrieve(getFirstImage(getSite(getSearchURL(search))), search+"_search_result.jpeg")
	while True:
		image = getFirstImage(getSite(getSearchURL(search)))
		if image is None:
			print "Searching for {0} didn't work. Trying again...".format(search)
			#print getSite(getSearchURL(search))
			return
		else:
			try:
				return urllib.urlretrieve(image, "Images/"+clean(search).replace("%20"," ")+"_"+image[(image.rfind("/")+1):])
			except:
				return None
