# lil-t

The following is an experiment in setting a Raspberry Pi (Zero) up as a
soft-synth device, hosting LV2 plug-ins.


## Examine the system you're configuring:
List ALSA playback interfaces:
```
$ aplay -L
```

List ALSA capture interfaces:
```
$ arecord -l
```

Test audio output by playing a sine wave:
```
$ speaker-test -t sine -c 2
```


## System setup

Configure overlay to pipe PWM to BCM pins 13 and 18 by adding to `/boot/config.txt`:
```
dtoverlay=pwm-2chan,pin=18,func=2,pin2=13,func2=4
```

Packages to `sudo apt-get install`:
```
git
python-pip
autoconf
autogen
automake
jackd2
dbus-x11
python-dev
python-tk
python-numpy
libreadline-dev
libportmidi0
libportmidi-dev
libffi-dev
libasound2-dev
libjack-jackd2-dev
```

Python modules to `sudo pip install`:
```
JACK-Client
python-rtmidi
mido
```

Bring in some packages not in the default repo, build and install:
```
$ mkdir src  &&  cd src/
```

lilv, LV2, etc:
```
$ cd ~/src/
$ git clone http://git.drobilla.net/drobillad.git
$ cd drobilla
$ git submodule init  &&  git submodule update  &&  git pull
$ ./waf configure --bindings  &&  ./waf  &&  sudo ./waf install
```

mod-host LV2 host:
```
$ cd ~/src/
$ git clone https://github.com/moddevices/mod-host.git
$ cd mod-host
$ make  &&  sudo make install
```

qin LV2 plug-in:
```
$ cd ~/src/
$ git clone https://github.com/magnusjonsson/qin.git
$ cd qin
$ make ; sudo make install
```


## Some post-setup testing

Check if JACK will run and can claim the interface:
```
dbus-launch jackd -dalsa -Phw:ALSA,0 -Xseq
```
Ctrl-C to kill the process if it succesfully starts and runs.


## Install services
Add some system services to auto-start JACK, mod-host, etc. at boot so
everything runs without user interaction.

Copy `*.service` files into `/etc/systemd/system/`:
```
$ sudo cp ./services/*.services /etc/systemd/system/
```

Test the newly added service:
```
$ systemctl start jackd.service
```

Enable the service:
```
$ systemctl enable jackd.service
```
