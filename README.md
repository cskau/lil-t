# lil-t

Note: these tools require various libraries and system services to be of any use.

- JACK, python-jack-client
- lilv, usable LV2 plugins
- python-mido
- https://github.com/moddevices/mod-host


## Setup

```
$ sudo apt-get install python-tk
```

If you're on a system that doesn't have, say, python-jack-client in the package
manager (like Raspbian), you can install some of them through PIP:
```
$ sudo apt-get install libffi-dev
$ sudo pip install JACK-Client
```

Mido:
```
$ sudo apt-get install libportmidi0 libportmidi-dev
$ sudo pip install python-rtmidi
$ sudo pip install mido
```

Numpy:
```
$ sudo apt-get install python-numpy
```


## lil-ui.py

Create a really simple UI for mod-host loads plugins and controls parameters
through the socket connection:
```
$ ./lil-ui.py
```

Naturally you'll need to be running mod-host listening to the default port first:
```
$ mod-host -p 5555
```


## lv2.py

List installed LV2 plugins:
```
$ ./lv2.py -l
Loading plugins ...
Plugins found:
0:
Qin
  URI: http://magnus.smartelectronix.com/lv2/synth/qin
  bundle URI: file:///home/user/.lv2//mj-qin.lv2/
  library URI: file:///home/user/.lv2//mj-qin.lv2/qin.so
  class: http://lv2plug.in/ns/lv2core#Plugin
  ports: 10
  latency port: None
  Required features:
    http://lv2plug.in/ns/ext/event
    http://lv2plug.in/ns/ext/uri-map
  Supported features:
    http://lv2plug.in/ns/lv2core#hardRtCapable
    http://lv2plug.in/ns/ext/uri-map
    http://lv2plug.in/ns/ext/event
  Optional features:
    http://lv2plug.in/ns/lv2core#hardRtCapable
  UIs:
  Ports:
    Output
    MIDI Input
    Amp Decay
    LP Filter Decay
    HP Filter Decay
    Amp Release
    LP Filter Release
    HP Filter Release
    Pulse Width
    Detune
[...]
Bye!
```

Attempt to run a particular plugin: (Note: probably doesn't work yet.)
```
$ ./lv2.py -p 0
Loading plugins ...
Instantiating plugin 0:
[...]
Activating plugin ..
[...]
```


## midi_out.py

Print some "diagnostics" about current MIDI ports on the system:
```
$ ./midi_out.py -d
MIDI input ports:
  0 Midi Through Port-0
  1 Teensy MIDI MIDI 1
MIDI I/O ports:
  0 Midi Through Port-0
  1 Teensy MIDI MIDI 1
MIDI output ports:
  0 Midi Through Port-0
  1 Teensy MIDI MIDI 1
[...]
```

Connect to first MIDI port and continuously toggle note 60 on and off:
```
$ ./midi_out.py
Opening port for output: Midi Through Port-0
Sending MIDI note 60 with velocity 60 at 60 BPM
```

Or a specific port, note, velocity and BPM (note toggles per minute):
```
$ ./midi_out.py -p 1 -n 64 -v 100 -b 30
Opening port for output: Teensy MIDI MIDI 1
Sending MIDI note 64 with velocity 100 at 30 BPM
```


## test_jack.py

Create a JACK client and print various information about the server and ports:
```
$ test_jack.py
Creating JACK client..
Activating..
Ports:
  jack.Port('system:capture_1')
  jack.Port('system:capture_2')
  jack.Port('system:playback_1')
  jack.Port('system:playback_2')
  jack.MidiPort('alsa_midi:Midi Through Midi Through Port-0 in')
  jack.MidiPort('alsa_midi:Midi Through Midi Through Port-0 out')
  jack.MidiPort('alsa_midi:Teensy MIDI Teensy MIDI MIDI 1 in')
  jack.MidiPort('alsa_midi:Teensy MIDI Teensy MIDI MIDI 1 out')
Transport state:
  jack.STOPPED
  {'frame': 0, 'frame_rate': 44100, 'usecs': 30798191999L}
jack.OwnPort('my_test_client:my_in')
jack.OwnPort('my_test_client:my_out')
0.0
```
