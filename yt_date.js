function convDate( text ){
    var text_split = text.split(" ");
    var text_month = text_split[2];
    var text_day = text_split[3].split(",")[0];
    var text_year = text_split[4];
    
    var num_month = monthToNum(text_month);
    var num_day = Number(text_day);
    var num_year = Number(text_year);
    
    var date = new Date();
    var today_year = date.getUTCFullYear();
    var today_month = date.getMonth()+1;
    var today_day  = date.getDate();
    
    var difference = daysToDate(getTotalDays(today_month,today_day,today_year)-getTotalDays(num_month,num_day,num_year));
    var diff_months = difference[0];
    var diff_days = difference[1];
    var diff_years = difference[2];
    
    var s = "";
    
    if( diff_years != 0 ){
        s += diff_years + " years";
    }
    
    if( diff_months != 0 ){
        if( s.length != 0 )
            s += ", ";
        s += diff_months + " months";
    }
    
    if( diff_months == 0 && diff_days != 0 ){
        if( s.length != 0 )
            s += ", ";
        s += diff_days + " days";
    }
    
    if( s.length != 0 )
        s += " ago"
    
    if( s.length == 0 )
        s = "Today";
        
    if( diff_months == 0 && diff_days == 1 && diff_years == 0 )
        s = "Yesterday";
    
    return "Posted " + s;
}

function getMonthDays( month ){
    if( month == 9 ||
        month == 4 || 
        month == 6 || 
        month == 11 )
        return 30;
    if( month == 2 )
        return 28;
    return 31;
}

function getTotalDays( month, day, year ){
    var total = day;
    
    for( var i = 1 ; i <= month ; i++ ){
        total += getMonthDays(i);
    }
    
    total += year * 365;
    
    return total;
}

function daysToDate( d ){
    var years  = d/365;
    var months = (years-Math.floor(years))*12;
    var days = (months-Math.floor(months))*getMonthDays(Math.floor(months));
    
    return [Math.floor(months), Math.floor(days)+1, Math.floor(years)];
}

function monthToNum( month ){
    switch( month ){
        case 'Jan': return 1;
        case 'Feb': return 2;
        case 'Mar': return 3;
        case 'Apr': return 4;
        case 'May': return 5;
        case 'Jun': return 6;
        case 'Jul': return 7;
        case 'Aug': return 8;
        case 'Sept':
        case 'Sep': return 9;
        case 'Oct': return 10;
        case 'Nov': return 11;
        case 'Dec': return 12;
    }
    return 0;
}

document.getElementsByClassName("watch-time-text")[0].innerText = convDate(document.getElementsByClassName("watch-time-text")[0].innerText);