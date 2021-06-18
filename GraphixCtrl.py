#!/usr/bin/python3 -u
# coding: utf8
# GraphixCtrl
from tango import DevState, AttrWriteType, DispLevel
from tango.server import Device, attribute, command, device_property
import time
import sys
import serial


class GraphixCtrl(Device):
    # device properties
    Port = device_property(
        dtype="str",
        default_value="/dev/ttyGraphix",
    )

    Baudrate = device_property(
        dtype="int",
        default_value=38400,
    )

    # device attributes
    hv_sv = attribute(
        dtype='str',
        access=AttrWriteType.READ,
        label='Version',
    )

    sn = attribute(
        dtype='str',
        access=AttrWriteType.READ,
        label='Serial number',
    )

    pn = attribute(
        dtype='str',
        access=AttrWriteType.READ,
        label='Part number',
    )

    display_unit = attribute(
        dtype='str',
        access=AttrWriteType.READ,
        label='Display unit',
    )

    nb_channels = attribute(
        dtype='int',
        access=AttrWriteType.READ,
        label='Number of channels',
    )

    # definition some constants
    __EOT = chr(4)  # end character
    __SI = chr(0x0f)  # read detection
    __SO = chr(0x0e)  # write detection
    __ACK = chr(6)  # parameter value accepted
    __NACK = chr(0x15)  # parameter value not accepted

    def init_device(self):
        self.info_stream("init_device()")
        Device.init_device(self)
        self.set_state(DevState.INIT)

        try:
            # configure serial
            self.info_stream("Connection on port {:s} with baudrate {:d}".format(self.Port, self.Baudrate))
            self.serial = serial.Serial(self.Port, baudrate=self.Baudrate, timeout=0)
            if self.serial.is_open:
                self.serial.close()
            self.serial.open()
            self.__hv_sv = self.read('5;1')
            self.__sn = self.read('5;2')
            self.__pn = self.read('5;3')
            self.__nb_chanels = int(self.read('5;8'))
            self.__display_unit = self.read('5;4')
            self.info_stream("Success on instrument:\nhardware and software version: {:s}\nserial number: {:s}\npart number: {:s}".format(self.__hv_sv, self.__sn, self.__pn))
            self.set_state(DevState.ON)
        except:
            self.info_stream("Cannot connect!")
            self.set_state(DevState.OFF)

    def delete_device(self):
        if self.serial.is_open:
            self.serial.close()
            self.info_stream("Closed connection on port {:s}".format(self.Port))

    def read_hv_sv(self):
        return self.__hv_sv

    def read_sn(self):
        return self.__sn

    def read_pn(self):
        return self.__pn

    def read_display_unit(self):
        return self.__display_unit

    def read_nb_channels(self):
        return self.__nb_chanels

    @command(dtype_in=str, dtype_out=str)
    def write(self, cmd):
        cmd = '{:s}{:s} '.format(self.__SO, cmd)
        return self.query(cmd)

    @command(dtype_in=str, dtype_out=str)
    def read(self, cmd):
        cmd = '{:s}{:s}'.format(self.__SI, cmd)
        return self.query(cmd)
    
    def query(self, cmd):
        self.debug_stream("write command: {:s}".format(cmd))
        cmd_crc = cmd + calc_crc(cmd) + self.__EOT
        self.serial.write(cmd_crc.encode("latin1"))
        self.serial.flush()
        time.sleep(0.02)  # 20ms wait time
        res = self.serial.readline().decode("latin1")
        self.debug_stream("read response: {:s}".format(res))
        if self.__ACK in res:
            response = res.lstrip(self.__ACK).rstrip(self.__EOT)[:-1]
            if len(response) == 0:  # successful write
                return "0"
            else:  # successful read
                return response
        else:  # error
            return res.lstrip(self.__NACK).rstrip(self.__EOT)[:-1]


def calc_crc(cmd):
    bytecmd = bytes(cmd, 'utf-8')
    s = 0
    for byte in bytecmd:
        s += int(byte)
    crc = 255 - (s%256)
    if crc < 32:
        crc += 32
    return chr(crc)


if __name__ == "__main__":
    GraphixCtrl.run_server()
