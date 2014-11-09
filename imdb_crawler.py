import urllib;
import sys;
import time;

def init():
    showName = getShowName();
    searchURL = getSearchURL(showName);
    pageURL = getPageURL(searchURL);
    numSeasons = getNumSeasons(pageURL);
    print showName + " has " + str(numSeasons) + " seasons"
    episodes = getAllEpisodes( showName, pageURL, numSeasons );
    writeFile( showName, episodes );
    print str(len(episodes)) + " episodes collected"

def getShowName():
    if len(sys.argv) != 2:
        print "Please input a show name";
        sys.exit(1);
    else:
        return sys.argv[1];
        
def getPage( url ):
    page = ""
    while True:
        try:
            http = urllib.urlopen(url);
            line = ""
            while True:
                line = http.readline();
                if len(line) == 0:
                    break;
                page += line
        except Exception,e:
            continue;
        break;
    return page;
    
def getSearchURL( search ):
    return "http://www.imdb.com/find?q=" + search.replace(" ","+")
    
def getPageURL( searchURL ):
    page = getPage(searchURL);
    page = page[page.find('<a href="/title/')+9:];
    page = "http://imdb.com" + page[0:page.find("?")-1]
    return page;
    
def getNumSeasons( pageURL ):
    if pageURL.find("tt0121955") != -1:
        return 18;
    if pageURL.find("tt0912343") != -1:
        return 5;

    page = getPage(pageURL);
    search = pageURL[15:] + "/episodes?season=";
    
    for numSeasons in range(1,50):
        if page.find(search+str(numSeasons)) == -1:
            return numSeasons-1;
    return 0;
    
def getSeasonURL( pageURL, seasonNum ):
    return pageURL + "/episodes?season=" + str(seasonNum);
    
def getAllEpisodes( showName, pageURL, numSeasons ):
    episodes = [];
    for i in range(0,numSeasons):
        print "Getting Season " + str(i+1);
        seasonURL = getSeasonURL(pageURL,i+1);
        episodes.extend(getEpisodes( showName, i+1, seasonURL ));
    return episodes;
    
def getEpisodes( showName, seasonNumber, seasonURL ):
    page = getPage(seasonURL);
    page = page[page.find("list detail eplist"):];
    episodes = [];
    
    episodeNumber = 1;
    
    while True:
        index = page.find('<a href="/title/');
        if index == -1:
            break;
        page = page[index+1:];
        if (page[:100]).find("epcast") != -1:
            break;
        if (page[:100]).find('itemprop="url"') != -1:
            continue;
        episodeInfo = getEpisodeInfo( showName, page[:1000] )
        episodeInfo.extend([seasonNumber,episodeNumber])
        episodes.append( episodeInfo );
        episodeNumber += 1;
    return episodes;
    
def getEpisodeInfo( showName, episode ):
    name_search = 'itemprop="name">';
    description_search = '<div class="item_description" itemprop="description">';
    
    episode = episode[episode.find(name_search)+len(name_search):];
    name = episode[:episode.find('</a>')];
    
    episode = episode[episode.find(description_search)+len(description_search):];
    description = episode[:episode.find('</div>')].replace('\n','').replace('\r','').strip();
    
    imageURL = getImageURL( showName, name );
    
    return [name,description,imageURL]
    
def getImageURL( showName, name ):
    import urllib2
    import simplejson
    
    numTries = 0;
    numTriesLimit = 3;
    
    while True:
        try:
            numTries += 1;
            if numTries > numTriesLimit:
                return "";
            
            searchTerm = '"' + showName + '" episode "' + name + '" -set -amazon -TUBE+ -Anniversary';
            searchTerm = searchTerm.replace(' ','%20')
            
            url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+searchTerm+'&start=0&userip=MyIP')
            
            request = urllib2.Request(url, None, {'Referer': 'testing'})
            response = urllib2.urlopen(request)
            
            results = simplejson.load(response)
            data = results['responseData']
            dataInfo = data['results']
            
            result = dataInfo[0]['unescapedUrl']
            
            return result;
        except Exception,e:
            print e;
            time.sleep(1)
    
    
def writeFile( showName, episodes ):
    f = file(showName.replace(" ","_")+".js", "w");
    
    f.write(showName.replace(" ","_").replace("-","_")+'_episodes = [');
    for i in range(0,len(episodes)-1):
        f.write(str(episodes[i]) + ",");
    f.write(str(episodes[-1]) + "]");
    
    f.flush();
    f.close();
    
init();