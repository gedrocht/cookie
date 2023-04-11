import socket
from threading import Thread
from threading import Lock
from time import sleep
from datetime import datetime
from enum import Enum

HOST = "192.168.0.6"  # Standard loopback interface address (localhost)
PORT_PI = 31023  # Port to listen on (non-privileged ports are > 1023)
PORT_WEB = 12889

LOG_SRC = Enum("SRC", ["DATA_BRIDGE",
                       "HTTP",
                       "BUTTON"]) 

LOG_TYPE = Enum("TYPE", ["RECV",
                         "SEND",
                         "INIT",
                         "CONN",
                         "DCON"])

def log(source, type, message):
    output = "[" + datetime.now().strftime("%Y:%m:%d:%H:%M:%S") + "]"
    output += " [" + source.name + "]"
    output += " [" + type.name + "]"
    output += " - " + str(message)
    print(output)

def raspberry_pi_server():
    global web_socket_buffer
    global web_socket_buffer_lock
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT_PI))
        s.listen()
        log(LOG_SRC.BUTTON, LOG_TYPE.INIT, "192.168.0.6:" + str(PORT_PI))
        conn, addr = s.accept()
        with conn:
            log(LOG_SRC.BUTTON, LOG_TYPE.CONN, conn.getpeername()[0] + ":" + str(conn.getpeername()[1]))
            while True:
                data = conn.recv(1024)
                if data == b"Pressed":
                    log(LOG_SRC.BUTTON, LOG_TYPE.RECV, str(data))
                    count_file = open("job_applications.txt", "r")
                    count_text = count_file.readline()
                    count = int(count_text.strip())
                    count += 1
                    count_file.close()
                    count_file = open("job_applications.txt", "w")
                    count_file.write(str(count))
                    count_file.flush()
                    count_file.close()
                    web_socket_buffer_lock.acquire()
                    web_socket_buffer.append(str(count))
                    web_socket_buffer_lock.release()
                elif data == b"Fart" or data == b"mario_oof" or data == b"laugh_track" or data == b"clapping":
                    log(LOG_SRC.BUTTON, LOG_TYPE.RECV, str(data))
                    web_socket_buffer_lock.acquire()
                    web_socket_buffer.append(str(data))
                    web_socket_buffer_lock.release()
                if not data:
                    break
                conn.sendall(data)

def data_bridge_recv(client_connection, client_ip, client_port):
    log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.CONN, str(client_ip) + ":" + str(client_port))
    try:
        while True:
            data = client_connection.recv(1024)
            log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.RECV, str(data))
            if data == b"info_request":
                count_file = open("job_applications.txt", "r")
                count_text = count_file.readline()
                count_file.close()
                log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.SEND, bytes(count_text, "utf-8"))
                client_connection.sendall(bytes(count_text, "utf-8"))
    except:
        log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.DCON, str(client_connection))
    

def data_bridge_server():
    global web_socket_buffer
    global web_socket_buffer_lock
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("192.168.0.6", PORT_WEB))
        s.listen()
        log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.INIT, "192.168.0.6:" + str(PORT_WEB))
        conn, (client_ip, client_port) = s.accept()
        with conn:
            client_thread = Thread(target=data_bridge_recv, kwargs={'client_connection':conn, 'client_ip': client_ip, "client_port": client_port})
            client_thread.daemon = True
            client_thread.start()
            # init_data = conn.recv(1024)
            # log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.RECV, str(init_data))
            while True:
                if len(web_socket_buffer) > 0:
                    web_socket_buffer_lock.acquire()
                    for i in range(0,len(web_socket_buffer)):
                        buffer_data = web_socket_buffer[i]
                        log(LOG_SRC.DATA_BRIDGE, LOG_TYPE.SEND, bytes(buffer_data, "utf-8"))
                        conn.sendall(bytes(buffer_data, "utf-8"))
                    web_socket_buffer = []
                    web_socket_buffer_lock.release()
                sleep(0.01)
            # client_thread.join()

if __name__ == '__main__':
    global web_socket_buffer
    web_socket_buffer = []
    global web_socket_buffer_lock
    web_socket_buffer_lock = Lock()
    pi_thread = Thread(target=raspberry_pi_server)
    web_thread = Thread(target=data_bridge_server)
    pi_thread.daemon = True
    web_thread.daemon = True
    pi_thread.start()
    web_thread.start()
    while True:
        sleep(1)