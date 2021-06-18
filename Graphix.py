#!/usr/bin/python3 -u
from tango.server import run
import os
from GraphixSensor import GraphixSensor
from GraphixCtrl import GraphixCtrl

# Run PhytronMCC2Ctrl and PhytronMCC2Axis
run([GraphixCtrl, GraphixSensor])