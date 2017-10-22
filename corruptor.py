import binascii
import sys
import os
from random import random

VERBOSE = False;

def go():
    input = open(sys.argv[1],"rb");
    output = open(sys.argv[1] + "_corrupted.nes","wb");
    output.write(input.read(2048))
    while True:
        data = input.read(2048);
        if len(data) == 0:
            break;
        output.write(corrupt(data));
        output.flush();
    output.close();
    pass;

def corrupt(data):
    data_index = int(round(random()*len(data)));
    hex_data = binascii.hexlify(data[data_index]);
    random_hex = get_random_hex();
    if random() < 0.5:
        hex_data = hex_data[0] + random_hex;
    else:
        hex_data = random_hex + hex_data[1];
    binary_data = binascii.unhexlify(hex_data);
    data = data[0:data_index] + binary_data + data[data_index+1:]
    return data;

def get_random_hex():
    return ('0123456789abcdef')[int(round(random()*15))]
go();