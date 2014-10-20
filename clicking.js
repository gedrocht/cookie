ClickingCooker = {};

ClickingCooker.d=document;
ClickingCooker.g='getElementById';

ClickingCooker.bigCookie = ClickingCooker.d[ClickingCooker.g]('bigCookie');

ClickingCooker.intervals = {};
ClickingCooker.resetTimeLimit = 12*60;//120

ClickingCooker.Interval = function(name,intervalFunction,intervalDelay){
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

ClickingCooker.addInterval = function(name,intervalFunction,intervalDelay){
    if( ClickingCooker.intervals.hasOwnProperty(name) ){
        throw new Error('Cannot create new interval with name "' + name + '": An interval with this name already exists');
    }
    ClickingCooker.intervals[name] = new ClickingCooker.Interval(name,intervalFunction,intervalDelay);
}

ClickingCooker.clickBigCookie = function(){
    ClickingCooker.bigCookie.click();
}

ClickingCooker.addInterval("Click Big Cookie",ClickingCooker.clickBigCookie,0);

ClickingCooker.addInterval("Buy Buildings",function(){
    var oneOfEach = true;
    var x;
    for(var i=11;i>-1;i--){
        x=ClickingCooker.d[ClickingCooker.g]('productOwned'+i);
        if(x==null)continue;
        if(Number(x.innerHTML)==0){
            oneOfEach = false;
            break;
        }
    }

    if( oneOfEach ){
        var lowest = 9999;
        var lowestNum = 1;
        for( var i = 11 ; i > -1 ; i-- ){
            x=ClickingCooker.d[ClickingCooker.g]('productOwned'+i);
            if(x==null)continue;
            if(Number(x.innerHTML)<lowest){
                lowest=Number(x.innerHTML);
                lowestNum=i;
            }
        }
        ClickingCooker.d[ClickingCooker.g]('productOwned'+lowestNum).click();
        return;
    } else {
        for(var i=11;i>-1;i--){
            x=ClickingCooker.d[ClickingCooker.g]('productOwned'+i);
            if(x==null)continue;
            x.click();
        }
    }

    for(var i=11;i>-1;i--){
        x=ClickingCooker.d[ClickingCooker.g]('productName'+i);
        if(x==null)continue;
        if( x.parentNode.parentNode.className == "product unlocked disabled" ){
            break;
        }
        if( x.parentNode.parentNode.className == "product unlocked enabled" ){
            x.click();
            break;
        }
        }},10);
        
ClickingCooker.addInterval("Buy Upgrades",function(){for(var a=999;a>-1;a--){
        var z=ClickingCooker.d[ClickingCooker.g]('upgrade'+a);
        if(z!=undefined){
            var upgradeNum = Number(z.onclick.toString().split("[")[1].split("]")[0]);
            if(upgradeNum==69  ||
               upgradeNum==85  ||
               upgradeNum==182 ||
               upgradeNum==183 ||
               upgradeNum==184 ||
               upgradeNum==185 ||
               upgradeNum==209 ){
                if( upgradeNum==69 ){
                    z.click();
                    setTimeout(function(){ClickingCooker.d[ClickingCooker.g]('promptOption0').click();},100);
                }
                continue;
            }
            z.click();
        }}},50);

ClickingCooker.addInterval("Click Golden Cookies",function(){var c=ClickingCooker.d[ClickingCooker.g]('goldenCookie');if(c!=undefined){c.click();}},200);

ClickingCooker.addInterval("Click Holiday Popups",function(){var c2=ClickingCooker.d[ClickingCooker.g]('seasonPopup');if(c2!=undefined){c2.click();}},200);

ClickingCooker.addInterval("Click Wrinklers",function(){
        for(var i = 0 ; i < Game.wrinklers.length ; i++ ){
            var wrinkler = Game.wrinklers[i];
            if( wrinkler.close == 1 ){
                wrinkler.selected = true;
            }}},100);

//addInterval("Reset",function(){if(Game.cookiesEarned / 1000000000000000000000>1){Game.Reset(1);}},1000); //reset every 1 sextillion cookies in bank
ClickingCooker.addInterval("Reset",function(){if(((Game.time - Game.startDate)/1000)/60 > ClickingCooker.resetTimeLimit){ClickingCooker.stopAllIntervals();Game.Reset(1);setTimeout(function(){ClickingCooker.startAllIntervals()},1000);}},1000); //reset every 2 hours
 
ClickingCooker.startAllIntervals = function(){
    for( var key in ClickingCooker.intervals ){
        ClickingCooker.intervals[key].start();
    }
    ClickingCooker.printIntervalStatus();
}

ClickingCooker.stopAllIntervals = function(){
    for( var key in ClickingCooker.intervals ){
        ClickingCooker.intervals[key].stop();
    }
    ClickingCooker.printIntervalStatus();
}

ClickingCooker.startInterval = function(name){
    ClickingCooker.intervals[name].start();
    ClickingCooker.printIntervalStatus();
}

ClickingCooker.stopInterval = function(name){
    ClickingCooker.intervals[name].stop();
    ClickingCooker.printIntervalStatus();
}

ClickingCooker.getInterval = function(name){
    return ClickingCooker.intervals[name];
}

ClickingCooker.printIntervalStatus = function(){
    var longestNameLength = 0;
    var longestName;
    var interval;
    for( var key in ClickingCooker.intervals ){
        interval = ClickingCooker.intervals[key];
        if( interval.name.length > longestNameLength ){
            longestName = interval.name;
            longestNameLength = interval.name.length;
        }
    }
    
    for( var key in ClickingCooker.intervals ){
        interval = ClickingCooker.intervals[key];
        console.log( ClickingCooker.rjust(interval.name,longestNameLength) + " : " + ((interval.running)?"RUNNING":"PAUSED ") );
    }
}

ClickingCooker.rjust = function( str, len ){
    if( str.length >= len ) return str;
    
    while( str.length < len ) str = " " + str;
    
    return str;
}

ClickingCooker.ljust = function( str, len ){
    if( str.length >= len ) return str;
    
    while( str.length < len ) str = str + " ";
    
    return str;
}

//4 debug lul
Beans = {};
Beans.timeLeft = function(){
    Beans.Total = (ClickingCooker.resetTimeLimit-((Game.time - Game.startDate)/1000)/60)/60;
    Beans.Hours = Math.floor(Beans.Total);
    Beans.Minutes = (Beans.Total-Math.floor(Beans.Total))*60;
    Beans.Seconds = (Beans.Minutes-Math.floor(Beans.Minutes))*60;
    Beans.Minutes = Math.floor(Beans.Minutes);
    Beans.Seconds = Math.round(Beans.Seconds);
    
    Beans.MinutesString=Beans.Minutes.toString().length==1?"0"+Beans.Minutes:Beans.Minutes.toString();
    Beans.SecondsString=Beans.Seconds.toString().length==1?"0"+Beans.Seconds:Beans.Seconds.toString();
    console.log( ((Beans.Hours>0)?(Beans.Hours+":"):("")) + Beans.MinutesString + ":" + Beans.SecondsString + " until next reset" );
}
Beans.heavenlyChips = function(){return Game.HowMuchPrestige(Game.cookiesReset)/1000000;};

ClickingCooker.startAllIntervals();
//ClickingCooker.addInterval("Set Title",function(){ClickingCooker.d.title=Beautify(Game.cookiesPs,0) + " CpS";},0);
Beans.timeLeft();

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