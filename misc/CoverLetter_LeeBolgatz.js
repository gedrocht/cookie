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

function getTotalDays(month, day, year){
    var total = day;
    for( var i = 1 ; i < month ; i++ ){
        total += getMonthDays(i);
    }
    total += year * 365;
    return total;
}

function daysToDate(days){
    var years = days/365;
    var months = (years-Math.round(years))*12;
    //30.43 days per month (avg)
    var days = (months-Math.round(months))*30.43;
    
    
    years = Math.round(years);
    months = Math.round(months);
    days = Math.round(days);
    
    
    return [months,days,years];
}

function convDate(d){
        split = d.split(" ");
        mon = Number(split[0]);
        day = Number(split[1].split(',')[0]);
        year = Number(split[2]);
        
        month = 1;
        switch(mon){
            case 'Jan': month = 1; break;
            case 'Feb': month = 2; break;
            case 'Mar': month = 3; break;
            case 'Apr': month = 4; break;
            case 'May': month = 5; break;
            case 'Jun': month = 6; break;
            case 'Jul': month = 7; break;
            case 'Aug': month = 8; break;
            case 'Sept': month = 9; break;
            case 'Oct': month = 10; break;
            case 'Nov': month = 11; break;
            case 'Dec': month = 12; break;
        }
        var date = new Date();
        today_year = date.getUTCFullYear();
        today_month = date.getMonth()+1;
        today_day  = date.getDate();
        
        today_totalDays = getTotalDays(today_month, today_day, today_year);
        
        other_totalDays = getTotalDays(month, day, year);
        
        var date_different = daysToDate(today_totalDays - other_totalDays);
        
        var s = "";
        
        var diff_years = date_different[2];
        s += diff_years;
        if( diff_years == 1 )
            s += " year";
        else
            s += " years";
        
        var diff_months = date_different[0];
        s += diff_months;
        if( diff_months == 1 )
            s += " month";
        else
            s += " months";
        
        return "Published " + s + " ago";
}
document.getElementsByClassName("watch-time-text")[0].innerText = convDate(document.getElementsByClassName("watch-time-text")[0].innerText.substr(13))