count=0;i=0;emoticons=[":ftlhuman:",":ftlmantis:",":melon:",":headcrab:",":RogueMoneybags:",":summerufo:"];
//greetings=["      hi", "haldo", "   hihi", " hello"];
greetings=["hi", "haldo", "hihi", "hello", "haldo frand", "gipper gorp", "blup", "barp", "glorp", "bloop", "beep", "meep", "glup", "floop"];
names=["robit", "robot", "grobocross", "robotron", "grobotron", "megazord", "robofrand", "robotime", "robomake", "mechasoft II", "grobohorn", "bep", "blorp", "blup", "blep", "gorp", "robocop"];
function getSecondaryGreeting(){
    return ", I am " + names[Math.round(Math.random()*(names.length-1))] + ". I got Thursday and Friday off! Sent at ";
}

function getTimeString(){
    var date = (new Date());
    var hours = date.getHours();
    if(Math.random()<0.66){
        if(hours>12){hours-=12;}
    }
    
    var minStr = date.getMinutes().toString();
    if(minStr.length==1){minStr="0"+minStr;}
    var secStr = date.getSeconds().toString();
    if(secStr.length==1){secStr="0"+secStr;}
    
    var timeStr = hours.toString() + ":" + minStr
    
    if( Math.random() < 0.6 ){
        timeStr += ":" + secStr;
        if( Math.random() < 0.4 ){
            timeStr += "." + date.getMilliseconds();
        }
    }
    
    return timeStr;
}
send_hi = function(){
    document.getElementById("chatmessage").value=greetings[Math.round(Math.random()*(greetings.length-1))]+getSecondaryGreeting()+getTimeString()+" "+emoticons[i]/*+" (Message "+(++count)+")"*/;i++;if(i>=emoticons.length){i=0;}document.getElementsByClassName("btn_darkblue_white_innerfade btn_medium")[0].click();
}
done=false;x=setInterval(function(){console.log((new Date()).getSeconds());if((new Date()).getSeconds()==0){if(!done){send_hi();chat_interval=setInterval(send_hi,59900);console.log("chat_interval = "+chat_interval);}clearInterval(x);}},500);