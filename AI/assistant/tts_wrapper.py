import socket
import threading
import queue
import tts  # Your existing TTS module

HOST = 'localhost'  # IP address
PORT = 65432        # Port to listen on

# Queue to store speech requests
speech_queue = queue.Queue()

# Function to handle TTS requests
def process_queue():
    while True:
        speech_text = speech_queue.get()  # Get the next item from the queue
        tts.speak(speech_text)            # Call your TTS module function (replace with your logic)
        speech_queue.task_done()          # Mark the task as done

# Function to handle connections from clients (other Python scripts)
def handle_client(conn):
    with conn:
        print('Connected by', conn)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            speech_text = data.decode('utf-8')
            speech_queue.put(speech_text)  # Add speech text to the queue
            conn.sendall(b'Request received')

# Start the TTS processing thread
threading.Thread(target=process_queue, daemon=True).start()

# Set up the server socket to listen for connections
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Listening on {HOST}:{PORT}')
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()