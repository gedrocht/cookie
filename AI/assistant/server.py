import socket
import threading
import json
import logging
import os
import signal
import sys
import threading
from tts_adapter import TTSAdapter

# Load configuration from a JSON file
def load_config(config_file='server_config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)

# Set up logging with both console and file output
def setup_logging(config):
    log_directory = config['logging']['directory']
    log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
    
    os.makedirs(log_directory, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_directory, 'server.log')),
            logging.StreamHandler()
        ]
    )

# Initialize the TTS Adapter
tts_adapter = TTSAdapter()

def process_client_request(data, config):
    """
    Process the incoming request based on the loaded config.
    Now includes TTS command handling via TTSAdapter.
    """
    try:
        command_parts = data.strip().split()
        module_name = command_parts[0]
        function_name = command_parts[1] if len(command_parts) > 1 else None
        params = command_parts[2:] if len(command_parts) > 2 else []

        if module_name == 'tts':
            logging.info(f"Processing TTS request")
            # Delegate the request to the TTSAdapter
            return tts_adapter.handle_tts_command(function_name, params)

        elif module_name in config['commands']:
            module_config = config['commands'][module_name]
            if function_name in module_config['functions']:
                # Add more modules here as needed
                return f"Executing {module_name}.{function_name} with params: {params}"

        return f"Unknown module or function: {module_name}.{function_name}"

    except Exception as e:
        logging.error(f"Error processing client request: {e}")
        return "Error processing request."

def handle_client(conn, addr, config):
    """
    Handles communication with a client in a separate thread.
    Receives data, processes it, and sends back the response.
    """
    logging.info(f"Connected to client: {addr}")
    try:
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    logging.info(f"Client {addr} disconnected")
                    break

                # Process client request and get response
                response = process_client_request(data.decode('utf-8'), config)
                logging.info(f"{response}")
                conn.sendall(response.encode('utf-8'))

    except Exception as e:
        logging.error(f"Unexpected error with client {addr}: {e}")
    finally:
        conn.close()

def handle_sigint(signum, frame):
    """Gracefully handle Ctrl+C for the server."""
    logging.info("Shutting down the server...")
    sys.exit(0)

def start_server(config):
    """
    Starts the server, accepts client connections, and spawns a new thread for each client.
    Uses a non-blocking accept() loop with a timeout.
    """
    try:
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, handle_sigint)

        host = config['server']['host']
        port = config['server']['port']

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((host, port))
            server_socket.listen(5)  # Allow multiple simultaneous clients
            server_socket.settimeout(1.0)  # Set a 1 second timeout on accept()

            logging.info(f"Server started on {host}:{port}, waiting for clients...")

            while True:
                try:
                    conn, addr = server_socket.accept()  # Try to accept connections
                    # Start a new thread to handle each client connection
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr, config), daemon=True)
                    client_thread.start()

                except socket.timeout:
                    # Timeout allows us to handle signals like Ctrl+C without being blocked by accept()
                    continue

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Unexpected server error: {e}")

if __name__ == '__main__':
    config = load_config('server_config.json')
    setup_logging(config)  # Initialize logging
    start_server(config)
