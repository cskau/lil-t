#!/bin/bash

add_plugin () {
  sudo -u pi -g audio jack_disconnect "a2j:Teensy MIDI [20] (playback): Teensy MIDI MIDI 1" "effect_0:$2"
  sudo -u pi -g audio jack_disconnect "effect_0:$3" "system:playback_1"
  sudo -u pi -g audio jack_disconnect "effect_0:$4" "system:playback_2"

  nc -w1 localhost 5556
  echo -n "remove 0" | nc -w1 localhost 5555
  nc -w1 localhost 5556

  nc -w1 localhost 5556
  echo -n "add $1 0" | nc -w1 localhost 5555
  nc -w1 localhost 5556

  sudo -u pi -g audio jack_connect "a2j:Teensy MIDI [20] (playback): Teensy MIDI MIDI 1" "effect_0:$2"
  sudo -u pi -g audio jack_connect "effect_0:$3" "system:playback_1"
  sudo -u pi -g audio jack_connect "effect_0:$4" "system:playback_2"
}

case $((RANDOM % 5)) in
0)
  add_plugin "http://magnus.smartelectronix.com/lv2/synth/qin" "midi" "output" "output"
  ;;
1)
  add_plugin "http://drobilla.net/plugins/mda/Piano" "event_in" "left_out" "right_out"
  ;;
2)
  add_plugin "http://drobilla.net/plugins/mda/EPiano" "event_in" "left_out" "right_out"
  ;;
3)
  add_plugin "http://drobilla.net/plugins/mda/DX10" "event_in" "left_out" "right_out"
  ;;
4)
  add_plugin "http://drobilla.net/plugins/mda/JX10" "event_in" "left_out" "right_out"
  ;;
*)
  echo "???"
  ;;
esac
