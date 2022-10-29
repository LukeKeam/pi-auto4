"""
gps

"""

import datetime
import time

import serial

from db_input import db_send_to_local_db
import threading
from at_connections import at_gps_stop, at_gps_start, at_internet_start, at_internet_stop, at_test_device_connection
from gpio import gpio_power_on, gpio_power_off
from bluetooth_connect import obd_data, obd_connection_test


# add to db via thread, otherwise screws up time
def send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert):
    t = threading.Thread(target=db_send_to_local_db, args=(utc, latitude, longitude, speed, vehicle_move_stop,
                                                  vehicle_move_start, alert))
    t.start()


def obd_data_thread(utc, obd_connection):
    t = threading.Thread(target=obd_data, args=(utc, obd_connection))
    t.start()


# have ser here?
ser = serial.Serial('/dev/ttyUSB1', 115200)


# namea output stream
def at_get_gps_position(ser, obd_connection):
    gps_start = True
    print('Start GPS session...')
    date_now = datetime.datetime.now()
    six_min = date_now + datetime.timedelta(minutes=6)
    sixty_mins = date_now + datetime.timedelta(minutes=60)
    stopped = False
    stopped_counter = 0
    vehicle_move_stop = 0
    vehicle_move_start = 0
    alert = 0
    speed_alert_speed = 103
    speed_alert_counter = 0
    date_now_plus_one = date_now + datetime.timedelta(seconds=1)
    date_now_plus_two = date_now + datetime.timedelta(seconds=2)
    stopped_counter_bool = False
    obd_counter = 0
    obd_connection_bool_false_counter = 0
    obd_connection_bool = False
    i = 0
    while gps_start:
        line = serial.Serial.readline(ser)
        GPRMC_test = str(line).startswith("b'$GPRMC")
        if GPRMC_test == True:
            print('')
            print('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
            date_now = datetime.datetime.now()
            data = line   # previously used ser.readline()
            # print('data', data)
            utc = 0
            latitude = 0
            longitude = 0
            speed = 0
            try:
                print('if str(data) != "b":')
                # set data vars
                split = str(data).split(',')
                time = split[1]
                date_str = split[9]
                date_str = datetime.datetime.strptime(str(date_str), '%d%m%y')
                date = datetime.datetime.strftime(date_str, '%Y%m%d')
                utc = date + time
                latitude = split[3]
                longitude = split[5]
                # altitude = split[5]
                speed = split[7]
                if not speed:
                    speed = 0
                print('utc', utc, 'latitude', latitude, 'longitude', longitude, 'speed', speed, 'time', time,
                      'date', date)
                print('')
            except:
                pass
            if float(speed) >= speed_alert_speed:
                speed_counter_initial = date_now
                date_now_plus_one = date_now + datetime.timedelta(seconds=1)
                date_now_plus_two = date_now + datetime.timedelta(seconds=2)
                if date_now >= date_now_plus_one and date_now <= date_now_plus_two:
                    speed_alert_counter = speed_alert_counter + 1
                    if speed_alert_counter >= 3:
                        alert = 1
                        # post to database
                        send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert)
                # reset counter??? this and idea... or
                if date_now != date_now_plus_one:
                    speed_alert_counter = 0
                    alert = 0
            # start
            if float(speed) > 3:
                # start speed
                if stopped == True:
                    vehicle_move_start = 1
                    vehicle_move_stop = 0
                    send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert)
                    vehicle_move_start = 0
                    stopped = False
            # stopped_function
            vehicle_move_stop = 0
            if float(speed) < 3:
                stopped_counter_initial = date_now
                # print('date_now', date_now, 'first', date_now_plus_one, date_now_plus_two)
                if date_now >= date_now_plus_one and date_now <= date_now_plus_two:
                    print('###############################################')
                    print('datenow plus one and two, stopped counter:', stopped_counter)
                    if stopped_counter_bool == False:
                        stopped_counter_bool = True
                        stopped_counter_utc = utc
                        stopped_counter_latitude = latitude
                        stopped_counter_longitude = longitude
                        stopped_counter_speed = speed
                    stopped_counter = stopped_counter + 1
                    if stopped_counter >= 241:
                        print('stopped counter', stopped_counter_initial)
                        vehicle_move_stop = 1
                        stopped = 1
                        # sixty min breaks?
                            # store current data
                        # reset initial
                        stopped_counter_initial = date_now
                    # send original stop to database then start 60 min loop
                    if stopped_counter == 300:
                        print('stopped counter and sent to database')
                        # todo. need to add orignal stop, testing
                        utc = stopped_counter_utc
                        latitude = stopped_counter_latitude
                        longitude = stopped_counter_longitude
                        speed = stopped_counter_speed
                        vehicle_move_stop = 1
                        send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert)
                        vehicle_move_stop = 0
                    print('')
                # start & reset counter?
                if date_now >= date_now_plus_two:
                    print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
                    print('Start: if date_now >= date_now_plus_two:')
                    stopped_counter = 0
                    vehicle_move_stop = 0
                    stopped = 0
                    print('t')
                # re do counters?
                date_now_plus_one = stopped_counter_initial + datetime.timedelta(seconds=1)
                date_now_plus_two = stopped_counter_initial + datetime.timedelta(seconds=2)
            # sixty mins and stopped
            if date_now >= six_min and stopped:
                print('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
                print('sixty mins')
                vehicle_move_stop = 1
                send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert)
                vehicle_move_stop = 0
                six_min = date_now + datetime.timedelta(minutes=6)
                #sixty_mins = date_now + datetime.timedelta(minutes=60)
            # if date_now >= six_min and not stopped:
            if not stopped:
                print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')
                print('six min store stuff:', six_min)
                # six_min = date_now + datetime.timedelta(minutes=6)
                send_to_db(utc, latitude, longitude, speed, vehicle_move_stop, vehicle_move_start, alert)
            # if no data then sleep
            if not data:
                print('if not data:', date_now)
            if ',,' not in str(data):
                print('if ,, not in str(data):', date_now)
            if data:
                # send data testing
                i = i + 1
                print('')
                print('int send data:', i)
                if i == 100:
                    print('100')
                if i >= 101:
                    print('101')
                    i = 0
            # run bluetooth here, every second
            try:
                print("obd_counter", obd_counter)
                if obd_connection_bool == False and obd_counter > 60 and obd_connection_bool_false_counter < 10:
                    obd_connection_test(obd_connection)
                    obd_connection_bool_false_counter = obd_connection_bool_false_counter + 1
                    obd_counter = 0
                if obd_connection_bool == False and obd_counter > 900 and obd_connection_bool_false_counter > 10:
                    obd_connection_test(obd_connection)
                    obd_counter = 0
                if obd_connection_bool == True:
                    obd_data_thread(utc, obd_connection)
                obd_counter = obd_counter + 1
            except:
                print('except')

