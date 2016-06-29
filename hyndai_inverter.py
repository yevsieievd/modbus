#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on 19 бер. 2016

@author: dbe
'''
import MySQLdb
import abstract_driver
import time



class HyndaiInverter( abstract_driver.AbstractDriver ):
    """Instrument class for Hyndai Inverter.

    Args:
        * portname (str): port name
        * slaveaddress (int): slave address in the range 1 to 247

    """
    def __init__(self, portname, slaveaddress, poll_counts, cursor):
        self.poll_counts = poll_counts
        self.cursor = cursor
        self.slaveaddress = slaveaddress
        self.sp_friq_addr_read = 0x0201
        self.sp_friq_addr_wright = 0x04
        self.output_friq_addr = 0x0101
        abstract_driver.AbstractDriver.__init__(self, portname, slaveaddress, poll_counts, cursor)
        self.serial.baudrate = 9600
        self.serial.bytesize = 8
    #    self.serial.parity = self.serial.PARITY_NONE
        self.serial.stopbits = 1
        self.serial.timeout = 0.05
    
    def get_out_friq(self): #Получить величину выходной частоты из частотника        
        output_friq = self.multiple_read(self.output_friq_addr, 1)#/100
        if output_friq:
            return output_friq[0]/100
        else: 
            return -1
        
    def get_friq_sp_ctrl(self): #Получить уставку частоты из частотника
        try: 
            out = self.read_registers(self.sp_friq_addr_read, 1, 0x03)
            return out[0]/100
        except (IOError, ValueError, TypeError):
            print("Failed to read from HyndaiInverter, addres=%d" % self.slaveaddress)
            return -1
        
    def set_friq_sp_ctrl(self, value): 
        self.write_register(self.sp_friq_addr_wright, int(value*100), numberOfDecimals=0, functioncode=0x06, signed=False) 
            
    def set_out_friq_to_db (self, value):
        set_friq_q = "UPDATE parametrs SET parametrs.value=%f, parametrs.last_update=NOW() WHERE parametrs.bus_id='%d' AND parametrs.addr='%d'" % (value, self.slaveaddress, self.output_friq_addr)
        self.cursor.execute(set_friq_q)
    
    def get_friq_sp_db(self): #Получить уставку частоты из БД
        get_params_q = "SELECT value direction FROM celse.parametrs WHERE parametrs.bus_id='%d' AND parametrs.addr='%d'" % (self.slaveaddress, self.sp_friq_addr_read)
        self.cursor.execute(get_params_q)
        sp_friq_in = self.cursor.fetchall()
        return float(str(sp_friq_in[0][0]))

    def get_friq_sp_iface_db(self): #Получить уставку частоты из БД
        get_params_q = "SELECT value direction FROM celse.parametrs WHERE parametrs.bus_id='%d' AND parametrs.addr='%d'" % (self.slaveaddress, self.sp_friq_addr_wright)
        self.cursor.execute(get_params_q)
        sp_friq_out = self.cursor.fetchall()
        return float(str(sp_friq_out[0][0]))

    def set_friq_all_db(self, value):
        set_friq_q = "UPDATE parametrs SET value=%f, last_update=NOW() WHERE bus_id='%d' AND (addr='%d' OR addr='%d')" % (value, self.slaveaddress, self.sp_friq_addr_read, self.sp_friq_addr_wright)
        self.cursor.execute(set_friq_q)
        
                   
    def set_friq(self, value):
        """Set output friquency ."""
        return self.write_register(0x0004, int(value*100), numberOfDecimals=0, functioncode=6, signed=False) > 0
    def stop(self):
        """Stop."""
        return self.write_register(0x0002, 0x0000, numberOfDecimals=0, functioncode=6, signed=False) > 0
    def run_fwd(self):
        """Run forward."""
        return self.write_register(0x0002, 0x0001, numberOfDecimals=0, functioncode=6, signed=False)
    def run_rev(self):
        """Run revers"""
        return self.write_register(0x0002, 0x0002, numberOfDecimals=0, functioncode=6, signed=False) > 0
    def reset(self):
        """"""
        return self.write_register(0x0002, 0x0004, numberOfDecimals=0, functioncode=6, signed=False) > 0
    def get_trip(self, addr):
        try:
            info = self.read_registers(addr, 1, 0x03)
            print ("Trip info addres=%d : %d" % addr, info)
            return info
        except (IOError, ValueError, TypeError):
            print("Failed to read from HyndaiInverter, addres=%d" % addr)
            return False   
    def get_trip_info(self):
        #return self.get_trip(addr = 0x010d)
        return self.read_registers(0x010d, 1, 0x03)
    def get_trip_prev1(self):
        #return self.get_trip(addr = 0x0111)
        return self.read_registers(0x0111, 1, 0x03)        
    def get_trip_prev2(self):
        #return self.get_trip(addr = 0x0115)
        return self.read_registers(0x0115, 1, 0x03)
    def get_trip_prev3(self):
        #return self.get_trip(addr = 0x0119)
        return self.read_registers(0x0119, 1, 0x03)
    def get_trip_count (self):
        #return self.get_trip(addr = 0x011D)
        return self.read_registers(0x011D, 1, 0x03)
    
    def upd_trips(self):
        get_params_q = "SELECT value, addr FROM celse.parametrs WHERE parametrs.bus_id='%d' AND parametrs.addr>'268' AND parametrs.addr<'286'" % (self.slaveaddress)
        self.cursor.execute(get_params_q)
        trips = self.cursor.fetchall()
        for trip in trips:
            value = int((trip[0]))
            addr = int((trip[1]))
            ctrl_val = self.read_registers(addr, 1, 0x03)
            #print "Trip [%d]=%d" % (addr, ctrl_val[0]) 
            if ctrl_val[0] != value:
                set_friq_q = "UPDATE parametrs SET value=%f, last_update=NOW() WHERE bus_id='%d' AND addr='%d'" % (ctrl_val[0], self.slaveaddress, addr)
            #    print set_friq_q 
                self.cursor.execute(set_friq_q)
            else:
            #    print "Trip is Uptodate"
                pass    
                
    def set_mode(self):
        get_params_q = "SELECT value, addr FROM celse.parametrs WHERE parametrs.bus_id='%d' AND parametrs.addr='2' AND parametrs.to_set='1'" % (self.slaveaddress)
        self.cursor.execute(get_params_q)
        mode = self.cursor.fetchall()
        if mode:
         #   print int(mode[0][0])
            self.write_register(0x0002, int(mode[0][0]), numberOfDecimals=0, functioncode=6, signed=False)
            set_to_set = "UPDATE parametrs SET to_set='0', last_update=NOW() WHERE bus_id='%d' AND addr='2'" % (self.slaveaddress)
            self.cursor.execute(set_to_set)
                    
             
    
    def synchonise(self):
        #получение и апдэйт выходной частоты
        output_friq = self.get_out_friq()
        if output_friq >= 0:
            #print output_friq
            self.set_onliune_to_db()
            self.set_out_friq_to_db(output_friq)
            #манипуляции с уставкой частоты: елсли изметения на частотнике - то в базу если с интерфейса - то в контроллер
            sp_friq = self.get_friq_sp_ctrl()
            sp_friq_db = self.get_friq_sp_db()
            sp_friq_iface_db = self.get_friq_sp_iface_db()
            if sp_friq != sp_friq_db: #Значит засетили на частотнике - записать в оба параметра в БД
                self.set_friq_all_db(sp_friq)
            else:
                if sp_friq_iface_db != sp_friq: #Значит засетили с интерфейса - записать в частотик
                    self.set_friq_sp_ctrl(sp_friq_iface_db)
            self.upd_trips()
            self.set_mode()
        else:
            print ("Hyndai - OFFLINE") 
            self.set_offliune_to_db()    
        return 

if __name__ == '__main__':
    db = MySQLdb.connect("localhost","root","vertrigo","celse" )
    cursor = db.cursor()
    invertor = HyndaiInverter('/dev/ttyUSB0', 8, 3, cursor)
    #state = invertor.get_out_friq() #+
    state = invertor.get_friq_sp_ctrl() #+ 
    #state = invertor.set_friq_sp_ctrl(40) #+
    #state = invertor.stop()#+
    #state = invertor.run_fwd()#+
    
    #state = invertor.reset()#+
    #state = invertor.get_trip_info()    #+
    #state = invertor.get_trip_prev1()    #+  
    #state = invertor.get_trip_prev2()    #+
    #state = invertor.get_trip_prev3()    #+
    #state = invertor.get_trip_count()    #+
    if state: 
        print "Output friq:"
        print state
        invertor.set_onliune_to_db()
    else:
        invertor.set_offliune_to_db()
        print "NO returne - Failure"        

    
    
    
    