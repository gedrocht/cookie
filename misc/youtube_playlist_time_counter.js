function pad(str, len){
	str = str.toString();
	while(str.length<len){
		str = "0"+str;
	}
	return str;
};

var timestamps = document.getElementsByClassName('timestamp');
/*
var wait_interval = setInterval( 
	function(){
		if( document.readyState == "complete" ){
			clearInterval(wait_interval);
*/
			var total = 0;
			var timestamp;
console.log(timestamps.length);
			for( var i = 0 ; i < timestamps.length ; i++ ){
				timestamp = timestamps[i];
				var time = timestamp.children[0].innerHTML.split(":");
				
				for( var i = 0 ; i < time.length ; i++ ){
					time[i] = Number(time[i]);
				}
				
				switch( time.length ){
					case 3:
						total += time[0]*60*60;
						total += time[1]*60;
						total += time[2];
						break;
					case 2:
						total += time[0]*60;
						total += time[1];
						break;
					default:
						console.warn( "Warning: Time format ["+time+"] not recognized." );
						break;
				}
			};
			
			var hours = total/(60*60);
			var minutes = (hours-Math.floor(hours))*60;
			var seconds = (minutes-Math.floor(minutes))*60;
			hours = Math.floor(hours);
			minutes = Math.floor(minutes);
			seconds = Math.round(seconds);
			
			document.getElementsByClassName('pl-header-details')[0].lastChild.innerHTML = hours + ":" + pad(minutes,2) + ":" + pad(seconds,2);/*
		}
	}
,100);*/
