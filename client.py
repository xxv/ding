#!/usr/bin/env python

# Copyright 2015 Steve Pomeroy <steve@staticfree.info> GPLv2
# with lots of inspiration/copying from
# https://gist.github.com/fcicq/5328876
# fcicq <fcicq@fcicq.net>, 2013.4.7, GPLv2

import tornado.websocket

import pygtk
pygtk.require('2.0')
import pynotify
import subprocess
import sys
from datetime import timedelta
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketClosedError
from socket import gaierror

class Bell():
    PING_TIMEOUT = 15
    RECONNECT_TIMEOUT = 1
    conn = None
    keepalive = None
    reconnection = None
    host = None

    def __init__(self, host):
        self.host = host
        self.connect()
        pynotify.init("Ding")

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
               self.conn.protocol.write_ping("")
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
        except WebSocketClosedError:
           self.reconnect_delayed()
        except gaierror:
           self.reconnect_delayed()

    def on_message(self, message):
        if message is not None:
            n = pynotify.Notification("Done", message)
            n.show()
            print("Ding! %s" % message)
            subprocess.Popen(["paplay", "bell.ogg"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            self.reconnect_delayed()

    def reconnect_delayed(self):
        if self.reconnect is not None:
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
    try:
        io_loop = IOLoop.instance()
        signal.signal(signal.SIGTERM, io_loop.stop)
        Bell(sys.argv[1])
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()

if __name__ == "__main__":
    main()
