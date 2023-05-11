// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://*/*
// @grant        none
// ==/UserScript==

    _log = "";
    function log(str){
        _log += str + "\n";
    }
(function() {
    setInterval(function(){
    learned_words = {"today":"今日",
                     "1":"一",
                     "2":"二",
                     "3":"三",
                     "4":"四",
                     "5":"五",
                     "6":"六",
                     "7":"七",
                     "8":"八",
                     "9":"九",
                     "yes":"はい",
                     "what":"何",
                     "cute":"可愛い",
                     "funny":"面白い"
                    };
    jQueries = ['.tweet-text',
                '.js-relative-timestamp',
                '.metadata',
                '.js-nav.trend-item-stats',
                '.ProfileCardStats-statValue',
                '.request-favorited-popup',
                '.request-retweeted-popup',
                '.ProfileTweet-actionCountForPresentation'
                ];
    for( var a = 0 ; a < jQueries.length ; a++ ){
        tweets = $(jQueries[a]);
        for( var key in learned_words ){
            for( var i = 0 ; i < tweets.length ; i++ ){
                //log("=========")
                //log(tweets[i])
                //log(key)
                //log(jQuery[a]);
                var re = new RegExp(key,"g");
                str = $(tweets[i]).text();
                $(tweets[i]).text( str.replace(re, learned_words[key]) );
            }
        }}}, 5*1000);
})();