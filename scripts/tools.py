import numpy as np

def euclid_dist(point0, point1):
    assert(point0.shape == (2,))
    assert(point1.shape == (2,))
    return np.sqrt(np.power(point1[0] - point0[0], 2) + 
                   np.power(point1[1] - point0[1], 2))

def city_dist(cities, ic0, ic1):
    #assert(ic0 >= 0)
    #assert(ic1 >= 0)
    
    #Nc = cities.shape[0]
    #assert(ic0 < Nc)
    #assert(ic1 < Nc)
    
    return np.sqrt(np.power(cities[ic1, 0] - cities[ic0, 0], 2) + 
                   np.power(cities[ic1, 1] - cities[ic0, 1], 2))
    

