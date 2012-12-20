import numpy as np

def load_cities():

    path = '../data/santa_cities.csv'
    
    return np.loadtxt(path, delimiter=',', unpack=False,
                      usecols=[1,2], dtype=int, skiprows=1)

def load_route(path='../data/random_paths_benchmark.csv'):
    
    tmp = np.loadtxt(path, delimiter=',', unpack=False,
                      usecols=[0,1], dtype=int, skiprows=1)
    
    return [tmp[:,0], tmp[:,1]]
    
