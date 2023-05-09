from PIL import Image

import binascii
import sys
import os

VERBOSE = False;

def build_canvas(width, height):
    canvas = []
    if VERBOSE:
        print "Building canvas..."
    for x in range(0,width):
        temp = [];
        for y in range(0,height):
            temp.append(0)
        canvas.append(temp[:])
    if VERBOSE:
        print "Canvas width: {0}".format(len(canvas))
        print "Canvas height: {0}".format(len(canvas[0]))
    return canvas;

def render(pixels,filename,width,height):
    new_im = Image.new("RGB",(width,height))
    new_im.putdata(pixels)
    new_im.save(filename)    

def setCanvas(x,y,red,green,blue,width,height,canvas):
    if x >= width:
        x = width-1;
    if y >= height:
        y = height-1;
    canvas[x][y] = (red,green,blue)

def generate_image( filename, offset ):
    canvas = []
    x = 0;
    y = 0;
    width = 0;
    height = 0;
    x_limit = 32;
    y_limit = -1;

    with open(filename, 'rb') as f:
        statinfo = os.stat(filename)
        if VERBOSE:
            print "File size: " + str(statinfo.st_size/1024) + " KB"
            print "Width and Height: " + str(int((statinfo.st_size/3) ** (0.5)))
        hexdata = binascii.hexlify(f.read())
        width = int((statinfo.st_size/3) ** (0.5))
        height = width;
        if VERBOSE:
            print "WIDTH AND HEIGHT SET: {0}x{1}".format(width,height)
        y_limit = height;
        canvas = build_canvas(width, height)
        
        i = offset;
        red = 0
        green = 0
        blue = 0
        x_offset = 0;
        y_offset = 0;
        pixels = [];
        limit = width * height
        while True:
            if i + 6 >= len(hexdata):
                break;
            if len(pixels) >= limit:
                break;
            if VERBOSE:
                pass
                #print hexdata[i:i+6]
            red =   hexdata[i+0:i+2]
            green = hexdata[i+2:i+4]
            blue =  hexdata[i+4:i+6]
            if VERBOSE:
                pass
                #print (red, green, blue)
            red =   int(red,16)
            green = int(green, 16)
            blue =  int(blue,16)
            if VERBOSE:
                pass
               # print (red, green, blue)
            
            setCanvas(y,x+x_offset,red,green,blue,width,height,canvas)
            x+=1;
            if x > x_limit:
                x = 0;
                y += 1;
                if y > y_limit:
                    x_offset += x_limit;
                    x = x_offset;
                    y = 0;
            i+=6;
        if VERBOSE:
            print hexdata[0:3000]
        for x in range(0,len(canvas)):
            for y in range(0, len(canvas[x])):
                pixels.append(canvas[x][y])
        render(pixels, filename + str(offset) + ".png", width, height)

generate_image(sys.argv[1],0);