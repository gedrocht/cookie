import paramiko
import subprocess
import re
from collections import namedtuple
import os
from time import sleep
import time
import sys
import curses

def get_bar(percentage, width):
  output = ""
  for i in range(0, width):
    progress = float(i) / float(width)
    if progress < percentage:
      output += "█"
    else:
       output += "░"
  return output

def connect(hostname, username, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    # Automatically add untrusted hosts (do not use in production!)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to the remote host
        ssh.connect(hostname, username=username, password=password)
        return ssh, None
    except Exception as e:
        return None, str(e)

def run_command(ssh, command):
    try:
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        # Read the output
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        # Return the output and error (if any)
        return output, error
    except Exception as e:
        return None, str(e)

def do_iostat(host_info):
  if host_info["connection"]:
    host_info["prev_iostat"] = host_info["curr_iostat"]

    raw_output, error = run_command(host_info["connection"], \
      '''
        iostat -o JSON -s | \
        grep -v udev | \
        grep -v cgroup | \
        grep -v tmpfs | \
        grep -v snap | \
        grep -v boot | \
        grep -v Steam | \
        grep -v loop | \
          jq '.sysstat.hosts[0].statistics[0].disk[] | ."disk_device", ."kB_read", ."kB_wrtn"'
      '''
    )
    if error:
       print(f"{error}")
       return None
    host_info["prev_iostat_check"] = host_info["curr_iostat_check"]
    host_info["curr_iostat_check"] = time.time()

    DiskStat = namedtuple('DiskStat', ['disk_device', 'kB_read', 'kB_wrtn'])

    lines = raw_output.splitlines()

    # Create an empty list to store the named tuples
    host_info["curr_iostat"] = []

    output = []
    # Loop through the lines and group them into tuples
    for i in range(0, len(lines), 3):
      disk_device = lines[i].strip('"')  # Remove quotes from the disk device name
      kB_read = float(lines[i+1])  # Convert read value to float
      kB_wrtn = float(lines[i+2])  # Convert write value to float
      # Append the named tuple to the list
      host_info["curr_iostat"].append(DiskStat(disk_device, kB_read, kB_wrtn))
    if not host_info["prev_iostat"] is None:
       for drive_i in range(0,len(host_info["curr_iostat"])):
          prev_drive_stats = host_info["prev_iostat"][drive_i]
          curr_drive_stats = host_info["curr_iostat"][drive_i]
          read_difference = curr_drive_stats.kB_read - prev_drive_stats.kB_read
          write_difference = curr_drive_stats.kB_wrtn - prev_drive_stats.kB_wrtn
          if not host_info["prev_iostat_check"] is None:
             seconds_since_last_check = host_info["curr_iostat_check"] - host_info["prev_iostat_check"]
             read_difference /= seconds_since_last_check
             write_difference /= seconds_since_last_check
          output.append(DiskStat(host_info["curr_iostat"][drive_i].disk_device, read_difference, write_difference))
    else:
      for drive_i in range(0,len(host_info["curr_iostat"])):
        output.append(DiskStat(host_info["curr_iostat"][drive_i].disk_device, 0.0, 0.0))
    return output

def do_df(host_info):
    if host_info["connection"]:
      raw_output, error = run_command(host_info["connection"], \
          '''
            df -h | \
            grep -v udev | \
            grep -v cgroup | \
            grep -v tmpfs | \
            grep -v snap | \
            grep -v boot | \
            grep -v Steam | \
            grep -v //
          '''
      )
      if error:
        print(f"{error}")
        return None
      # Extract the third part (numbers) after splitting by whitespace
      output = "\n".join([re.sub(r'([a-z]*)([0-9]*)(\s*)([0-9].*)', r'\1 \4', line) for line in raw_output.splitlines()])
      # devs = "\n".join([re.sub(r'(^[^\s]*)(\s*)([0-9].*)', r'\1', line) for line in raw_output.splitlines()])

      # Remove the first line
      output_lines = output.splitlines()
      output = "\n".join(output_lines[1:])

      # Exclude lines containing 'Steam'
      output = "\n".join([line for line in output.splitlines() if 'Steam' not in line])

      # Replace '/' at the end of the string with 'Power'
      # output = re.sub(r'\/$', 'Power', output)

      # Remove '/media/user/' from the string
      output = re.sub(r'/media/user/', '', output)

      output = re.sub(r'/dev/', '', output)

      return "Device  Size  Used Avail Use% Drive\n" + output
    return None

def get_connections():
  connections = {
      "mu":    {"ip":"192.168.0.7",   "username":"user",  "password":"Vm10kym#22", "connection":None, "prev_iostat":None, "curr_iostat":None, "curr_iostat_check":None, "prev_iostat_check":None},
      "gamma": {"ip":"192.168.0.2",   "username":"user",  "password":"Vm10kym#22", "connection":None, "prev_iostat":None, "curr_iostat":None, "curr_iostat_check":None, "prev_iostat_check":None}
  }
  for hostname in connections:
      host_info = connections[hostname]
      connection, error = connect(host_info["ip"], host_info["username"], host_info["password"])
      if error:
        print(f"{error}")
      else:
        host_info["connection"] = connection
  return connections

def disconnect_all(connections):
   for hostname in connections:
      host_info = connections[hostname]
      if host_info["connection"]:
        host_info["connection"].close()

def rpad(input, length, char=" "):
  output = input
  while len(output) < length:
    output += " "
  return output

def lpad(input, length, char=" "):
   output = input
   while len(output) < length:
      output = " " + output
   return output

def get_disk_status(connections):
  DiskUsage = namedtuple('DiskUsage', ['dev', 'size', 'used', 'available', 'percentage_used', 'drive'])
  output = ""
  output += "+------------------------------+\n"
  for hostname in connections:
      host_info = connections[hostname]
      df_output = do_df(host_info)
      main_drive = ""
      if hostname == "mu":
          main_drive = "Fox"
      elif hostname == "gamma":
          main_drive = "Power"
      df_output = re.sub(r'/\n', f'{main_drive}\n', df_output)
      io_stats = do_iostat(host_info)
      if df_output:
        data = [DiskUsage(*re.split(r'\s+', line)) for line in re.split(r'\n',df_output)[1:]]
        for entry in data:
           df_percentage = float(entry.percentage_used.replace("%",""))/100.0
           bar_line =  f"| {get_bar(df_percentage, 20)} {entry.drive}"
           bar_line =  rpad(bar_line, 31) + "|"
           info_beginning = rpad(f"| {lpad(entry.available,5)} free of {entry.size}", 22)
           info_line = f"{info_beginning} {rpad(entry.percentage_used,3)}"
           info_line = rpad(info_line, 31) + "|"

           io_line = ""
           for io in io_stats:   
              reading_speed = ""
              writing_speed = ""
              if io.disk_device == entry.dev:
                 kbps_reading = io.kB_read
                 kbps_writing = io.kB_wrtn
                 reading_unit = ""
                 writing_unit = ""
                 if kbps_reading > 1024.0:
                    reading_speed = f"{kbps_reading / 1024.0}"
                    reading_unit = "MB/s"
                 else:
                    reading_speed = f"{kbps_reading}"
                    reading_unit = "KB/s"
                 
                 if kbps_writing > 1024.0:
                    writing_speed = f"{kbps_writing / 1024.0}"
                    writing_unit = "MB/s"
                 else:
                    writing_speed = f"{kbps_writing}"
                    writing_unit = "KB/s"
                 
                 reading_speed = str(reading_speed)[:5]
                 writing_speed = str(writing_speed)[:5]
                 reading_string = lpad(f"↑{reading_speed}", 7)
                 writing_string = lpad(f"↓{writing_speed}", 7)
                 io_line = rpad(f"{reading_string} {reading_unit}", 14) + rpad(f"{writing_string} {writing_unit}", 14)
                 break
           bottom_bar = "+------------------------------+"
           output += f"{bar_line}\n"
           output += f"{info_line}\n"
           # output += rpad(f"| [{rpad(f'↑{reading_speed}', 9)}]  [{lpad(f'↓{writing_speed}', 9)}]", 31) + "|\n"
           output += rpad(f"| {io_line}", 31) + "|\n"
           output += f"{bottom_bar}\n"
      print("===================================")
  return output

_DEBUG = False
def main(stdscr):
   connections = get_connections()
   if not _DEBUG:
    clear = lambda: os.system('cls')
    clear()
   while True:
    if not _DEBUG:
      sys.stdout.write('\033[H')
      sys.stdout.flush()
    disk_status = get_disk_status(connections)
    disk_status_lines = disk_status.splitlines()
    for i in range(0,len(disk_status_lines)):
      if _DEBUG:
         print(f"{disk_status_lines[i]}")
      else:
        stdscr.addstr(i, 0, f"{disk_status_lines[i]}")
        stdscr.refresh()
    
    sleep(5) 
   # print(do_iostat(connections["gamma"]))
   # print(do_df(connections["gamma"]))
   return disconnect_all(connections)

if __name__ == "__main__":
  if _DEBUG:
     main(None)
  else:
     curses.wrapper(main)

'''
  connection = connect(hostname, username, password)
  # output, error = run_command(connection, "ps -aux")
  output, error = do_df(connection)

  if error:
      print(f"{error}")
  else:
      print(f"{output}")

  connection.close()
'''