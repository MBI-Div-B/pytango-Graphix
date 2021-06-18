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
        default_value="38400",
    )

    Address_RS489 = device_property(
        dtype="int",
        default_value="-1",
    )

    # definition some constants
    __EOT = chr(4)  # end character
    __SI = chr(0x0f)  # read detection
    __SO = chr(0x0e)  # write detection
    __ACK = chr(6)  # parameter value accepted
    __NACK = chr(0x15)  # parameter value not accepted

    def init_device(self):
        self.set_state(DevState.INIT)

        try:
            # configure serial
            self.info_stream("Connection on port {:s} with baudrate {:d}".format(self.Port, self.Baudrate))
            self.serial = serial.Serial(self.Port, baudrate=self.Baudrate, timeout=0)
            if self.serial.is_open():
                self.serial.close()
            self.serial.open()
            self.info_stream("Success")
            self.set_state(DevState.ON)
        except:
            self.info_stream("Cannot connect!")
            self.set_state(DevState.OFF)

        self.info_stream("port: {:s}".format(self.Port))
        self.info_stream("baudrate = {:s}".format(self.Baudrate))

        # open serial port
        self.open()

    def delete_device(self):
        if self.serial.is_open():
            self.serial.close()
            self.info_stream("Closed connection on port {:s}".format(self.Port))

    @command(dtype_in=str, dtype_out=str)
    def write_read(self, cmd):
        cmd = self.__STX + cmd + self.__ETX
        self.debug_stream("write command: {:s}".format(cmd))
        self.serial.write(cmd.encode("utf-8"))
        self.serial.flush()
        time.sleep(0.02)  # 20ms wait time
        res = self.serial.readline().decode("utf-8")
        self.debug_stream("read response: {:s}".format(res))
        if self.__ACK in res:
            return res.lstrip(self.__STX).lstrip(self.__ACK).rstrip(self.__ETX)
        else:
            # no acknowledgment in response
            return self.__NACK


if __name__ == "__main__":
    GraphixCtrl.run_server()
