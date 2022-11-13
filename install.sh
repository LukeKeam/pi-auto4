#!/bin/bash
: '
have installed and working os, you will not need a gui!
Raspberry Pi OS Lite 32bit os https://www.raspberrypi.com/software/operating-systems/
once have ssh connection to pi
curl -LJO https://raw.githubusercontent.com/LukeKeam/pi-auto4/master/install.sh && sudo bash ./install.sh
'

# intro
echo ""
echo ""
echo ""
echo ""
echo "Thanks for choosing pi-auto4 from https://fleet-track.org"
echo ""
echo "This is in testing continue at own risk, press ENTER to continue or ctrl+c to exit"
read testing

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

[Unit]
Description=pi-auto4
After=multi-user.target

[Service]
Type=idle
WorkingDirectory=/pi-auto4
ExecStart=/bin/bash -c "python3 /pi-auto4/main.py"

[Install]
WantedBy=multi-user.target'
# line removed ExecStart=/bin/bash -c "mount -o remount,rw /pi-auto4 && python3 /pi-auto4/main.py"

echo "$append_line" | sudo tee /lib/systemd/system/pi-auto4.service # need to make other lines ro
sudo systemctl enable pi-auto4.service


################################################################################################
echo "poops out here and in testing/dev"
################################################################################################
read experimental
echo "setup internet"
# edit sudo nano /etc/ppp/peers/provider


echo "Making OS read only"
# https://github.com/vladbabii/raspberry_os_buster_read_only_fs
# https://hallard.me/raspberry-pi-read-only/
# remove stuff
sudo apt-get remove --purge triggerhappy logrotate dphys-swapfile -y
# sudo apt-get autoremove --purge -y  # this needed?

# sys log
sudo apt-get install busybox-syslogd -y
sudo dpkg --purge rsyslog

# sudo nano /boot/cmdline.txt # add fastboot noswap ro
# add to same line?
echo "fastboot noswap ro" | sudo tee -a /boot/cmdline.txt # not on the same line though

# Move some system files to temp filesystem
sudo rm -rf /var/lib/dhcp/ /var/lib/dhcpcd5 /var/run /var/spool /var/lock /etc/resolv.conf
sudo ln -s /tmp /var/lib/dhcp
sudo ln -s /tmp /var/lib/dhcpcd5
sudo ln -s /tmp /var/run
sudo ln -s /tmp /var/spool
sudo ln -s /tmp /var/lock
sudo touch /tmp/dhcpcd.resolv.conf
sudo ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf

# move random-seed
sudo rm /var/lib/systemd/random-seed &&
sudo ln -s /tmp/random-seed /var/lib/systemd/random-seed
# edit random seed service
sudo sed '/^RemainAfterExit=.*/a ExecStartPre=/bin/echo "" >/tmp/random-seed' /lib/systemd/system/systemd-random-seed.service

# reload systemctl
sudo systemctl daemon-reload


# make os read only maybe a sed like above
# /home/pi/pi-auto     /pi-auto        ext4    defaults,bind,rw     0       0
append_line="tmpfs        /tmp            tmpfs   nosuid,nodev         0       0
tmpfs        /var/log        tmpfs   nosuid,nodev         0       0
tmpfs        /var/tmp        tmpfs   nosuid,nodev         0       0"
echo "$append_line" | sudo tee -a /etc/fstab # need to make other lines ro


# remove startup scripts
sudo systemctl disable bootlogs
sudo systemctl disable console-setup


read "May need to check what device eg /dev/ttyUSB1 is outputting NMEA data"
read "need to go to rapid-config > interface > no then yes"

echo "Update UART "
# add line to config enable uart # # raspi-config for serial???
append_line="enable_uart=1"
echo "$append_line" | sudo tee -a /boot/config.txt


# this was a bug when trying to make the filesystem read only and running sudo pon
sudo mkdir /var/lockfile/

# add bluetooth device
echo ""
echo "Bluetooth device can be added to variables.py"


# finished & reboot
echo ""
echo ""
echo "#############################"
echo "Restarting in 5seconds"
echo ""
echo "New hostname is pi-auto4"
sleep 5
sudo reboot