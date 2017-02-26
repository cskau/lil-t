# lil-t

The following is an experiment in setting a Raspberry Pi (Zero) up as a
soft-synth device, hosting LV2 plug-ins.


## Examine the system
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

Configure overlay to pipe PWM to BCM pins 13 and 18, and remove hissing
background noise by disabling dithering.

Add to `/boot/config.txt`:
```
dtoverlay=pwm-2chan,pin=18,func=2,pin2=13,func2=4
disable_audio_dither=1
```

Packages to `$ sudo apt-get install`:
```
git
python-pip
autoconf
autogen
automake
jackd2
dbus-x11
a2jmidid
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

Python modules to `$ sudo pip install`:
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


## Post-setup testing

Check if JACK will run and can claim the interface:
```
$ dbus-launch jackd -dalsa -Phw:ALSA,0 -Xseq
```
Ctrl-C to kill the process if it successfully starts and runs.


## Install services
Add some system services to auto-start JACK, mod-host, etc. at boot so
everything runs without user interaction.

Copy `*.service` files into `/etc/systemd/system/`:
```
$ sudo cp ./services/*.services /etc/systemd/system/
```

Test the newly added services:
```
$ sudo systemctl start jackd.service
$ sudo systemctl start mod-host.service
$ sudo systemctl start a2jmidid.service
$ sudo systemctl start demo.service
```

```
$ sudo systemctl status jackd.service
$ sudo systemctl status mod-host.service
$ sudo systemctl start a2jmidid.service
$ sudo systemctl start demo.service
```

Enable the service:
```
$ sudo systemctl enable jackd.service
$ sudo systemctl enable mod-host.service
$ sudo systemctl start a2jmidid.service
$ sudo systemctl start demo.service
```


## Test system

Manually tell mod-host to load Qin:
```
$ echo -n 'add http://magnus.smartelectronix.com/lv2/synth/qin 0' | nc -w1 localhost 5555
$ nc -w1 localhost 5556
```

Print all JACK port and their connections:
```
$ sudo jack_lsp -c
```

Connect some JACK ports:
```
$ sudo jack_connect effect_0:output system:playback_1
$ sudo jack_connect effect_0:output system:playback_2
```
