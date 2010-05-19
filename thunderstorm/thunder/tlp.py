# -*- coding: utf-8 -*-

# Copyright (C) 2010 Trémouilles David

#This file is part of Thunderstorm.
#
#ThunderStrom is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#ThunderStorm is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public License
#along with ThunderStorm.  If not, see <http://www.gnu.org/licenses/>.

""" tlp data
"""

import numpy as np
from thunder.pulses import IVTime

class TLPcurve(object):
    """The data for a TLP curve
    """
    def __init__(self, current, voltage):
        """current is a 1D numpy array
        voltage is a 1D numpy array
        of same length
        """
        assert current.__class__ == np.ndarray
        assert voltage.__class__ == np.ndarray
        assert current.shape == voltage.shape
        assert len(current.shape) == 1
        length = current.shape[0]
        format = np.dtype([('Voltage', (np.float64, length)),
                            ('Current', (np.float64, length))])
        self._data = np.zeros(1, format)
        self._data['Voltage'] = voltage
        self._data['Current'] = current
        self.data = _data

    @property
    def current():
        """Return the current array of the TLP curve
        """
        return self._data['Current']

    @property
    def voltage():
        """Return the voltage array of the TLP curve
        """
        return self._data['Voltage']

    @property
    def data():
        """Return a copy of the raw tlp curve data
        """
        return self._data.copy()


class RawTLPdata(object):
    """All measurement data: device name, pulses, TLP curve, leakage ...
    are packed in this class
    """

    def __init__(self, device_name, pulses,
                 iv_leak, tlp_curve, leak_evol,
                 file_path, tester_name=None):
        """
        Parameters
        ----------
        device_name: string
            The device name

        pulses:
            A set of TLP IVTime pulses

        iv_leak:
            Leakage curves data

        tlp_curve:
            TLP curve data
        """
        assert type(device_name) is str
        assert pulses.__class__ is IVTime
        self._device_name = device_name
        self._pulses_data = pulses
        self._iv_leak_data = iv_leak
        self._tlp_curve = tlp_curve
        self._leak_evol = leak_evol
        self._tester_name = tester_name
        self._original_data_file_path = file_path

    def __repr__(self):
        message = "%g pulses \n" %self.pulses.pulses_nb
        message += "Original file: " + self.original_file_name
        return message

    @property
    def tester_name(self):
        return self._tester_name

    @property
    def pulses(self):
        """Pulses data """
        return self._pulses_data

    @property
    def iv_leak(self):
        """Leakage curve data """
        return self._iv_leak_data

    @property
    def device_name(self):
        return self._device_name

    @property
    def tlp_curve(self):
        return self._tlp_curve

    @property
    def leak_evol(self):
        return self._leak_evol

    @property
    def original_file_name(self):
        return self._original_data_file_path


class Experiment(object):

    def __init__(self, raw_data, exp_name="Unknown"):
        assert raw_data.__class__ is RawTLPdata
        self._raw_data = raw_data
        self._exp_name = exp_name
        return

    def __repr__(self):
        message = "Experiement\n"
        message += "name: " + self._exp_name +"\n"
        return message

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def exp_name(self):
        return self._exp_name

    @exp_name.setter
    def exp_name(self, value):
        self._exp_name = value
