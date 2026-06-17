import numpy as np

from pymodaq_utils.utils import ThreadCommand
from pymodaq_data.data import DataToExport
from pymodaq_gui.parameter import Parameter

from pymodaq.control_modules.viewer_utility_classes import DAQ_Viewer_base, comon_parameters, main
from pymodaq.utils.data import DataFromPlugins


from pymodaq_plugins_teaching.hardware.spectrometer import Spectrometer



class DAQ_0DViewer_PhotoDiode(DAQ_Viewer_base):
    """ Instrument plugin class for a OD viewer.
    
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
        ## TODO for your custom plugin: elements to be added here as dicts in order to control your custom stage
        ]

    def ini_attributes(self):
        self.controller: Spectrometer = None
        pass

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
        ##

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
            initialized = self.controller.open_communication() # call eventual methods
        else:
            self.controller = controller
            initialized = True
        self.settings.child('amp').setValue(self.controller.amplitude)
        self.settings.child('noise').setValue(self.controller.noise)
        self.settings.child('width').setValue(self.controller.width)
        # TODO for your custom plugin (optional) initialize viewers panel with the future type of data
        #self.dte_signal_temp.emit(DataToExport(name='myplugin',
                                              # data=[DataFromPlugins(name='Mock1',
                                                                   # data=[np.array([0]), np.array([0])],
                                                                   # dim='Data0D',
                                                                   # labels=['Mock1', 'label2'])]))

        info = "Whatever info you want to log"
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

        # synchrone version (blocking function)
        #raise NotImplementedError  # when writing your own plugin remove this line
        data_array = self.controller.grab_monochromator()
        self.dte_signal.emit(DataToExport(name='MyMonochromator',
                                          data=[
                                              DataFromPlugins(name='Mono', data=[data_array],
                                                                dim='Data0D', labels=['Intensity']),

                                          ]))

        # asynchrone version (non-blocking function with callback) très rare uniquement si c'est trop lent
        #raise NotImplementedError  # when writing your own plugin remove this line
        #self.controller.grab_monochromator(self.callback)  # when writing your own plugin replace this line
        #########################################################


    def callback(self):
        """optional asynchrone method called when the detector has finished its acquisition of data"""
        data_tot = self.controller.your_method_to_get_data_from_buffer()
        self.dte_signal.emit(DataToExport(name='myplugin',
                                          data=[DataFromPlugins(name='Mock1', data=data_tot,
                                                                dim='Data0D', labels=['dat0', 'data1'])]))

    def stop(self):
        """Stop the current grab hardware wise if necessary"""
        self.controller.stop()  # when writing your own plugin replace this line
        self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
        return ''


if __name__ == '__main__':
    main(__file__)
