#!/bin/sh

### BEGIN INIT INFO
# Provides:          lil-t
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description:
# Description
### END INIT INFO

# Steps:
# Make the script runable:
#  sudo chmod 755 /etc/init.d/lil-t.sh
# Test the start mechanism:
#  sudo /etc/init.d/lil-t.sh start
# Test the stop mechanism:
#  sudo /etc/init.d/lil-t.sh stop
# Set up script for start at boot-up:
#  sudo update-rc.d lil-t.sh defaults
# Remove script from boot-up sequence:
#  sudo update-rc.d -f lil-t.sh remove

case "$1" in
  start)
    echo "Starting lil-t"
    # /usr/local/bin/lil-t
    ;;
  stop)
    echo "Stopping lil-t"
    # killall lil-t
    ;;
  *)
    echo "Usage: /etc/init.d/lil-t.sh {start|stop}"
    exit 1
    ;;
esac

exit 0
