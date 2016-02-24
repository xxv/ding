#!/usr/bin/env python

# Copyright 2015 Steve Pomeroy <steve@staticfree.info> GPLv2
# with lots of inspiration/copying from
# https://gist.github.com/fcicq/5328876
# fcicq <fcicq@fcicq.net>, 2013.4.7, GPLv2

import tornado.websocket

import subprocess
import sys
from datetime import timedelta, datetime
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketClosedError
from socket import gaierror
import socket
import json

class Play():
    def play(self, sound_file):
        pass

class AudioFilePlay(Play):
    def play(self, sound_file):
        subprocess.Popen(["afplay", sound_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class PulseAudioPlay(Play):
    def play(self, sound_file):
        subprocess.Popen(["paplay", sound_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class Bell():
    PING_TIMEOUT = 15
    RECONNECT_TIMEOUT = 1
    conn = None
    keepalive = None
    reconnection = None
    host = None
    special_alerts = None
    playback = None
    bell = None

    def __init__(self, host, playback, bell, special_alerts=None):
        self.host = host
        self.connect()
        self.special_alerts = special_alerts
        self.playback = playback
        self.bell = bell

    def connect(self):
        ws = tornado.websocket.websocket_connect("ws://%s/dingsocket" % self.host)
        ws.add_done_callback(self.conn_callback)
        self.ws = ws

    def dokeepalive(self):
        stream = self.conn.protocol.stream
        stream.set_close_callback(self.reconnect_delayed)
        if not stream.closed():
           self.keepalive = stream.io_loop.add_timeout(
                   timedelta(seconds=self.PING_TIMEOUT), self.dokeepalive)
           try:
               self.conn.protocol.write_ping(bytes("", 'utf-8'))
           except WebSocketClosedError:
               self.reconnect_delayed()
        else:
            self.keepalive = None # should never happen

    def conn_callback(self, conn):
        try:
            self.conn = conn.result()
            self.conn.on_message = self.on_message
            self.keepalive = IOLoop.instance().add_timeout(
                    timedelta(seconds=self.PING_TIMEOUT), self.dokeepalive)
            print("Connected.")
        except WebSocketClosedError:
           self.reconnect_delayed()
        except gaierror:
           self.reconnect_delayed()

    def on_message(self, message):
        if message is not None:
            print("%s: Ding! %s" % (datetime.now(), message))
            sound_file = self.bell
            if message in self.special_alerts:
                sound_file = self.special_alerts[message]
            self.playback.play(sound_file)
        else:
            self.reconnect_delayed()

    def reconnect_delayed(self):
        if self.reconnection is not None:
            reconnection = self.reconnection
            self.reconnection = None
            IOLoop.instance().remove_timeout(reconnection)
        self.reconnection = IOLoop.instance().add_timeout(
                timedelta(seconds=self.RECONNECT_TIMEOUT), self.reconnect)

    def reconnect(self):
        print("Attempting to reconnect...")
        if self.keepalive is not None:
            keepalive = self.keepalive
            self.keepalive = None
            IOLoop.instance().remove_timeout(keepalive)
        self.connect()

import signal
def main():
    bell = None
    try:
        io_loop = IOLoop.instance()
        signal.signal(signal.SIGTERM, io_loop.stop)
        if len(sys.argv) < 2:
            print("%s config_file.json" % sys.argv[0])
            sys.exit(1)

        config = {}
        with open(sys.argv[1]) as config_file:
            config = json.load(config_file)

        bell = Bell(config['server'], PulseAudioPlay(), config['bell'], config['special_alerts'])
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()
    except OSError as e:
        print("OSError: %s" % e)
        if bell:
            bell.reconnect_delayed()
    except socket.error:
        print("socket error")
        if bell:
            bell.reconnect_delayed()

if __name__ == "__main__":
    main()
