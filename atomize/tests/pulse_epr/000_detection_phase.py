import numpy as np

p_temp = np.array([1, 1j, -1, -1j])
p1 = np.repeat( p_temp, 16 )
p2 = np.tile( np.repeat( p_temp, 4 ), 4 )
p3 = np.tile( p_temp, 16 )

detection = p1**-1 * p2**2 * p3**-2
det_parsed = []

for el in detection:
    if el == 1:
        det_parsed.append( '+x' )
    elif el == -1:
        det_parsed.append( '-x' )
    elif el == 1j:
        det_parsed.append( '+y' )
    elif el == -1j:
        det_parsed.append( '-y' )

print(det_parsed)