#!/usr/bin/env python

import json
import paho.mqtt.client as paho
import socket
import ssl
import subprocess
import sys
from datetime import timedelta, datetime
from os import path

from ding import Ding

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

class Bell(Ding):
    special_alerts = None
    playback = None
    bell = None

    def __init__(self, mqtt, playback, bell, special_alerts=None):
        super(Bell, self).__init__(mqtt)
        self.mqtt_config = mqtt
        self.special_alerts = special_alerts
        self.playback = playback
        self.bell = bell
        self.mqtt = paho.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Connected!")
        self.mqtt.subscribe(self.mqtt_config['topic'] + '/#')

    def on_message(self, client, userdata, mqtt_message):
        message = mqtt_message.topic.split('/')[1]
        print("%s: Ding! %s" % (datetime.now(), message))
        sound_file = self.bell
        if message in self.special_alerts:
            sound_file = self.special_alerts[message]
        self.playback.play(sound_file)

def main():
    bell = None
    try:
        if len(sys.argv) > 1:
            print("usage: %s" % sys.argv[0])
            sys.exit(1)

        config = Ding.load_config()

        sound = None
        if config['sound'] == 'pulseaudio':
            sound = PulseAudioPlay()
        elif config['sound'] == 'audiofile':
            sound = AudioFilePlay()

        bell = Bell(config['mqtt'], sound, config['bell'], config['special_alerts'])
        bell.connect()
        bell.loop_forever()
    except KeyboardInterrupt:
        bell.disconnect()

if __name__ == "__main__":
    main()
