
from pymodaq.control_modules.viewer_utility_classes import main
from pymodaq_data import DataCalculated
from pymodaq_plugins_mockexamples.daq_viewer_plugins.plugins_2D.daq_2Dviewer_BSCamera import DAQ_2DViewer_BSCamera
import laserbeamsize as lbs
import numpy as np

class DAQ_2DViewer_BeamProfiler(DAQ_2DViewer_BSCamera):

    params = ( DAQ_2DViewer_BSCamera.params +
              [ {'title': 'Beam position (mm)', 'name': 'pos', 'type': 'bool', 'default': True },
                {'title': 'Beam size (mm)', 'name': 'size', 'type': 'bool', 'default': True },
                {'title': 'Rotation (°)', 'name': 'phi', 'type': 'bool', 'default': True }
             ])


    def grab_data(self, Naverage=1, **kwargs):
        dte = self.average_data(Naverage)
        data_array_2D = dte.get_data_from_name('BSCamera').data[0]

        x, y, d_major, d_minor, phi = lbs.beam_size(data_array_2D)
        dte_0D_size = DataCalculated('BeamSize', data=[np.atleast_1d(d_major),
                                                   np.atleast_1d(d_minor)], labels = ['Dminor','Dmajor'])

        dte_0D_position = DataCalculated('BeamPosition', data=[np.atleast_1d(x), np.atleast_1d(y)], labels = ['X','Y'])

        dte_0D_angle = DataCalculated('BeamAngle', data=[np.atleast_1d(phi)]
                                                   , labels = ['Phi'])
        if self.settings.child('pos').value() :
            dte.append(dte_0D_position)
        if self.settings.child('size').value() :
            dte.append(dte_0D_size)
        if self.settings.child('phi').value() :
            dte.append(dte_0D_angle)
        return self.dte_signal.emit(dte)


if __name__ == '__main__':
    main(__file__)
