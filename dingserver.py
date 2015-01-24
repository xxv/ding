#!/usr/bin/env python
"""
Ding! Your process is done.
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/ding", DingHandler),
            (r"/dingsocket", DingSocketHandler),
        ]
        settings = dict(
            xsrf_cookies=False,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class DingHandler(tornado.web.RequestHandler):
    def post(self):
        DingSocketHandler.send_updates(self.request.body)

class DingSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def open(self):
        DingSocketHandler.waiters.add(self)

    def on_close(self):
        DingSocketHandler.waiters.remove(self)

    @classmethod
    def send_updates(cls, ding):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(ding)
            except:
                logging.error("Error sending message", exc_info=True)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
