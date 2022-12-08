"""
# mount file system
sudo mount -o remount,ro /
sudo mount -o remount,rw /
sudo mount --bind /home/pi/pi-auto4 /pi-auto4 -o --rw
sudo mount /pi-auto4 /home/pi/pi-auto4 -o bind,rw


# systemctl commands
sudo systemctl restart pi-auto4.service
sudo systemctl status pi-auto4.service
sudo systemctl stop pi-auto4.service
sudo systemctl start pi-auto4.service
"""


import datetime
import time

import obd, serial, subprocess, threading
import os.path

import obd
import serial
import subprocess
import threading

import variables
from at_connections import at_gps_start, at_gps_stop, at_internet_stop
from at_gps import at_get_gps_position
from db_connect import db_create_connection
from gpio import gpio_power_on, gpio_power_off
from log_write_to_text_file import log_write_to_text_file
from rest_communicate import post_to_server_thread
from temp_mon import *

# user vars
token = variables.token
auth_user_id = variables.auth_user_id
apn_var = variables.apn_var

# go to writeable dir
os.chdir('/pi-auto4')

# log_write_to_text_file('msg')
log_write_to_text_file('Program Started')

# test for database & create one if not exist
my_file = os.path.isfile("data.db")
if my_file == False:
    import db_setup
    db_setup.create_tables()
    db_setup.add_data()
    print("Created db")

# db connect
database = r"data.db"
db_file = database
conn = db_create_connection(db_file)
# get records
# db_select_all(conn)
# ser = serial.Serial(variables.serial_connection, 9600)


############################################
# bluetooth start
############################################
# sudo rfcomm bind rfcomm0 00:1D:A5:68:C3:E2
bluetooth_folder_check = os.path.isdir('/dev/rfcomm0')
if bluetooth_folder_check == False:
    subprocess.run(['sudo', 'rfcomm', 'bind', 'rfcomm0', variables.bluetooth_mac])

obd.logger.setLevel(obd.logging.DEBUG)
obd_connection = obd.OBD(portstr='/dev/rfcomm0', baudrate='115200', protocol='6')
# time.sleep(5)  # needed?


def temp_start():
    t = threading.Thread(target=measure_temp, args=())
    t.start()


def at_command(at_command):
    ser.write((at_command + "\r \n").encode())
    sleep_long()
    msg = ser.read_all()
    print(msg)


############################################
# gps start stop
############################################
def gps_start(ser):
    at_gps_start(ser)

def gps_start_app(ser, obd_connection):
    at_get_gps_position(ser, obd_connection)

def gps_stop(ser):
    at_gps_stop(ser)


############################################
# Hat turn off and on reset
############################################
def startup():
    gpio_power_on()
    sleep_long()

def restart():
    at_command('AT+CRESET')  # reset

def shutdown():
    at_command('AT+CPOF')  # power off
    # gpio_power_off()  # needed?
    # ser.close()  # needed?


############################################
# sleep long and short
############################################
def sleep_short():
    time.sleep(.5)

def sleep_long():
    time.sleep(2)


############################################
# internet start & stop
############################################
def internet_start_pon():
    result = subprocess.run(['sudo', 'pon'], capture_output=True)
    log_write_to_text_file('Internet_start pon: {0} {1}'.format(result.stdout, result.stderr))

def internet_start():
    internet_start_pon()
    result = subprocess.run(['sudo', 'pon'], capture_output=True)
    log_write_to_text_file('Internet_start: {0} {1}'.format(result.stdout, result.stderr))
    """
    # pon
    https://manpages.ubuntu.com/manpages/xenial/en/man1/pon.1.html
    
    # start connection from cmdline.. this hijacks the serial connection tho
    # sudo nano /etc/ppp/peers/provider
    # sudo nano /etc/chatscripts/gprs 

    # pon works or test sudo wvdial
    sudo pon

    # when successfully connected 
    # ping and check dns
    ping -I ppp0 google.com
    ping -I ppp0 8.8.8.8

    # see network interfaces 
    ip a

    # pipe internet through ppp0 # not currently needed
    # sudo route add -net "0.0.0.0" ppp0
    """

def internet_start_pon_thread():
    t = threading.Thread(target=internet_start_pon, args=())
    t.start()

def internet_stop_poff():
    result = subprocess.run(['sudo', 'poff'], capture_output=True)
    log_write_to_text_file('Internet_start: {0} {1}'.format(result.stdout, result.stderr))

def internet_stop():
    internet_stop_poff()


###################################################
# Updates
###################################################
def update_check():
    result = subprocess.run(['sudo', 'sh', './git_update.sh'], capture_output=True)
    print('Internet_start: {0} {1}'.format(result.stdout, result.stderr))
    log_write_to_text_file('Internet_start: {0} {1}'.format(result.stdout, result.stderr))


def update_datetime_thread():
    def update_datetime():
        print('before update_datetime: ', datetime.datetime.now())
        log_write_to_text_file('before update_datetime: {0}'.format(datetime.datetime.now()))
        subprocess.run(['sudo', 'mount', '-o', 'remount,rw', '/'])
        subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'True'])
        subprocess.run(['sudo', 'mount', '-o', 'remount,ro', '/', '-force'])
        print('after update_datetime: ', datetime.datetime.now())
        log_write_to_text_file('after update_datetime: {0}'.format(datetime.datetime.now()))
    update_datetime()


###################################################
# Main
###################################################
if __name__ == '__main__':
    temp_start()
    ser = serial.Serial(variables.serial_connection, 115200)
    at_command('AT+CGPSAUTO=1')  # gps set to auto start
    # gps_start(ser)  # needed?
    internet_start_pon_thread()
    # ser = serial.Serial(variables.serial_connection, 9600)
    update_datetime_thread()
    update_check()
    post_to_server_thread(conn=conn, token=token, auth_user_id=auth_user_id)
    time.sleep(30)  # testing bonus time for letting the app/pi start
    ser_gps = serial.Serial(variables.gps_device, 115200)
    gps_start_app(ser_gps, obd_connection, conn, token, auth_user_id)
