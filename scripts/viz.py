import numpy as np
import matplotlib.pyplot as plt
import innout as io

def plot_cities(cities, route):
    plt.ion()
    plt.figure()
    #plt.scatter(cities[:,0], cities[:,1], s=1, c='black', alpha=0.5)
    plt.plot(cities[route[0],0], cities[route[0],1], c='red', alpha=0.5)
    plt.axis('tight')
    plt.hold(True)
    
    plt.figure()    
    plt.plot(cities[route[1],0], cities[route[1],1], c='green', alpha=0.5)
    plt.axis('tight')
    
    plt.show()
    
    
    
