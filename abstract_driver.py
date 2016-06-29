#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 22 квіт. 2016

@author: dbe
Абстрактный драйвер
'''
import minimalmodbus
import time
import MySQLdb


class AbstractDriver(minimalmodbus.Instrument):
    '''
    classdocs
    '''
    def __init__(self, portname, slaveaddress, poll_counts, cursor):
        '''
        Constructor
        '''
        self.slaveaddress = slaveaddress;
        self.poll_counts = poll_counts
        self.cursor = cursor
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)

    def multiple_read(self, startadddres, registers):
        fail_counter = 0
        ctrl_state = False
        try: #Попробовать запихнуть в while
            ctrl_state=self.read_registers(startadddres, registers, 0x03)
        except (IOError, ValueError, TypeError):
            pass
        while not ctrl_state:
            time.sleep(0.010) 
            if fail_counter > self.poll_counts:
                break
            try:
                ctrl_state=self.read_registers(startadddres, registers, 0x03)
            except (IOError, ValueError, TypeError):
                fail_counter += 1
                #print("Failed to read from ctrl, addres=%d" % self.slaveaddress)
        if ctrl_state:
            return ctrl_state # добавить передачу счетчика ошибок 
        else:
            return False
    
    def set_onliune_to_db (self):
        set_online_q = "UPDATE ctrls SET ctrls.online=1, ctrls.last_update=NOW()\
                         WHERE ctrls.bus_id='%d'" % (self.slaveaddress)
        self.cursor.execute(set_online_q)
    
    def set_offliune_to_db (self):
        set_online_q = "UPDATE ctrls SET ctrls.online=0, ctrls.last_update=NOW()\
                         WHERE ctrls.bus_id='%d'" % (self.slaveaddress)
        self.cursor.execute(set_online_q)
        
    def log_param (self, addr, addr_type, value):
        get_value = "SELECT value FROM celse.paramlog WHERE paramlog.bus_id='%d' AND paramlog.addr='%d' AND paramlog.addr_type='%d' ORDER BY paramlog.time ASC LIMIT 1  " % (self.slaveaddress, addr, addr_type) 
        self.cursor.execute(get_value)
        last_value = self.cursor.fetchall()
        if last_value:
            if (last_value != value):
                ins_value = "INSERT INTO `paramlog` (`bus_id`, `addr`, `addr_type`, `value`, `time`) VALUES (%d, %d, %d, %f, NOW())" % (self.slaveaddress, addr, addr_type, value)
                self.cursor.execute(ins_value)
        else:
            ins_value = "INSERT INTO `paramlog` (`bus_id`, `addr`, `addr_type`, `value`, `time`) VALUES (%d, %d, %d, %f, NOW())" % (self.slaveaddress, addr, addr_type, value)
            self.cursor.execute(ins_value)    
            
if __name__ == '__main__':
    db = MySQLdb.connect("localhost","root","vertrigo","celse" )
    cursor = db.cursor()
    ctrl = AbstractDriver('/dev/ttyUSB0', 1, 3, cursor)
    ctrl_state = ctrl.multiple_read(0, 8)
    if ctrl_state:
        ctrl.set_onliune_to_db()
        ctrl.log_param(1, 1, 25)
        print "Ctrl return = %s" % ' '.join(str(i) for i in ctrl_state)
    else:
        ctrl.set_offliune_to_db()
        ctrl.log_param(1, 1, 15)
        print "NO returne - Failure"
       