import numpy as np
import matplotlib.pyplot as plt
import santa_io as io

def plot_cities(cities=io.load_cities()):
    
    plt.scatter(cities[:,0], cities[:,1], s=1, c='black', alpha=0.3)
    plt.axis('tight')
    route = io.load_route()
    plt.hold(True)
    plt.plot(cities[route[:,0],0], cities[route[:,0],1], c='red', alpha=0.1)
    plt.show()
    
    
    
