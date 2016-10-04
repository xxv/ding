Ding!
=====

A simple way to be notified of long-running processes finishing, even if
they're on remote servers.

Requirements
------------

* Python
* MQTT broker

Usage
-----

Copy `config.json.example` to `~/.ding.conf` and modify it with your settings.
If there is no keyword specified, ding will just play the "bell" sound. Otherwise, it will play the
special alert for the given keyword.

Run `bell.py` on a computer with speakers.

Then you can run `ding` on any computer that you wish to have trigger a sound.

One handy usage is to have it trigger after a long-running command:

```sh
YOUR_LONG_RUNNING_COMMAND AND_ARGUMENTS GOES_HERE; ding keyword
```
