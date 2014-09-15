d=document;
g='getElementById';

bigCookie = d[g]('bigCookie');

intervals = {};

function clickBigCookie(){
    bigCookie.click();
}

addInterval("Click Big Cookie",clickBigCookie,0);

addInterval("Buy Buildings",function(){
    oneOfEach = true
    for(var i=11;i>-1;i--){
        x=d[g]('productOwned'+i);
        if(x==null)continue;
        if(Number(x.innerHTML)==0){
            oneOfEach = false;
            break;
        }
    }

    if( oneOfEach ){
        lowest = 9999;
        lowestNum = 1;
        for( var i = 11 ; i > -1 ; i-- ){
            x=d[g]('productOwned'+i);
            if(x==null)continue;
            if(Number(x.innerHTML)<lowest){
                lowest=Number(x.innerHTML);
                lowestNum=i;
            }
        }
        d[g]('productOwned'+lowestNum).click();
        return;
    } else {
        for(var i=11;i>-1;i--){
            x=d[g]('productOwned'+i);
            if(x==null)continue;
            x.click();
    }

    for(var i=11;i>-1;i--){
        x=d[g]('productName'+i);
        if(x==null)continue;
        if( x.parentNode.parentNode.className == "product unlocked disabled" ){
            break;
        }
        if( x.parentNode.parentNode.className == "product unlocked enabled" ){
            x.click();
            break;
        }
        }},10);
        
addInterval("Buy Upgrades",function(){for(var a=999;a>-1;a--){
        z=d[g]('upgrade'+a);
        if(z!=undefined){
            upgradeNum = Number(z.onclick.toString().split("[")[1].split("]")[0]);
            if(upgradeNum==69  ||
               upgradeNum==85  ||
               upgradeNum==182 ||
               upgradeNum==183 ||
               upgradeNum==184 ||
               upgradeNum==185 ||
               upgradeNum==209 ){
                if( upgradeNum==69 ){
                    z.click();
                    setTimeout(function(){d[g]('promptOption0').click();},100);
                }
                continue;
            }
            z.click();
        }}},50);

addInterval("Click Golden Cookies",function(){c=d[g]('goldenCookie');if(c!=undefined){c.click();}},200);

addInterval("Click Holiday Popups",function(){c2=d[g]('seasonPopup');if(c2!=undefined){c2.click();}},200);

addInterval("Click Wrinklers",function(){
        for(var i = 0 ; i < Game.wrinklers.length ; i++ ){
            var wrinkler = Game.wrinklers[i];
            if( wrinkler.close == 1 ){
                wrinkler.selected = true;
            }}},100);
addInterval("Set Title",function(){d.title=Beautify(Game.cookiesPs,0) + " CpS";},0);

//addInterval("Reset",function(){if(Game.cookiesEarned / 1000000000000000000000>1){Game.Reset(1);}},1000); //reset every 1 sextillion cookies in bank
  addInterval("Reset",function(){if(((Game.time - Game.startDate)/1000)/60 > 60){stopAllIntervals();Game.Reset(1);setTimeout(startAllIntervals,1000);}},1000); //reset every hour

function Interval(name,intervalFunction,intervalDelay){
    this.name = name;
    this.intervalFunction = intervalFunction;
    this.intervalDelay = intervalDelay;
    this.running = false;
    this.number = -1;
    this.start = function(){
        if( this.running ) return;
        this.number = setInterval(this.intervalFunction,this.intervalDelay);
        this.running = true;
    }
    this.stop = function(){
        if( !this.running ) return;
        clearInterval(this.number);
        this.running = false;
    }
}

function addInterval(name,intervalFunction,intervalDelay){
    if( intervals.hasOwnProperty(name) ){
        throw new Error('Cannot create new interval with name "' + name + '": An interval with this name already exists');
    }
    intervals[name] = new Interval(name,intervalFunction,intervalDelay);
}

function startAllIntervals(){
    for( var key in intervals ){
        intervals[key].start();
    }
    printIntervalStatus();
}

function stopAllIntervals(){
    for( var key in intervals ){
        intervals[key].stop();
    }
    printIntervalStatus();
}

function startInterval(name){
    intervals[name].start();
    printIntervalStatus();
}

function stopInterval(name){
    intervals[name].stop();
    printIntervalStatus();
}

function getInterval(name){
    return intervals[name];
}

function printIntervalStatus(){
    var longestNameLength = 0;
    var longestName;
    var interval;
    for( var key in intervals ){
        interval = intervals[key];
        if( interval.name.length > longestNameLength ){
            longestName = interval.name;
            longestNameLength = interval.name.length;
        }
    }
    
    for( var key in intervals ){
        interval = intervals[key];
        console.log( rjust(interval.name,longestNameLength) + " : " + ((interval.running)?"RUNNING":"PAUSED ") );
    }
}

function rjust( str, len ){
    if( str.length >= len ) return str;
    
    while( str.length < len ) str = " " + str;
    
    return str;
}

function ljust( str, len ){
    if( str.length >= len ) return str;
    
    while( str.length < len ) str = str + " ";
    
    return str;
}
startAllIntervals();

/*
INTERVAL_LOL = setInterval(function(){
    var hours=((cookieGoal-Game.cookies) / cookieDiff)/(60.0*60.0);
    var numHours = Math.floor(hours);
    var numMinutes = Math.floor((hours-numHours)*60,0);
    var minStr = numMinutes.toString();
    if(minStr.length==1){minStr="0"+minStr;}
    var timeStr = numHours.toString() + ":" + minStr + " Remaining";
    document.title = timeStr;
    },0);
*/