Ding!
=====

A simple way to be notified of long-running processes finishing, even if
they're on remote servers.

Note: this is currently a hack and has no security. At present, that's OK, as
there's not much someone could do other than annoy you.

Requirements
------------

Server

* A place to host dingserver.py
* Python
* Tornado

Client (the thing that makes the alerts)

* Python
* pygtk
* pynotify
* Tornado

Remote process

* curl

Usage
-----

Find a cozy server to run `dingserver.py`. Your client will connect to that via
websockets, so that it'll be notified of alerts. The remote process will then
simply send a POST request to the server and deliver the alert to the client.

There's a handy `ding` shell script which you just use by adding it to your
path and doing:

```sh
YOUR_LONG_RUNNING_COMMAND AND_ARGUMENTS GOES_HERE; ding 'Your job has finished.'
```


