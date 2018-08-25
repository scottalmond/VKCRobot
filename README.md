# VKCRobot

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

