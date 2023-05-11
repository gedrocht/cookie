function gradually_b( str ){
    var output = "";
    for( var i = 0 ; i < str.length ; i++ ){
        if( str[i] != " " && Math.random() < i/str.length ){
            output += "🅱"
        } else {
            output += str[i];
        }
    }
    return output;
}