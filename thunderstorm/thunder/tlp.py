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
import os,sys
import glob, shutil


import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from thunderstorm.thunder.pulses import IVTime
from thunderstorm.thunder.analysis.tlp_analysis import TLPAnalysis
from thunderstorm.thunder.analysis.leakage_analysis import LeakageAnalysis
from thunderstorm.thunder.analysis.report_analysis import TLPReporting


from datetime import datetime
import markdown as md


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
        data = np.zeros(1, format)
        data['Voltage'] = voltage
        data['Current'] = current
        self._data = data

    @property
    def current(self):
        """Return the current array of the TLP curve
        """
        return self._data['Current']

    @property
    def voltage(self):
        """Return the voltage array of the TLP curve
        """
        return self._data['Voltage']

    @property
    def data(self):
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
		if not(type(device_name) is str):
			raise TypeError("Device name must be a string")
		self._device_name = device_name

		if not(pulses.__class__ is IVTime):
			raise TypeError("Pulses must be an IVTime object")
		self._pulses_data = pulses
        #TODO this should be reworked to handle None
        #if no transient data is available
		if pulses.pulses_length == 0 or pulses.pulses_nb == 0:
			self.has_transient_pulses = False
		else:
			self.has_transient_pulses = True

		if (leak_evol == None or len(leak_evol) == 0
			or np.alltrue(leak_evol == 0)):
			self.has_leakage_evolution = False
			self._leak_evol = None
		else:
			self.has_leakage_evolution = True
			self._leak_evol = leak_evol

		if len(iv_leak) == 0:
			self.has_leakage_ivs = False
			self._iv_leak_data = None
		else:
			self.has_leakage_ivs = True
			self._iv_leak_data = iv_leak

		self.has_report = False
		self._tlp_curve = tlp_curve
		self._tester_name = tester_name
		self._original_data_file_path = file_path

        ## PSA thi is a trial to integrate the data analysis
		baseDir=os.path.dirname(file_path)

		#path_comp=os.path.abspath(baseDir).split('/')
		#if path_comp[-1]=='':
		#	devName=path_comp[-2]
		#else:
		#	devName=path_comp[-1]
			
		devName = os.path.splitext(os.path.basename(str(file_path)))[0]


		if not os.path.exists(os.path.join(baseDir,'report_analysis')):
			os.mkdir(os.path.join(baseDir,'report_analysis'))

		
		self.spot_v=0.5  		# default value for leakage extraction : 0.5V
		self.fail_perc=15    	# default value for failure level 15%
		self.seuil=-0.4     	# default value for triggering point extraction: -0.4V
		
		my_tlp_analysis=TLPAnalysis(tlp_curve)
		my_tlp_analysis.set_threshold(self.seuil)


		if self.has_leakage_ivs :
			my_tlp_analysis.set_leak_analysis(self._iv_leak_data)
			my_leak_analysis=my_tlp_analysis.my_leak_analysis
			my_tlp_analysis.set_spot(self.spot_v)
			my_tlp_analysis.set_fail(self.fail_perc)
			
		elif self.has_leakage_evolution :
			my_tlp_analysis.set_evol_analysis(leak_evol)
			my_leak_analysis=my_tlp_analysis.my_leak_analysis
			my_tlp_analysis.set_fail(self.fail_perc)


		my_tlp_analysis.set_device_name(devName)
		my_tlp_analysis.set_base_dir(baseDir)

			
			#leak_tab=my_leak_analysis.get_leak_array_from_voltage(self.spot_v)
			#err_tab=my_leak_analysis.check_leak_array_from_percentage(leak_tab,self.fail_perc) # Value in %
			#rising,falling=my_leak_analysis.get_failure_points(err_tab,self.fail_perc)
			#fail_index=my_leak_analysis.fail_index
			#my_leak_analysis.set_fail_str(my_tlp_analysis.tlp_data)
	
				
			#kInd=my_tlp_analysis.extract_triggering_point(self.seuil)
			#volt=my_tlp_analysis.get_voltage_array()
			#curr=my_tlp_analysis.get_current_array()

			#trig_inf=my_tlp_analysis.set_triggering_str()


			
			#my_leak_analysis.make_reference_plot(baseDir+'/report_analysis/reference.png')
			#my_tlp_analysis.make_derivative_plot(baseDir+'/report_analysis/derivative.png')
			#my_leak_analysis.make_evolution_plot(baseDir+'/report_analysis/evolution.png')
			#my_leak_analysis.make_first_evolution_plot(baseDir+'/report_analysis/first_evolution.png')
			#my_tlp_analysis.make_tlp_plot(baseDir+'/report_analysis/TLP')
			
			#my_tlp_analysis.get_fitting_data()
			
			#my_tlp_analysis.make_extraction_plot(baseDir+'/report_analysis/TLP_C.png')
			#my_leak_analysis.make_error_plot(baseDir+'/report_analysis/leak_error.png')
			
			
		my_tlp_analysis.update_analysis()
			

		self.myOfile=baseDir+os.sep+devName+'_report.html'
		self.css=os.path.abspath("."+os.sep+"ESDAnalysisTool.css")


		self.report=TLPReporting()
		self.report.set_css_format(self.css)


		self.has_report = self.report.create_report(my_tlp_analysis)
		self.report.save_report(self.myOfile)

		self.my_tlp_analysis=my_tlp_analysis


########### end of addon by PAS July 2nd, 2012


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
		
	def update_analysis(self):
		#print "analysis running an update"
		self.my_tlp_analysis.set_spot(self.spot_v)
		self.my_tlp_analysis.set_fail(self.fail_perc)
		self.my_tlp_analysis.set_threshold(self.seuil)
		self.my_tlp_analysis.update_analysis()

		if self.has_report :
			self.report.clear_report()
			self.has_report=self.report.create_report(self.my_tlp_analysis)
			self.report.save_report(self.myOfile)
			
	def update_style(self):
		self.report.clear_report()
		self.report.set_css_format(self.css)
		self.has_report = self.report.create_report(self.my_tlp_analysis)
		self.report.save_report(self.myOfile)
		
	def save_analysis(self,save_name):
		if self.has_report :
			self.report.clear_report()
			self.has_report=self.report.create_doc(self.my_tlp_analysis)
			f=open(save_name,"w")
			f.write(self.report.output)
			f.close()
			
			baseDir=os.path.dirname(self.myOfile)
			pathName=os.path.dirname(save_name)
			rep=os.path.join(baseDir,'report_analysis')
			#names=os.listdir(rep)
			names=glob.glob(rep+os.sep+"*.png")
			#print rep+"/*.png",names
			for item in names:
				(mypath,myname) =os.path.split(item)
				dest=pathName+os.sep+myname
				shutil.copy(item,dest)

			
			


class Experiment(object):

    def __init__(self, raw_data, exp_name="Unknown"):
        assert raw_data.__class__ is RawTLPdata
        self._raw_data = raw_data
        self._exp_name = exp_name
        return

    def __repr__(self):
        message = "Experiement: "
        message += self._exp_name +"\n"
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
