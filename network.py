def toBinary(x):
    return str(bin(x))[2:]

def toBits(s):
    b = [];
    for c in s:
        b.append(int(c))
    return b;
    
def toByte(bits):
    return reduce(lambda n, b: n << 1 | b, bits);

TYPE = type("",(), dict(
        position_x     = (toBits("00000000"),float),
        position_y     = (toBits("00000001"),float),
        position_z     = (toBits("00000010"),float),
        rotation_x     = (toBits("00000011"),float),
        rotation_y     = (toBits("00000100"),float),
        rotation_z     = (toBits("00000101"),float),
        cur_weapon     = (toBits("00000110"),int),
        chat_all       = (toBits("00000111"),str),
        chat_team      = (toBits("00001000"),str),
        new_player     = (toBits("00001001"),str),
        new_object     = (toBits("00001010"),int),
        sound_start    = (toBits("00001011"),int),
        sound_stop     = (toBits("00001100"),int),
        cur_state      = (toBits("00001101"),int),
        equipment_on   = (toBits("00001110"),int),
        equipment_off  = (toBits("00001111"),int),
        team_join      = (toBits("00010000"),int),
        health         = (toBits("00010001"),int),
        name_change    = (toBits("00010010"),str),
        server_message = (toBits("00010011"),str),
        velocity_x     = (toBits("00010100"),float),
        velocity_y     = (toBits("00010101"),float),
        velocity_z     = (toBits("00010110"),float),
        item_get       = (toBits("00010111"),int),
        item_use       = (toBits("00011000"),int),
        item_lose      = (toBits("00011001"),int)
        ))()
    
def getDataType( integerValue ):
    bits = toBits(toBinary(integerValue).zfill(8));
    for d in dir(TYPE)[18:]:
        if eval("TYPE."+d)[0] == bits:
            return eval("TYPE."+d)[1]
    return None;
    
def convertToPacket( id, msg_type, data ):
    packet_bits = [];
    
    packet_bits.extend(toBits(toBinary(id).zfill(8)));
    
    if type(msg_type) == int:
        msg_type = toBits(toBinary(msg_type).zfill(8));
    packet_bits.extend(msg_type);
    
    if type(data) != str:
        data = str(data)
    
    packet_bits.extend(toBits(toBinary(len(data)).zfill(8)));
    
    bits = [];
    for i in range(0,len(data)):
        bits.extend( toBits(toBinary(ord(data[i])).zfill(8)) )
    packet_bits.extend(bits)
    
    packet = bytearray(len(packet_bits)/8);
    packet[0] = toByte(packet_bits[0:8])
    packet[1] = toByte(packet_bits[8:16])
    packet[2] = toByte(packet_bits[16:24])
    for i in range(3,len(packet_bits)/8):
        packet[i] = toByte(packet_bits[i*8:(i+1)*8])
    return packet

def convertFromPacket( packet ):
    result = dict();
    origin_id   = packet[0];
    packet_type = packet[1];
    data_length = packet[2];
    
    if type(origin_id) == str:
        origin_id   = ord(packet[0])
        packet_type = ord(packet[1])
        data_length = ord(packet[2])
    
    data_str = ""
    data_type = getDataType(packet_type)
    
    if data_type != str:
        for i in range(3,len(packet)):
            data_str += chr(int(toBinary(packet[i]).zfill(8),2))
    else:
        data_str = packet[3:len(packet)]
    data = data_type(data_str)
    
    return {"origin_id":origin_id,  "packet_type":packet_type, "data":data}