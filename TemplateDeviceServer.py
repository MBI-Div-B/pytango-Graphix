#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (C) 2020  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: Luca Barbera / Email: barbera@mbi-berlin.de


from tango import AttrWriteType, DevState, DebugIt, DispLevel
from tango.server import Device, attribute, command, device_property

# import the drivers you will use


class TemplateDeviceServer(Device):
    '''
    This docstring should describe your Tango Class and optionally
    what it depends on (drivers etc).
    '''


# ------ Attributes ------ #

    humidity = attribute(label='Humidity',
                         dtype=float,
                         access=AttrWriteType.READ,
                         doc='Example for an attribute that can only be read.')

    # optionally use fget/fset to point to read and write functions.
    # Default is "read_temperature"/"write_temperature".
    # Added some optional attribute properties.
    temperature = attribute(label='Temperature',
                            fget='get_temperature',
                            dtype=float,
                            access=AttrWriteType.READ_WRITE,
                            display_level=DispLevel.EXPERT,
                            min_value=-273.15,
                            min_alarm=-100,
                            max_alarm=100,
                            min_warning=-50,
                            max_warning=50,
                            unit='C',
                            format="8.4f",
                            doc='Attribute that can be read/written.')


# ------ Device Properties ------ #
    # device_properties will be set once per family-member and usually -
    # contain serial numbers or a certain port-ID that needs to be set once -
    # and will not change while the server is running.

    port = device_property(dtype=int, default_value=10000)

# ------ default functions that are inherited from parent "Device" ------ #
    def init_device(self):
        Device.init_device(self)
        self.info_stream('Connection established')  # prints this line while -
        # in logging mode "info" or lower
        self.set_state(DevState.ON)

        # here you could initiate first contact to the hardware (driver)

        self.__temp = 0  # declaring values for the attributes if needed
        self.__humid = 0

    def delete_device(self):
        self.set_state(DevState.OFF)
        self.error_stream('A device was deleted!')  # prints this line while -
        # in logging mode "error" or lower.

    # define what is executed when Tango checks for the state.
    # Here you could inquire the state of the hardware and not just -
    # (as it is in default) of the TDS.
    # Default returns state but also sets state from ON to ALARM if -
    # some attribute alarm limits are surpassed.
    def dev_state(self):
        # possible pseudo code:
        # if hardware-state and TDS-state is ON:
        #   return DevState.ON
        # else:
        #   return DevState.FAULT
        return DevState

    def always_executed_hook(self):
        # a method that is executed continuously and by default does nothing.
        # if you want smth done polled/continuously, put it in this method.
        # check connection to hardware or whether status is acceptable etc.
        pass

# ------ Read/Write functions ------ #
    def read_humidity(self):  # this is default to read humidity
        return self.__humid  # returns the value of the "humidity" attr.

    def get_temperature(self):  # this was set by fget in attribute declaration
        return self.__temp

    def write_temperature(self, value):
        # possibly execute some function here to talk to the hardware -
        # (e.g. set temperature with a thermostat)
        self.__temp = value  # update the declared server value of the attr.

# ------ Internal Methods ------ #
    # method that works with multiple input parameters only "inside" this code

    def internal_method(self, param1, param2):
        # do something with param1, param2
        pass


# ------ COMMANDS ------ #

    @DebugIt()  # let the execution of this command be logged in debugging mode
    @command()  # make method executable through the client -
    # (as opposed to just callable inside this code)
    def external_method(self, param):
        # this kind of method only allows one input parameter
        pass

    # more examples of externally executable methods
    @command()
    def turn_off(self):
        self.set_state(DevState.OFF)

    @command()
    def turn_on(self):
        self.set_state(DevState.ON)


# start the server
if __name__ == "__main__":
    TemplateDeviceServer.run_server()
