import socket
import sys
import threading

from network import *

tcp_HOST, tcp_PORT = "localhost", 9999
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
    print(printBuffer[:-1]);
    printBuffer = "";
    
    printLock -= 1;

def tcp_connect():
    try:
        tcp_sock.connect((tcp_HOST, tcp_PORT));
        _print("CONNECTED TO TCP SERVER " + str(tcp_HOST) + ":" + str(tcp_PORT));
    finally:
        pass;
    
def tcp_send():
    _print("STARTING TCP SENDING THREAD");
    try:
        while True:
            data = convertToPacket(0,TYPE.chat_all[0],raw_input(''));
            tcp_sock.sendall(data);
    except Exception,e:
        _print("Send Error: " + str(e))
        
def tcp_receive():
    _print("STARTING TCP RECIEVING THREAD");
    try:
        while True:
            received = tcp_sock.recv(1024);
            if len(received) == 0: continue;
            data = convertFromPacket(received);
            
            if data["packet_type"] == toByte(TYPE.chat_all[0]):
                _print( str(data["origin_id"]) + ": " + str(data["data"]) );
    except Exception,e:
        _print("Receive Error: " + str(e))

tcp_connect();

sendingThread = threading.Thread(target=tcp_send);
sendingThread.daemon = True;
sendingThread.start();

receivingThread = threading.Thread(target=tcp_receive);
receivingThread.daemon = True;
receivingThread.start();

while True:
    pass