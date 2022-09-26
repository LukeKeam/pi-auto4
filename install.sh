#!/bin/bash
echo "Thanks for choosing pi-auto4 from https://fleet-track.org"
# have installed and working os, you will not need a gui!
# Raspberry Pi OS Lite 32bit os https://www.raspberrypi.com/software/operating-systems/
# curl -LJO https://raw.githubusercontent.com/LukeKeam/pi-auto4/master/install.sh && sudo bash ./install.sh
# once have ssh connection to pi

# update
sudo apt-get update
sudo apt-get upgrade -y

# install
sudo apt-get install python3 python3-pip tmux minicom screen bluetooth busybox-syslogd wvdial libqmi-utils ntp git -y

# update host name
echo "Updating host name to pi-auto4"
newhostname="pi-auto4"
echo "$newhostname" | sudo tee /etc/hostname
# add hostname to /etc/hosts
echo "127.0.1.1   $newhostname" | sudo tee -a /etc/hosts

# update password?
# mypassword="password"
# echo "$mypassword" | passwd --stdin

echo "Downloading and creating /pi-auto4"
# creat dir
cd /

# clone repository
sudo git clone https://github.com/LukeKeam/pi-auto4.git
sudo chown -R "$USER":"$USER" /pi-auto4
cd /pi-auto4

# pip install
sudo pip3 install -r requirements.txt


echo "Making Service"
# add service
append_line='# sudo nano /lib/systemd/system/pi-auto4.service
# sudo systemctl restart pi-auto4.service
# sudo systemctl status pi-auto4.service
# sudo systemctl enable pi-auto4.service
# sudo systemctl daemon-reload
# User=pi?

[Unit]
Description=pi-auto4
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/pi-auto4
ExecStart=/bin/bash -c "mount -o remount,rw /pi-auto4 && python3 /pi-auto4/main.py"

[Install]
WantedBy=multi-user.target'
echo "$append_line" | sudo tee /lib/systemd/system/pi-auto4.service # need to make other lines ro
sudo systemctl enable pi-auto4.service

echo "Making OS read only"
# https://hallard.me/raspberry-pi-read-only/
# make os read only
append_line="/home/pi/pi-auto4     /pi-auto4        ext4    defaults,bind,rw     0       0
tmpfs        /tmp            tmpfs   nosuid,nodev         0       0
tmpfs        /var/log        tmpfs   nosuid,nodev         0       0
tmpfs        /var/tmp        tmpfs   nosuid,nodev         0       0"
echo "$append_line" | sudo tee -a /etc/fstab # need to make other lines ro
sudo apt-get remove --purge triggerhappy logrotate dphys-swapfile -y
# sudo apt-get autoremove --purge -y  # this needed?
# sudo nano /boot/cmdline.txt # add fastboot noswap ro
echo "fastboot noswap ro" | sudo tee -a /boot/cmdline.txt # not on the same line though
sudo apt-get install busybox-syslogd -y
sudo rm /var/lib/systemd/random-seed &&
sudo ln -s /tmp/random-seed /var/lib/systemd/random-seed
# edit random seed service
sed '/^RemainAfterExit=.*/a ExecStartPre=/bin/echo' /lib/systemd/system/systemd-random-seed.service


echo "Update UART "
# add line to config enable uart # # raspi-config for serial???
append_line="enable_uart=1"
echo "$append_line" | sudo tee -a /boot/config.txt


: '
This Needed? as it updaes time on every start? and gets time off gps

# time cronjob
# /etc/cron.hourly/fake-hwclock
#!/bin/sh
#
# Simple cron script - save the current clock periodically in case of
# a power failure or other crash

if (command -v fake-hwclock >/dev/null 2>&1) ; then
  mount -o remount,rw /
  fake-hwclock save
  mount -o remount,ro /
fi
'

# add bluetooth device
# manual process


# finished & reboot
echo "Restarting in 5seconds"
echo "New hostname is pi-auto4"
sleep 5
sudo reboot