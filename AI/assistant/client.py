import socket
import json
import logging
import os
import signal
import sys

def load_client_config(config_file='client_config.json'):
    with open(config_file, 'r') as file:
        return json.load(file)

def setup_client_logging(config):
    log_directory = config['logging']['directory']
    log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
    
    os.makedirs(log_directory, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_directory, 'client.log')),
            logging.StreamHandler()
        ]
    )

def handle_sigint(signum, frame):
    """Gracefully handle Ctrl+C for the client."""
    logging.info("Shutting down the client...")
    sys.exit(0)

def send_command(command, config):
    host = config['server']['host']
    port = config['server']['port']

    try:
        # Register signal handler for graceful shutdown
        signal.signal(signal.SIGINT, handle_sigint)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            logging.info(f"Sending command: {command}")
            s.sendall(command.encode('utf-8'))
            
            data = s.recv(1024)
            logging.info(f"Received response: {data.decode('utf-8')}")

    except socket.error as e:
        logging.error(f"Socket error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    client_config = load_client_config('client_config.json')
    setup_client_logging(client_config)  # Initialize logging
    while True:
        send_command(input("> "), client_config)
#    send_command("tts speak 'Hello, world!'", client_config)
#    send_command("tts set_rate 120", client_config)
#    send_command("tts get_rate", client_config)
