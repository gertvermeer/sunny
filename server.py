#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import re
import time
import argparse
import barometer

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT
from flask import Flask, jsonify, request

app = Flask(__name__)

instruction = [{'type': "", 'message': ""}];
serial = spi(port=0, device=0, gpio=noop())

device = max7219(serial, cascaded=4, block_orientation=90,
                 rotate=0, blocks_arranged_in_reverse_order=False)
# create matrix device
print("Created device")


# API to collect Barometer stats
@app.route("/roomstats", methods=["GET"])
def getBaroStats():
    temperature, pressure, humidity = barometer.readBME280All()
    data = {"temperature": temperature, "pressure": pressure, "humdity": humidity}
    return jsonify(data);


# Standardmessage
@app.route("/display", methods=['POST'])
def displayMessage():
    temp = request.json['temp']
    trend = request.json['trend']
    baro = request.json['baro']
    data={"temp" : temp,"trend":trend, "baro": baro}
    displayDefault(temp,trend,baro)
    return jsonify(data)


# Standardmessage met  Solat
@app.route("/displaySolar", methods=['POST'])
def displaySolarMessage():
    temp = request.json['temp']
    production = request.json['production']
    data={"temp" : temp,"production":production}
    displaySolar(temp,production)
    return jsonify(data)



def displaySolar(temp, production):
    device.contrast(0x05)
    matrix = canvas(device)
    xoffset = str(temp).count("1")*2 # graden teken goed plaatsen
    if temp < 0:
        temp = abs(temp)
        with matrix as draw:
            text(draw, (0, 0), chr(250), fill="white", font=proportional(CP437_FONT))
    with matrix as draw:
        text(draw, (2, 0), str(temp), fill="white", font=proportional(LCD_FONT))
    if temp >-10 and temp <10:
        text(draw, (8-xoffset, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    else:
        text(draw, (14-xoffset, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    with matrix as draw:
        text(draw, (18, 0), str(production), fill="white", font=proportional(LCD_FONT))
        
        
def displayDefault(temp, trend,baro):
    device.contrast(0x05)
    matrix = canvas(device)
    xoffset = str(temp).count("1")*2 # graden teken goed plaatsen
    if temp < 0:
        temp = abs(temp)
        with matrix as draw:
            text(draw, (0, 0), chr(250), fill="white", font=proportional(CP437_FONT))
    with matrix as draw:
        text(draw, (2, 0), str(temp), fill="white", font=proportional(LCD_FONT))
    if temp >-10 and temp <10:
        text(draw, (8-xoffset, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    else:
        text(draw, (14-xoffset, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    if baro <1010:
        print "laag"
        rain(24,0,matrix)
    if baro >1015:
        sun(24,0,matrix)
    if baro>1009 and baro <1016:
        cloud(24,0,matrix)
    if trend =="up":
        up(20,0,matrix)
    if trend =="down":
        down(20,0,matrix)

#Alert
@app.route("/matrix", methods=["POST"])
def addAccountId():
    device.contrast(0x05)
    type = request.json['type']
    message = request.json['message']
    character = request.json['character']
    xcoord = request.json['xcoord']
    ycoord = request.json['ycoord']
    fontsel = request.json['font']
    if fontsel == "TINY_FONT":
        font = TINY_FONT;
    if fontsel == "LCD_FONT":
        font = LCD_FONT;
    if fontsel == "CP437_FONT":
        font = CP437_FONT
    if fontsel == "SINCLAIR_FONT":
        font = SINCLAIR_FONT;

    print("received", message, character, xcoord, ycoord, fontsel)
    data = {'type': type, 'message': message}
    startMessage(type, message,  character, xcoord, ycoord, font)
    return jsonify(data)


def startMessage(type, msg, character, xcoord, ycoord, font):
    try:
        fill = "white"
        if (type == 'runner'):
            device.contrast(0x05)
            print ("runner: ", msg)
            show_message(device, msg, fill=fill, font=proportional(font))

        if (type == 'special'):
            device.contrast(0x20)
            print ("runner: ", msg)
            show_message(device, msg, fill=fill, font=proportional(font))

        if (type == 'fixed'):
            print ("fixed: ", msg)
            with canvas(device) as draw:
                text(draw, (xcoord, ycoord), msg, fill="white", font=proportional(font))

        if (type == 'character'):
            print ("special: ", chr(character))
            with canvas(device) as draw:
                text(draw, (xcoord, ycoord), chr(character), fill="white", font=proportional(font))
    except KeyboardInterrupt:
        pass


def sun(x, y, canvas):
    with canvas as draw:
        text(draw, (x + 0, y + 0), chr(15), fill="white", font=proportional(CP437_FONT))


def rain(x, y,canvas):
        with canvas as draw:
            text(draw, (x + 0, y - 1), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 2, y - 1), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 4, y - 1), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 6, y - 1), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 1, y - 3), chr(250), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 2, y - 3), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 4, y - 3), chr(250), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 5, y - 3), chr(249), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 7, y - 3), chr(250), fill="white", font=proportional(CP437_FONT))
            text(draw, (x + 1, y ), chr(46), fill="white", font=proportional(TINY_FONT))
            text(draw, (x + 1, y + 2), chr(46), fill="white", font=proportional(TINY_FONT))
            text(draw, (x + 3, y ), chr(46), fill="white", font=proportional(TINY_FONT))
            text(draw, (x + 3, y + 2), chr(46), fill="white", font=proportional(TINY_FONT))
            text(draw, (x + 5, y), chr(46), fill="white", font=proportional(TINY_FONT))
            text(draw, (x + 5, y ++2), chr(46), fill="white", font=proportional(TINY_FONT))


def cloud(x, y, canvas):
    with canvas as draw:
        text(draw, (x + 0, y +2), chr(249), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 2, y +2), chr(249), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 4, y +2), chr(249), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 6, y +2), chr(249), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 1, y), chr(250), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 2, y), chr(249), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 4, y), chr(250), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 6 ,y-1), chr(250), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 5, y), chr(250), fill="white", font=proportional(CP437_FONT))
        text(draw, (x + 5, y-3), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 5, y-4), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 3, y-4), chr(46), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 4, y-2), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 5, y-1), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 6, y-3), chr(46), fill="white", font=proportional(TINY_FONT))
        text(draw, (x + 7, y-4), chr(46), fill="white", font=proportional(TINY_FONT))

def up(x, y, canvas):
    with canvas as draw:
        text(draw, (x+1, y), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x+1, y-2), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x, y-2), chr(46), fill="white", font=proportional(TINY_FONT))
        text(draw, (x+2, y-2), chr(46), fill="white", font=proportional(TINY_FONT))

def down(x, y, canvas):
    with canvas as draw:
        text(draw, (x+1, y), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x+1, y-2), chr(44), fill="white", font=proportional(TINY_FONT))
        text(draw, (x , y-1), chr(46), fill="white", font=proportional(TINY_FONT))
        text(draw, (x+2, y-1), chr(46), fill="white", font=proportional(TINY_FONT))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
