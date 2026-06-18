import numpy as np

from pymodaq.extensions.data_mixer.model import DataMixerModel, np  # np will be used in method eval of the formula

from pymodaq_utils.math_utils import gauss1D, my_moment

from pymodaq_data.data import DataToExport, DataWithAxes, DataCalculated, DataDim
from pymodaq_gui.parameter import Parameter
import laserbeamsize as lbs
from pymodaq.extensions.data_mixer.parser import (
    extract_data_names, split_formulae, replace_names_in_formula)

class DataMixerBeamProfiler(DataMixerModel):
    params = [
                {'title': 'Beam position (mm)', 'name': 'pos', 'type': 'bool', 'value': True},
                {'title': 'Beam size (mm)', 'name': 'size', 'type': 'bool', 'value': True},
                {'title': 'Rotation (°)', 'name': 'phi', 'type': 'bool', 'value': True}
    ]

    def process_dte(self, dte: DataToExport):
        dte_processed = DataToExport('computed')
        data_array_2D = dte.get_data_from_name('BSCamera').data[0]

        x, y, d_major, d_minor, phi = lbs.beam_size(data_array_2D)

        if self.settings.child('size').value():
            dwa_0D_size = DataCalculated('BeamSize', data=[np.atleast_1d(d_major),
                                                           np.atleast_1d(d_minor)], labels=['Dminor', 'Dmajor'])
            dte_processed.append(dwa_0D_size)

        if self.settings.child('pos').value():
            dwa_0D_position = DataCalculated('BeamPosition', data=[np.atleast_1d(x), np.atleast_1d(y)],
                                                labels=['X', 'Y'])
            dte_processed.append(dwa_0D_position)

        if self.settings.child('phi').value():
            dwa_0D_angle = DataCalculated('BeamAngle', data=[np.atleast_1d(phi)]
                                            , labels=['Phi'])
            dte_processed.append(dwa_0D_angle)

        return dte_processed




