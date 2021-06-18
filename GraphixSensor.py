#!/usr/bin/python3 -u
# coding: utf8
# GraphixSensor
from tango import DevFailed, AttrWriteType, DevState, DeviceProxy, DispLevel
from tango.server import device_property
from tango.server import Device, attribute, command

class GraphixSensor(Device):
    # device properties
    CtrlDevice = device_property(
        dtype="str", default_value="domain/family/member"
    )

    Channel = device_property(
        dtype="int"
    )

    # device attributes
    name = attribute(
        dtype="str",
        label="Name",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    sensor_type = attribute(
        dtype="str",
        label="Type",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    pressure = attribute(
        dtype="float",
        label="Pressure",
        format="%6.2g",
        access=AttrWriteType.READ,
        display_level=DispLevel.OPERATOR,
    )

    def init_device(self):
        self.info_stream("init_device()")
        Device.init_device(self)
        self.set_state(DevState.INIT)

        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream("Connected to ctrl. device: {:s}".format(self.CtrlDevice))
            self.set_state(DevState.ON)
        except DevFailed as df:
            self.error_stream("Failed to create proxy to {:s}".format(self.CtrlDevice))
            self.set_state(DevState.OFF)

        self.__sensor_type = self.read(4)
        self.__name = self.read(5)
        self.info_stream("Sensor {:s} of type {:s}".format(self.__name, self.__sensor_type))

        ac3 = self.get_attribute_config_3([b"pressure"])
        ac3[0].unit = self.ctrl.display_unit.encode("utf-8")
        self.set_attribute_config_3(ac3)

    def delete_device(self):
        self.set_state(DevState.OFF)

    # attribute read/write methods
    def read_name(self):
        return self.__name

    def read_sensor_type(self):
        return self.__sensor_type

    def read_pressure(self):
        return float(self.read(29))

    @command(dtype_in=str)
    def set_name(self, name):
        if self.write(5, name) == "0":
            self.__name = name

    def read(self, parameter):
        return self.ctrl.read("{:d};{:d}".format(self.Channel, parameter))

    def write(self, parameter, value):
        return self.ctrl.write("{:d};{:d};{:s}".format(self.Channel, parameter, value))

if __name__ == "__main__":
    GraphixSensor.run_server()
