#!/usr/bin/env python

import tornado.websocket

import pygtk
pygtk.require('2.0')
import pynotify
import subprocess
import sys

class Bell():
    conn = None
    def __init__(self, host):
        self.connect(host)
        pynotify.init("Ding")

    def connect(self, host):
        ws = tornado.websocket.websocket_connect("ws://%s/dingsocket" % host)
        ws.add_done_callback(self.conn_callback)

    def conn_callback(self, conn):
        self.conn = conn.result()
        self.conn.on_message = self.on_message

    def on_message(self, message):
        if message != None:
            n = pynotify.Notification("Done", message)
            n.show()
            print("Ding! %s" % message)
            subprocess.Popen(["paplay", "bell.ogg"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

import signal
def main():
    try:
        io_loop = tornado.ioloop.IOLoop.instance()
        signal.signal(signal.SIGTERM, io_loop.stop)
        Bell(sys.argv[1])
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()

if __name__ == "__main__":
    main()
