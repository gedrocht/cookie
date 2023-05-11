import sys
import time

def getSearchString():
    if len(sys.argv) != 2:
        print "Please input a search term";
        sys.exit(1);
    else:
        return sys.argv[1];
        
def getImageURL( search ):
    import urllib2
    import simplejson
    
    numTries = 0;
    numTriesLimit = 3;
    
    while True:
        try:
            numTries += 1;
            if numTries > numTriesLimit:
                return "";
            
            ret_results = [];
            for a in range(0,10):
                search= search.replace(' ','%20')
                
                url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+search+'&start='+str(a*4)+'&userip=MyIP')
                
                request = urllib2.Request(url, None, {'Referer': 'testing'})
                response = urllib2.urlopen(request)
                
                results = simplejson.load(response)
                data = results['responseData']
                dataInfo = data['results']
                
                for i in range(0,len(dataInfo)):
                    ret_results.append( dataInfo[i]['unescapedUrl'] );
                
            return ret_results;
        except Exception,e:
            print e;
            time.sleep(1)
            
results=getImageURL(getSearchString());
print "results=[";
for r in range(0,len(results)-1):
    print '"' + results[r] + '",'
print '"' + results[-1] + '"];'