# Copied from Raspberry Pi with physical buttons attached to breadboard

import socket
import os

if os.name == "posix":
    from gpiozero import Button
    from gpiozero import LED
    from signal import pause

from datetime import datetime
from enum import Enum
from time import sleep

HOST = "192.168.0.6"  # The server's hostname or IP address
PORT = 31023  # The port used by the server

LOG_SRC = Enum("SRC", ["DATA_BRIDGE",
                       "HTTP",
                       "BUTTON"])

LOG_TYPE = Enum("TYPE", ["RECV",
                         "SEND",
                         "INIT",
                         "CONN",
                         "DCON"])

if __name__ == "__main__":
  global last_job_button_press
  last_job_button_press = datetime.now()

def log(source, type, message):
    output = "[" + datetime.now().strftime("%Y:%m:%d:%H:%M:%S") + "]"
    output += " [" + source.name + "]"
    output += " [" + type.name + "]"
    output += " - " + str(message)
    print(output)

def connect_to_button_server():
  global button_socket
  button_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  button_socket.connect((HOST, PORT))
  log(LOG_SRC.BUTTON, LOG_TYPE.CONN, str(PORT))

def send_to_button_server(msg):
  global button_socket
  try:
    button_socket.sendall(msg)
  except ConnectionResetError:
    log(LOG_SRC.BUTTON, LOG_TYPE.DCON, "Connection reset.")
    sleep(5)
    log(LOG_SRC.BUTTON, LOG_TYPE.DCON, "Reconnecting...")
    connect_to_button_server()

def button_was_pressed():
  global last_job_button_press
  if (datetime.now() - last_job_button_press).total_seconds() < 1.5:
    log(LOG_SRC.BUTTON, LOG_TYPE.SEND, "Job button pressed too frequently")
    return
  last_job_button_press = datetime.now()
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"Pressed")
  send_to_button_server(b"Pressed")

def fart_button_pressed():
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"Fart")
  send_to_button_server(b"Fart")

def mario_oof_button_pressed():
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"mario_oof")
  send_to_button_server(b"mario_oof")

def laugh_track_button_pressed():
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"laugh_track")
  send_to_button_server(b"laugh_track")

def clapping_button_pressed():
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"clapping")
  send_to_button_server(b"clapping")

def toggle_button_pressed():
  led_toggle_on = not led_toggle_on
  log(LOG_SRC.BUTTON, LOG_TYPE.SEND, b"toggle")
  send_to_button_server(b"toggle")

if os.name == "posix":
    button = Button(2)
    fart_button = Button(3)
    mario_oof_button = Button(26)
    laugh_track_button = Button(16)
    clapping_button = Button(17)
    toggle_button = Button(20)

    button.when_pressed = button_was_pressed
    fart_button.when_pressed = fart_button_pressed
    mario_oof_button.when_pressed = mario_oof_button_pressed
    laugh_track_button.when_pressed = laugh_track_button_pressed
    clapping_button.when_pressed = clapping_button_pressed

connect_to_button_server()

if os.name == "posix":
    pause()
else:
   while True:
      print("Enter command: (J)ob, (Q)uit")
      command = input().lower()
      if command == "j":
         button_was_pressed()
      elif command == "q":
         break
      else:
         print("Unrecognized command.")