from datetime import datetime, timezone
from suncalc import get_position, get_times
import math

LATITUDE = 43.008472
LONGITUDE = -71.436389
COMPASS_HEADING_deg = 302.5

HUMAN_READABLE = False

def print_position(when=datetime.now(), longitude=LONGITUDE, latitude=LATITUDE):
  sun_position_rad = get_position(when, longitude, latitude)
  azimuth_rad = sun_position_rad["azimuth"]
  altitude_rad = sun_position_rad["altitude"]
  azimuth_deg = math.degrees(azimuth_rad) % 360.0
  altitude_deg = math.degrees(altitude_rad) % 360.0
  sun_angle_deg = (360.0 - azimuth_deg) % 360.0

  if HUMAN_READABLE:
    print("Time: " + str(when))
    print("Window Angle: " + str(round(COMPASS_HEADING_deg*10)/10) + "°")
    print("Sun Angle: " + str(round(sun_angle_deg*10)/10) + "°")
    print("Sun Altitude: " + str(round(altitude_deg*10)/10) + "° above the horizon")
  else:
    print(str(when) + "," + str(sun_angle_deg) + "," + str(altitude_deg))

def pad_str(string, length=2, character="0"):
  string = str(string)
  while len(string) < length:
    string = character + string
  return string

def dt_from_values(year, month, day, hour, minute=0, second=0):
  return datetime.fromisoformat(
    str(year) + "-" + pad_str(month) + "-" + pad_str(day) + "T" + 
    pad_str(hour) + ":" + pad_str(minute) + ":" + pad_str(second) + ".000000")

def dt_set_time(dt, hour, minute=0, second=0):
  year = dt.year
  month = dt.month
  day = dt.day
  return dt_from_values(year, month, day, hour, minute, second)

def print_positions_for_day(when=datetime.now(), longitude=LONGITUDE, latitude=LATITUDE):
  for hour in range(0,24):
    print_position(dt_set_time(when, hour))
    if HUMAN_READABLE:
      print("-----------")

print_positions_for_day()