#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 21 07  2016

@author: dbe
'''
import abstract_driver
import MySQLdb

class DOModule(abstract_driver.AbstractDriver):
    '''
    classdocs
    '''
    def __init__(self, portname, slaveaddress, poll_counts, cursor):
#        self.slaveaddress = slaveaddress;
#        self.poll_counts = poll_counts
#        self.cursor = cursor
        abstract_driver.AbstractDriver.__init__(self, portname, slaveaddress, poll_counts, cursor)
        self.serial.baudrate = 19200

        '''
        Constructor
        '''
    def get_status(self):
        ctrl_state=self.multiple_read(0, 19)
        if ctrl_state:
            return ctrl_state # добавить передачу счетчика ошибок
        else:
            return False

    def synchonise(self):
        ctrl_state=self.get_status()
        if ctrl_state:
            self.set_onliune_to_db()
            get_params_q = "SELECT addr, value, direction, to_log FROM celse.parametrs WHERE parametrs.bus_id='%d'" % self.slaveaddress
            self.cursor.execute(get_params_q)
            param_res = self.cursor.fetchall()
            if param_res:
                print ctrl_state
                for p_row in param_res:
                    p_addr = int(str(p_row[0]))
                    p_value = float(str(p_row[1]))
                    p_direction = int(str(p_row[2]))
                    to_log = int(str(p_row[3]))
                    #print "p_addr=%d p_value=%s p_direction=%d" % (p_addr, p_value, p_direction)
                    if p_value != ctrl_state[p_addr]:
                        if p_direction == 1: #To the database
                        #    if p_addr == 3 and ctrl_state[0] > 150:
                        #        set_param_q = "UPDATE parametrs SET value=%f, last_update=NOW() WHERE bus_id='%d' AND addr='%d'" % (1, self.slaveaddress, p_addr)
                        #    else:
                            set_param_q = "UPDATE parametrs SET value=%f, last_update=NOW() WHERE bus_id='%d' AND addr='%d'" % (ctrl_state[p_addr], self.slaveaddress, p_addr)
                            self.cursor.execute(set_param_q)
                            if to_log == 1:
                                self.log_param (p_addr, 1, ctrl_state[p_addr])
                        else: #To the ctrl
                            value_to_set = int(p_value)
                            try: #Попробовать запихнуть в while
                                self.write_register(p_addr, value_to_set, numberOfDecimals=0, functioncode=6, signed=False)
                            except (IOError, ValueError, TypeError):
                                pass
            return True
        else:
            self.set_offliune_to_db()
            print("Failed to read from DOModule, addres=%d" % self.slaveaddress)
            return False

if __name__ == '__main__':
    db = MySQLdb.connect("localhost","root","vertrigo","celse" )
    cursor = db.cursor()
    domodule = DOModule('/dev/ttyS0', 1, 3, cursor)
    state = domodule.get_status()
    if state:
        print "DOModule = %s" % ' '.join(str(i) for i in domodule.get_status())
        tsens.set_onliune_to_db()
    else:
        tsens.set_offliune_to_db()
        print "NO returne - Failure"


#       try:
#           return self.read_registers(0, 8, 3)
#       except (IOError, ValueError, TypeError):
#           print("Failed to read from Tsens485, addres=%d" % self.slaveaddress)
