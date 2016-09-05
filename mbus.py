#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 25 02 2016

@author: dbe
'''
import time
import tsens485
import hyndai_inverter
import fancoil
import domodule

import serial

import MySQLdb
from os import listdir
#import serial

if __name__ == '__main__':
    current_port_index = 0;

    def get_ttyUSB():
        files = listdir('/dev')
        ports = filter (lambda x: x.startswith('ttyUSB'), files)
        return ports

    def get_onlins(cursor):
        get_ctrls_q = "SELECT COUNT(*) FROM celse.ctrls WHERE ctrls.online ='1'"
        cursor.execute(get_ctrls_q)
        ctrls_res = cursor.fetchall()
        return ctrls_res[0]

    '''get from db ctrl's and params info'''
    db = MySQLdb.connect("localhost","root","vertrigo","celse" )
    cursor = db.cursor()
    get_ctrls_q = "SELECT bus_id, type FROM celse.ctrls"
    cursor.execute(get_ctrls_q)
    ctrls_res = cursor.fetchall()
    errors = [ 0 for i in range(256)] #Список с количествами неверных опросов
    print "ONLINE - %d" % get_onlins(cursor)
    while True:
        ports = get_ttyUSB()
        if ports :
            port = ports[current_port_index]
            for row in ctrls_res:
                bus_id = row[0];
                ctrl_t = row[1];
                get_params_q = "SELECT addr, value, direction FROM celse.parametrs WHERE parametrs.bus_id='%d'" % bus_id
                cursor.execute(get_params_q)
                param_res = cursor.fetchall()
                if param_res:
                    if ctrl_t != 2:
                        try:
                            ctrl = tsens485.Tsens485('/dev/'+port, bus_id, 10, cursor) #10 - polls_count
                        except (serial.serialutil.SerialException):
                            ctrl = False
                            break
                            #pass
                    if ctrl_t == 2:
                        try:
                            ctrl = hyndai_inverter.HyndaiInverter('/dev/'+port, bus_id, 10, cursor)
                        except (serial.serialutil.SerialException):
                            ctrl = False
                            break
                            #pass
                    if ctrl_t == 3:
                        try:
                            ctrl = fancoil.FanCoil('/dev/'+port, bus_id, 10, cursor)
                        except (serial.serialutil.SerialException):
                            ctrl = False
                            break
                    if ctrl_t == 4:
                        try:
                            ctrl = domodule.DOModule('/dev/'+port, bus_id, 10, cursor)
                        except (serial.serialutil.SerialException):
                            ctrl = False
                            break
                    if ctrl:
                        if (ctrl.synchonise() == False):
                            errors[bus_id] += 1
                            print "communication errors ctrl"+str(bus_id)+"="+str(errors[bus_id])
                            if errors[bus_id] > 5:
                                print "Set OffLine to db, ctrl "+str(bus_id)
                                errors[bus_id] = 0
                                ctrl.set_offliune_to_db
                        else:
                            errors[bus_id] = 0
                    else:
                        errors[bus_id] += 1
                        print "communication errors ctrl"+str(bus_id)+"="+str(errors[bus_id])
                        if errors[bus_id] > 5:
                            print "Set OffLine to db, ctrl "+str(bus_id)
                            errors[bus_id] = 0
                            ctrl.set_offliune_to_db

            if get_onlins(cursor) == 0:
                if current_port_index < len(ports)-1:
                    ++current_port_index
                    port = ports[current_port_index]
                    print port
                else:
                    current_port_index = 0
                    port = ports[current_port_index]
                    print port
        else:
            print "No ports available."
        time.sleep(3)
    db.close()
    pass
