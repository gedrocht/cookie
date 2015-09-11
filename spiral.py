import win32api
import win32con
import time
import math

def move_to(x,y):
	win32api.SetCursorPos((x,y))
	

MINUTE = 60;
HOUR = 60;

x = 0;
y = 0;
sec = MINUTE * HOUR * 3;

theta = 0;

click_reset = 40;
clicked = click_reset-1;

while sec > 0:
	theta += 1;
	
	x = int(sec/12 * math.cos(theta) + 950);
	y = int(300 * math.sin(theta) + 600);
	
	move_to(x,y);
	
	if clicked == 0:
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0);
		clicked = click_reset;
		print sec, "clicking";
	elif clicked == click_reset:
		print sec, "stopping";
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0);
		clicked -= 1;
	else:
		print sec, "clicked: ", clicked
		clicked -= 1;
	
	sec -= 0.033;
	time.sleep(0.033)