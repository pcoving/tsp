import numpy as np
import santa_io as io

def NN(cities=io.load_cities(), start=np.array([0,0])):
    Nc = cities.shape[0]
    assert(Nc == 150000)
    
    assert((start[0] < Nc) & (start[1] < Nc))
    
    route = np.zeros([Nc, 2])
    route[0,:] = start

    return route

def greedy(cities=io.load_cities()):
    Nc = cities.shape[0]
    assert(Nc == 150000)

    
