import numpy as np

p_temp = np.array([1, 1j, -1, -1j])
p_temp2 = np.array([1j, -1j])
p_temp3 = np.array([1, -1])
p1 = np.repeat( p_temp, 64 )
p2 = np.tile( np.repeat( p_temp, 4 ), 16 )
p3 = np.tile( np.concatenate( (np.repeat( p_temp2, 32 ), np.repeat( p_temp3, 32 )) ), 2) #np.tile( p_temp, 16 )
p4 = np.tile( p_temp, 64 )

detection = p1**+1 * p2**-2 * p3**0 * p4**+2
det_parsed = []

for el in p4:
    if el == 1:
        det_parsed.append( '+x' )
    elif el == -1:
        det_parsed.append( '-x' )
    elif el == 1j:
        det_parsed.append( '+y' )
    elif el == -1j:
        det_parsed.append( '-y' )

print(det_parsed)