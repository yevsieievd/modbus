#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 25 02 2016

@author: dbe
'''
import time
import tsens485
import hyndai_inverter

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
                        ctrl = tsens485.Tsens485('/dev/'+port, bus_id, 3, cursor) #3 - polls_count
                        ctrl.synchonise()
                    if ctrl_t == 2: 
                        ctrl = hyndai_inverter.HyndaiInverter('/dev/'+port, bus_id, 3, cursor)
                        ctrl.synchonise()
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
