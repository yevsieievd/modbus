#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 21 07  2016

@author: dbe
'''
import abstract_driver
import MySQLdb

class FanCoil(abstract_driver.AbstractDriver):
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
        ctrl_state=self.multiple_read(0, 15)
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
                ctrl_state[0] = (float(ctrl_state[0])/100)
                ctrl_state[4] = (float(ctrl_state[4])/100)
                ctrl_state[5] = (float(ctrl_state[5])/100)
                if ctrl_state[2] == 0:
                    for p_row in param_res:
                        if p_row[0] == 4:
                            ctrl_state[7] = (float(ctrl_state[7])/100) + float(str(p_row[1]))
                if ctrl_state[2] == 1:
                    for p_row in param_res:
                        if p_row[0] == 5:
                            ctrl_state[7] = (float(ctrl_state[7])/100) + float(str(p_row[1]))
                ds_alarm = ctrl_state[6]
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
                            if p_addr == 0 or p_addr == 4 or p_addr == 5:
                                value_to_set = int(p_value*100)
                            else:
                                value_to_set = int(p_value)

                            if ds_alarm == 0 or p_addr != 1: #Датчик температуры наместе
                                self.write_reg(p_addr, value_to_set)
                            elif ds_alarm == 1 and p_addr == 1 and p_value == 1:
                                self.write_reg(p_addr, 0)
                            elif ds_alarm == 1 and p_addr == 1 and p_value != 1:
                                self.write_reg(p_addr, value_to_set)


            return True
        else:
            self.set_offliune_to_db()
            print("Failed to read from FanCoil, addres=%d" % self.slaveaddress)
            return False

if __name__ == '__main__':
    db = MySQLdb.connect("localhost","root","vertrigo","celse" )
    cursor = db.cursor()
    for addr in range(1, 32):
        fcoil = FanCoil('/dev/ttyUSB0', addr, 3, cursor)
        state = fcoil.get_status()
        if state:
            print "Addres %s returne [ OK! ]" % addr
            print "FanCoil = %s" % ' '.join(str(i) for i in fcoil.get_status())
            #fcoil.set_onliune_to_db()
        else:
            #fcoil.set_offliune_to_db()
            print "Addres %s - [ Failure! ]" % addr


#       try:
#           return self.read_registers(0, 8, 3)
#       except (IOError, ValueError, TypeError):
#           print("Failed to read from Tsens485, addres=%d" % self.slaveaddress)
