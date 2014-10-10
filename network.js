Network = {};

Network.TYPE = {
    position_x     :[0,Number],
    position_y     :[1,Number],
    position_z     :[2,Number],
    rotation_x     :[3,Number],
    rotation_y     :[4,Number],
    rotation_z     :[5,Number],
    cur_weapon     :[6,Number],
    chat_all       :[7,String],
    chat_team      :[8,String],
    new_player     :[9,String],
    new_object     :[10,Number],
    sound_start    :[11,Number],
    sound_stop     :[12,Number],
    cur_state      :[13,Number],
    equipment_on   :[14,Number],
    equipment_off  :[15,Number],
    team_join      :[16,Number],
    health         :[17,Number],
    name_change    :[18,String],
    server_message :[19,String],
    velocity_x     :[20,Number],
    velocity_y     :[21,Number],
    velocity_z     :[22,Number],
    item_get       :[23,Number],
    item_use       :[24,Number],
    item_lose      :[25,Number]
};

Network.decode = function(data){
    var origin_id   = data.charCodeAt(0);
    var packet_type = data.charCodeAt(1);
    var data_length = data.charCodeAt(2);
    var packet_data = "";
    for( var i = 3 ; i < data.length ; i++ )
        packet_data += data[i];
    
    return {"origin_id":origin_id, "packet_type":packet_type, "data_length":data_length, "data":packet_data};
}

Network.encode = function( id, type, data ){
    if( data.length == 0 )
        return "";
    
    var packet = [id,type,data];
    
    return packet;
}

Network.pad = function( s, digits ){
    while(s.length < digits)
        s="0"+s
    return s;
}  

Network.connected = false;
Network.server;

window.onload = function() {
    Network.server = new WebSocket("ws://"+Config.WebSocketServerAddress);
    Network.server.onopen = function(e) { Network.connected = true; }
    Network.server.onclose = function(e) { Network.connected = false; }
    Network.server.onmessage = function(e) { Network.handleReceivedPacket(Network.decode(e.data)); }
};
Network.handleReceivedPacket = function(){}