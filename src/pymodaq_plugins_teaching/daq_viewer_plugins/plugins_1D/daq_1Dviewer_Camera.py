import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport, Axis
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins

from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer

from pymodaq_data import Q_

class DAQ_1DViewer_Camera(DAQ_Viewer_base):
    """ Instrument plugin class for a 1D viewer.
    
    This object inherits all functionalities to communicate with PyMoDAQ’s DAQ_Viewer module through inheritance via
    DAQ_Viewer_base. It makes a bridge between the DAQ_Viewer module and the Python wrapper of a particular instrument.

    TODO Complete the docstring of your plugin with:
        * The set of instruments that should be compatible with this instrument plugin.
        * With which instrument it has actually been tested.
        * The version of PyMoDAQ during the test.
        * The version of the operating system.
        * Installation instructions: what manufacturer’s drivers should be installed to make it run?

    Attributes:
    -----------
    controller: object
        The particular object that allow the communication with the hardware, in general a python wrapper around the
         hardware library.
         
    # TODO add your particular attributes here if any

    """
    params = comon_parameters + [ {'title': 'Amplitude', 'name': 'amp', 'type': 'float', 'value': 500 },
                                  {'title': 'Noise', 'name': 'noise', 'type': 'float', 'value': 0.5 },
                                  {'title': 'Width', 'name': 'width', 'type': 'float', 'value': 20 },
                                  {'title': 'Gratings', 'name': 'gratings', 'type': 'list', 'limits': Spectrometer.gratings},
                                  {'title': 'Laser wavelength (nm)', 'name': 'laser', 'type': 'float', 'value': 532}
        ]

    def ini_attributes(self):
        self.controller: Spectrometer = None



        self.x_axis = None

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == "amp":
           self.controller.amplitude = param.value()  # when writing your own plugin replace this line
        elif param.name() == "noise":
            self.controller.noise = param.value()
        elif param.name() == "width":
            self.controller.width = param.value()
        elif param.name() == "gratings":
            self.controller.grating = param.value()
        elif param.name() == "laser":
            self.controller.data_wavelength = param.value()
        data_x_axis = self.controller.get_wavelength_axis()
        self.x_axis = Axis(data=data_x_axis, label='Wavelength', units='nm', index=0)

    def ini_detector(self, controller=None):
        """Detector communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator/detector by controller
            (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """
        if self.is_master:
            self.controller = Spectrometer()  #instantiate you driver with whatever arguments are needed
            self.controller.open_communication() # call eventual methods
            initialized = self.controller.open_communication()
        else:
            self.controller = controller
            initialized = True

        self.settings.child('gratings').setValue(self.controller.grating)

        # get the x_axis (you may want to to this also in the commit settings if x_axis may have changed
        data_x_axis = self.controller.get_wavelength_axis()  # if possible
        self.x_axis = Axis(data=data_x_axis, label='Wavelength', units='nm', index=0)

        self.settings.child('laser').setValue(Q_(self.controller.data_wavelength,'nm').m_as('nm'))
        self.settings.child('amp').setValue(self.controller.amplitude)
        self.settings.child('width').setValue(self.controller.width)
        self.settings.child('noise').setValue(self.controller.noise)

        info = "Initialized"
        return info, initialized

    def close(self):
        """Terminate the communication protocol"""
        if self.is_master:
            self.controller.close_communication()  # when writing your own plugin replace this line


    def grab_data(self, Naverage=1, **kwargs):
        """Start a grab from the detector

        Parameters
        ----------
        Naverage: int
            Number of hardware averaging (if hardware averaging is possible, self.hardware_averaging should be set to
            True in class preamble and you should code this implementation)
        kwargs: dict
            others optionals arguments
        """
        data_tot = self.controller.grab_spectrum()
        axis = Axis('Wavelength', data=self.controller.get_wavelength_axis())
        self.dte_signal.emit(DataToExport('myplugin',
                                          data=[DataFromPlugins(name='Spectrometer', data=[data_tot],
                                                                dim='Data1D', labels=['Wavelength (nm)'],
                                                                axes=[axis])]))



    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport('myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data1D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""

        self.controller.stop()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))

        return ''


if __name__ == '__main__':
    main(__file__)
