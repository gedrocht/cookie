appids = [ 
["205100",	"Dishonored"],
]

store_url = "http://store.steampowered.com/app/"

for i in range(0,len(appids)):
    print '<a href="' + store_url + appids[i][0] + '">' + appids[i][1] + '</a><br>'