import Queue
import threading
import urllib2
import socket
import time
import re
from base64 import b64encode
from hashlib import sha1

from network import *

CONNECTION_TCP = 0;
CONNECTION_WS  = 1;
CONNECTION_UDP = 2;

connections = [];
connectionLock = 0;

def addConnection( connection, connection_type ):
    global connections
    global connectionLock

    while connectionLock:
        pass;
        
    connectionLock += 1;
    
    connections.append( (connection, connection_type) );
    
    connectionLock -= 1;
    
    return len(connections)
    

def removeConnection( connection, connection_type ):
    global connections
    global connectionLock
    
    while connectionLock:
        pass;
    connectionLock += 1;
    newConnections = [];
    
    for c in connections:
        if c[0] == connection and c[1] == connection_type:
            continue;
        newConnections.append(c);
    
    connections = newConnections;
    
    connectionLock -= 1;
    
    
def getConnection( connection, connection_type ):
    global connections
    global connectionLock
    
    while connectionLock:
        pass;
    connectionLock += 1;
    
    for c in connections:
        if c[0] == connection and c[1] == connection_type:
            connectionLock -= 1;
            return c
    connectionLock -= 1;


printBuffer = ""
printLock = 0;
def _print(s):
    global printBuffer;
    global printLock;
    while printLock:
        pass;
    printLock += 1;
    
    if type(s) is not type(str()):
        s = str(s);
    
    printBuffer += s + "\n";
    print printBuffer[:-1];
    printBuffer = "";
    
    printLock -= 1;

    
def xor( a, b ):
    s = ""
    i = 0;
    offset = 0;
    greatestLength = len(a);
    a_is_longer = True;
    if len(b) > greatestLength:
        a_is_longer = False;
        greatestLength = len(b);
    
    for z in range(0,greatestLength):
        if a_is_longer:
            if z+offset >= len(b):
                offset -= len(b);
            if a[z] == b[z+offset]:
                s += "0";
            else:
                s += "1";
        else:
            if z+offset >= len(a):
                offset -= len(a);
            if a[z+offset] == b[z]:
                s += "0";
            else:
                s += "1";
    
    return bytearray(s)
    
websocket_answer = (
    'HTTP/1.1 101 Switching Protocols',
    'Upgrade: websocket',
    'Connection: Upgrade',
    'Sec-WebSocket-Accept: {key}\r\n\r\n',
)
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

def ws_startServer():
    t = threading.Thread(target=ws_acceptConnections);
    t.daemon = True;
    t.start();

def ws_acceptConnections():
    ip = "127.0.0.1";
    port = 8999;
    
    _print( "Starting WebSocket server at " + str(ip) + ":" + str(port) )
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s.bind((ip,port));
    s.listen(2);
    
    _print( "WebSocket Server Online" )
    
    while True:
        conn, addr = s.accept();
        t = threading.Thread(target=ws_handleConnection, args=(conn,addr));
        t.daemon = True;
        t.start();
        
def ws_handleConnection( connection, address ):
    cs = str(address[0]) + ":" + str(address[1])
    _print( cs + " connected" )
    
    id = addConnection( connection, CONNECTION_WS );
    _print( cs + " ID: " + str(id) )
    
    text = connection.recv(1024)
    
    key = (re.search('Sec-WebSocket-Key:\s+(.*?)[\n\r]+', text)
    .groups()[0]
    .strip())
    
    response_key = b64encode(sha1(key + GUID).digest())
    response = '\r\n'.join(websocket_answer).format(key=response_key)
    
    connection.send(response)
    
    try:
        while True:
            data = connection.recv(1024)
            if len(data) == 0: continue;
            
            wsPacketPayload = decodeWsPacket(data);
            
            decodedPayload = wsPacketPayload.split(",");
            
            packet_origin_id = int(decodedPayload[0]);
            packet_type = int(decodedPayload[1]);
            packet_data = decodedPayload[2];
            
            #_print( cs + ": " + "{'data': " + str(packet_data) + ", 'packet_type': " + str(packet_type) + ", 'origin_id': " + str(id) + "}" );
            
            new_packet_id = packet_origin_id;
            if( packet_type == toByte(TYPE.chat_all[0]) ):
                new_packet_id = id;
            
            newPacket = convertToPacket( new_packet_id, packet_type, packet_data );
            sendToAllOthers( connection, CONNECTION_WS, newPacket )
            
    except Exception:
        pass;
    finally:
        removeConnection( connection, CONNECTION_WS );
        _print( cs + " disconnected" );
        connection.close();
        
def decodeWsPacket( data ):
    bytes = bytearray(data);
    output = ""
    for i in range(0,len(bytes)):
        output += str(bin(bytes[i]))[2:].rjust(8,"0") + " ";
    payloadLength = output.replace(" ","")[9:16]
    mask = bytearray(output.replace(" ","")[16:48])
    payload = bytearray(output.replace(" ","")[48:])
    result = xor(mask,payload);
    
    resultString = "";
    for i in range(0,int(payloadLength,2)):
        resultString += chr(int(str(result)[i*8:(i+1)*8],2))
    return resultString;

def sendToAllOthers( connection, connection_type, message ):
    global connections
    global connectionLock
    while connectionLock:
        pass;
    connectionLock += 1;
    
    for conn in connections:
        if conn[0] == connection and conn[1] == connection_type:
            continue;
        sendTo(conn[0], conn[1], message);
    
    connectionLock -= 1;
    
    
def sendTo( connection, connection_type, data ):
    if connection_type == CONNECTION_TCP:
        sendToTCP( connection, data );
    elif connection_type == CONNECTION_WS:
        sendToWs( connection, data );
    
def sendToWs( connection, data ):
    _fin =      "1"
    _reserved = "000"
    _opcode = "0001"
    _mask = "0"
    
    _payload = str(data);
    _payload_len = str(bin(len(_payload)))[2:].zfill(7);
    
    bytes = bytearray(0);
    bytes.append(toByte(toBits( _fin + _reserved + _opcode )));
    bytes.append(toByte(toBits( _mask + _payload_len )));
    for character in _payload:
        bytes.append(toByte(toBits(str(bin(ord(character)))[2:].zfill(8))))
    connection.sendall(bytes);
    
def sendToTCP( connection, data ):
    connection.send(data);

def udp_startServer():
    t = threading.Thread(target=udp_acceptConnections);
    t.daemon = True;
    t.start();
    
def udp_acceptConnections():
    ip = "127.0.0.1";
    port = 7999;
    
    _print( "Starting UDP server at " + str(ip) + ":" + str(port) );
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    s.bind((ip,port));
    
    _print( "UDP Server Online (inoperable)" );
    
def tcp_startServer():
    t = threading.Thread(target=tcp_acceptConnections);
    t.daemon = True;
    t.start();

def tcp_acceptConnections():
    ip = "127.0.0.1";
    port = 9999;
    
    _print( "Starting TCP server at " + str(ip) + ":" + str(port) );
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s.bind((ip,port));
    s.listen(2);
    
    _print( "TCP Server Online" );
    
    while True:
        conn,addr = s.accept();
        t = threading.Thread(target=tcp_handleConnection, args=(conn,addr));
        t.daemon = True;
        t.start();
    
def tcp_handleConnection( connection, address ):
    cs = str(address[0]) + ":" + str(address[1])
    _print( cs + " connected" );
    id = addConnection( connection, CONNECTION_TCP );
    _print( cs + " ID: " + str(id) );
    try:
        while True:
            data = connection.recv(1024);
            if len(data) == 0: continue;
            
            try:
                decodedPacket = convertFromPacket( bytearray(data) );
            except Exception,e:
                _print(e)
            
            decodedPayload = decodedPacket["data"];
            
            decodedPacket["origin_id"] = id;
            _print( cs + ": " + str(decodedPacket) )
            
            if( decodedPacket["packet_type"] == toByte(TYPE.chat_all[0]) ):
                newPacket = convertToPacket( id, TYPE.chat_all[0], decodedPayload );
                sendToAllOthers( connection, CONNECTION_TCP, newPacket );
            
    except Exception,e:
        _print("TCP Connection Error: " + str(e));
    finally:
        removeConnection( connection, CONNECTION_TCP );
        _print( cs + " disconnected" );
        connection.close();
    
def doInterval( func, params, interval ):
    while True:
        if params is not None:
            func(params);
        else:
            func();
        time.sleep(interval/1000.0);
    
def setInterval( func, params, interval ):
    z = threading.Thread(target=doInterval, args=(func,params,interval));
    z.daemon = True;
    z.start();

def say(s): _print( s );

tcp_startServer();
udp_startServer();
ws_startServer()

'''
def printAllConnections():
    global connections;
    global connectionLock;
    while connectionLock:
        pass;
    connectionLock += 1;
    _print("---------------");
    _print("CONNECTIONS: ");
    if len(connections) == 0:
        _print("NONE")
    for conn in connections:
        _print(conn)
    connectionLock -= 1;
setInterval( printAllConnections, None, 1000 );
'''

while True: time.sleep(1000);