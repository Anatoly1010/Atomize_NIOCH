import os
import numpy as np
import atomize.general_modules.general_functions as general
from scipy.interpolate import CubicSpline, PchipInterpolator

path_to_main = os.path.abspath(os.getcwd())
filename = os.path.join(path_to_main, '', 'test_calibration_until720mT.csv')

header_array = []
header = 0
spline_array = np.zeros(1000)
field_spline_array = np.zeros(1000)

file_to_read = open(filename, 'r')
for i, line in enumerate(file_to_read):
    if i is header: break
    temp = line.split("#")
    header_array.append(temp)
file_to_read.close()

temp = np.genfromtxt(filename, dtype = float, delimiter = ',', skip_header = 1, comments = '#') 
data = np.transpose(temp)

cs = CubicSpline(data[0], data[1]/data[0], bc_type='natural')
#cs = PchipInterpolator(data[0], data[1]/data[0])

general.plot_1d('EXP', data[0], data[1]/data[0], label = 'exp', xname = 'Field', xscale = 'G', yname = 'Meas/Set', yscale = 'A. U.')

for i in range(1000):
    field_spline_array[i] = 900 + i
    spline_array[i] = cs(900 + i)

FIELD = 3020
print('Set = ', FIELD / cs(FIELD))

general.plot_1d('EXP', field_spline_array, spline_array, label = 'spline', xname = 'Field', xscale = 'G', yname = 'Meas/Set', yscale = 'A. U.')
