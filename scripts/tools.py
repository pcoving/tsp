import numpy as np

def euclid_dist(point0, point1):
    assert(point0.shape == (2,))
    assert(point1.shape == (2,))
    return np.sqrt(np.power(point1[0] - point0[0], 2) + 
                   np.power(point1[1] - point0[1], 2))

