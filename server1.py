#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

import re
import time
import argparse
# import barometer

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


@app.route("/roomstats", methods=["GET"])
def getBaroStats():
    temperature, pressure, humidity = barometer.readBME280All()
    data = {"temperature": temperature, "pressure": pressure, "humdity": humidity}
    return jsonify(data);

@app.route("/display", methods=['POST'])
def displayMessage():
    temp = request.json['temp']
    trend = request.json['trend']
    baro = request.json['baro']
    data={"temp" : temp,"trend":trend, "baro": baro}
    displayDefault(temp,trend,baro)
    return jsonify(data)


def displayDefault(temp, trend,baro):
    matrix = canvas(device)
    if temp < 0:
        temp = abs(temp)
        with matrix as draw:
            text(draw, (0, 0), chr(250), fill="white", font=proportional(CP437_FONT))
    with matrix as draw:
        text(draw, (2, 0), str(temp), fill="white", font=proportional(LCD_FONT))
    if temp >-10 and temp <10:
        text(draw, (6, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    else:
        text(draw, (12, 0), chr(248), fill="white", font=proportional(CP437_FONT))
    if baro <1010:
        print "laag"
        rain(24,0,matrix)
    if baro >1015:
        sun(24,0,matrix)
    if baro>1010 and baro <1015:
        cloud(24,0,matrix)
    if trend =="up":
        up(19,0,matrix)
    if trend =="down":
        down(19,0,matrix)

@app.route("/matrix", methods=["POST"])
def addAccountId():
    type = request.json['type']
    message = request.json['message']
    character = request.json['character']
    xcoord = request.json['xcoord']
    ycoord = request.json['ycoord']
    fontsel = request.json['font']
    message2 = request.json['message2']
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
    startMessage(type, message, message2, character, xcoord, ycoord, font)
    return jsonify(data)


def startMessage(type, msg, msg2, character, xcoord, ycoord, font):
    try:
        fill = "white"
        contrast = 0x05
        device.contrast(contrast)

        if (type == 'runner'):
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

        if (type == 'special'):
            print ("special: ", chr(character))
            with canvas(device) as draw:
                text(draw, (0, 0), msg, fill="white", font=proportional(font))
                text(draw, (xcoord, ycoord), chr(character), fill="white", font=proportional(CP437_FONT))
                text(draw, (xcoord + 8, 0), msg2, fill="white", font=proportional(font))

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
    # canvas1 = canvas(device)
    # displayDefault(-12, "up",2000)
    # time.sleep(1)
    # displayDefault(12, "down", 1000)
    # time.sleep(1)
    # displayDefault(-1, "down", 1013)
    # time.sleep(1)
    # displayDefault(1, "down", 2000)
    # time.sleep(1)

    app.run(host='0.0.0.0', debug=False)
