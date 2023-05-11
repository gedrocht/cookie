Util = {};

Util.alphabet    = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'];
Util.hexadecimal = ['0','1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f'];

Util.intervalFor = function( start, bool, incr, func, delay ){
    var intervalValue = -1;
    start();
    
    var loop = function(){
        if(!bool()){
            clearInterval(intervalValue);
            return;
        }
        func();
        incr();
    }
    
    setTimeout(loop,0);
    intervalValue = setInterval(loop,delay)
}

Util.doSteadyChange = function( start, stop, numFrames, frameDelay, setter ){
    var delta = (stop-start)/numFrames;
    
    for( var i = 0 ; i < numFrames ; i++ )
        setTimeout( function(i){return function(){setter(start + i*delta)}}(i) , frameDelay*i );
}

Util.addIntervalFunc = function( func, condFunc, delay ){
    var intervalValue = setInterval(
        function(){
            func();
            if(condFunc())
                clearInterval(intervalValue)
        }
        ,delay);
    return intervalValue;
}

Util.addInterval = function( func, delay ){
    var intervalValue = setInterval(
        function(){
            if( !func() )
                clearInterval(intervalValue)
        }
    ,delay);
    return intervalValue;
}

Util.randFloat = function(a,b){
    if (b==undefined)
        return Math.random()*a;
    return Math.random()*(b-a)+a;
}

Util.randInt = function(a,b){
    return Math.round(Util.randFloat(a,b));
}

Util.randElem = function( arr ){
    return arr[Math.floor(Math.random()*arr.length)];
}

Util.randLetter = function(){
    return Util.randElem(Util.alphabet);
}

Util.randHex = function(){
    return Util.randElem(Util.hexadecimal);
}

Util.randRGB = function(){
    return Util.toRGBString(Util.randInt(0,255),Util.randInt(0,255),Util.randInt(0,255));
}

Util.randHexColor = function(){
    var result = "#";
    for( var i = 0 ; i < 6 ; i++ )
        result += Util.randHex();
    return result;
}

Util.round = function(decimal, digits){
    var result = decimal * (Math.pow(10,digits));
    return Math.round(result)/(Math.pow(10,digits));
}

Util.toRGBString = function( r, g, b ){
    if ( r instanceof Array )
        return "rgb(" + r[0] + "," + r[1] + "," + r[2] + ")";
    return "rgb(" + r + "," + g + "," + b + ")";
}

Util.toRGBArray = function(s){
    var result = s.substring(s.indexOf("(")+1,s.length-1).split(",");
    for( var i = 0 ; i < result.length ; i++ ){ result[i] = Number(result[i]); }
    return result;
}

Util.setRGBAtIndex = function( rgb, index, value ){
    var array = Util.toRGBArray(rgb);
    array[index] = Math.round(value);
    return Util.toRGBString(array[0], array[1], array[2]);
}

Util.setRGB_R = function( rgb, r ){
    return Util.setRGBAtIndex(rgb,0,r);
}

Util.setRGB_G = function( rgb, g ){
    return Util.setRGBAtIndex(rgb,1,g);
}

Util.setRGB_B = function( rgb, b ){
    return Util.setRGBAtIndex(rgb,2,b);
}

Util.addRGB = function( rgbOne, rgbTwo ){
    var arrayOne = Util.toRGBArray(rgbOne);
    var arrayTwo = Util.toRGBArray(rgbTwo);
    
    var newArray = [arrayOne[0] + arrayTwo[0],
                    arrayOne[1] + arrayTwo[1],
                    arrayOne[2] + arrayTwo[2]];

    if (newArray[0] > 255) newArray[0] = 255;
    if (newArray[1] > 255) newArray[1] = 255;
    if (newArray[2] > 255) newArray[2] = 255;
    
    if (newArray[0] < 0) newArray[0] = 0;
    if (newArray[1] < 0) newArray[1] = 0;
    if (newArray[2] < 0) newArray[2] = 0;
    
    return Util.toRGBString(newArray);
}


go=function(){
var divs = document.getElementsByTagName("div");
for( var i = 0 ; i < divs.length ; i++ ){
    var div = divs[i];
    var color;
    if( div.style.backgroundColor.length == 0 ){
        color = Util.randRGB();
        div.style.backgroundColor = color;
    } else {
        color = div.style.backgroundColor;
    }
    
    for( var z = 0 ; z < 3 ; z++ ){
        Util.doSteadyChange(
            Util.toRGBArray(color)[z],
            Util.randInt(255),
            1000,
            16,
            function(div,z){
                return function(x){
                    div.style.backgroundColor = Util.setRGBAtIndex(div.style.backgroundColor, z, x);
                }
            }(div,z)
        );
    }
}}

go();
setInterval(go,1000*16);