# VKCRobot

use knock-off USB drivers for LittleBig Arm Windows USB communciation with Arduino IDE
<link>

sudo apt-get update && sudo apt-get upgrade

delete JUST the text "console=serial0,115200" from "/boot/cmdline.txt".  Leave other text intact.  Do not comment lines, file must contain only one line when finished

install opencv from EscapeRoom tools

pip3 install imutils

frees 800 MB of space:
sudo apt-get purge wolfram-engine

sudo apt-get install arduino

researching...
(
sudo nano /boot/config.txt
add ",i2c_arm_baudrate=400000" after (on the same line as) "dtparam=i2c_arm=on"
)

download old i2c driver (that allows for disabling resending start bit), then modify /boot/config.txt per instructions below:
https://github.com/raspberrypi/firmware/issues/828#issuecomment-311262108

configure adhoc for communication between rpi's (wireless), with the capabiolity to swap to tethered internet for GitHub updates (eth0)
ad-hoc: https://wiki.debian.org/WiFi/AdHoc
hot-swapping network connections: https://unix.stackexchange.com/questions/316031/programmatically-switch-between-ad-hoc-and-regular-network
add the text below the dashes to the existing 'interface' file
With XXX as an int between 0 and 255, YYY and a string:
Use one value for XXX on one rpi, use a different value on another rpi
ex. 192.168.1.1 on target and 192.168.1.2 in source
sudo nano /etc/network/interfaces

------------

auto lo
iface lo inet loopback

auto eth0
allow-hotplug eth0
iface eth0 inet dhcp

auto wlan0
allow-hotplug wlan0
iface wlan0 inet static
    address 192.168.1.XXX
    netmask 255.255.255.0
    wireless-channel 1
    wireless-essid YYY
    wireless-mode ad-hoc
iface normal inet dhcp

----------

to swap between configurations:

swap to rpi-rpi communication:
sudo ifdown eth0
sudo ifup wlan0

swap to internet:
sudo ifdown wlan0
sudo ifup eth0

----------

sudo apt-get install zbar-tools
sudo apt-get install python-zbar
sudo apt-get install libzbar0
sudo pip3 install zbar
#zbar not support under python3, need to use alternative...
pip3 install pyzbar

----

sudo pip3 install wiringpi
also, enable i2c, camera, etc from start > pref > conf > Interfaces
ref EscapeRoom

---

edited rc.local to add line:
python3 /home/pi/Documents/VKCRobot/src/build_test.py &