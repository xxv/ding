#!/usr/bin/env python

import json
import paho.mqtt.client as paho
import ssl
import sys
from os import path

class Ding():
    mqtt = None

    def __init__(self, mqtt=None):
        self.mqtt_config = mqtt or self.load_config()['mqtt']
        self.mqtt = paho.Client()

    def load_config(self=None, config_file_name="~/.ding.conf"):
        config = {}
        config_file_path = path.expanduser(config_file_name)
        with open(config_file_path) as config_file:
            config = json.load(config_file)
            return config

    def connect(self):
        self.mqtt.username_pw_set(self.mqtt_config['username'], self.mqtt_config['password'])
        if 'ca_certs' in self.mqtt_config:
            self.mqtt.tls_set(self.mqtt_config['ca_certs'], tls_version=ssl.PROTOCOL_TLSv1_2)
        self.mqtt.connect(self.mqtt_config['host'], self.mqtt_config['port'])

    def ding(self, message=None):
        topic = self.mqtt_config['topic']
        if not message:
            message = "ding"
        topic += '/' + message
        self.mqtt.publish(topic)

    def loop_forever(self):
        self.mqtt.loop_forever()

    def disconnect(self):
        self.mqtt.disconnect()

def main():
    ding = None
    if len(sys.argv) > 2:
        print("usage: %s [keyword]" % sys.argv[0])
        sys.exit(1)

    ding = Ding()
    ding.connect()

    message = None
    if len(sys.argv) > 1:
        message = sys.argv[1]
    ding.ding(message)

if __name__ == "__main__":
    main()

