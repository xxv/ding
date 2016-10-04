#!/usr/bin/env python

import json
import paho.mqtt.client as paho
import socket
import subprocess
import sys
from datetime import timedelta, datetime
from os import path


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
    special_alerts = None
    playback = None
    bell = None
    mqtt = None

    def __init__(self, mqtt, playback, bell, special_alerts=None):
        self.mqtt_config = mqtt
        self.special_alerts = special_alerts
        self.playback = playback
        self.bell = bell
        self.mqtt = paho.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message
        self.connect()

    def connect(self):
        self.mqtt.username_pw_set(self.mqtt_config['username'], self.mqtt_config['password'])
        self.mqtt.connect(self.mqtt_config['host'])

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
        config_file_path = path.expanduser("~/.ding.conf")
        if len(sys.argv) > 1:
            print("usage: %s" % sys.argv[0])
            sys.exit(1)

        config = {}
        with open(config_file_path) as config_file:
            config = json.load(config_file)

        sound = None
        if config['sound'] == 'pulseaudio':
            sound = PulseAudioPlay()
        elif config['sound'] == 'audiofile':
            sound = AudioFilePlay()

        bell = Bell(config['mqtt'], sound, config['bell'], config['special_alerts'])
        bell.mqtt.loop_forever()
    except KeyboardInterrupt:
        bell.mqtt.disconnect()

if __name__ == "__main__":
    main()
