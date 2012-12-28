import numpy as np

def load_cities():
    print 'loading cities...'
    path = '../data/santa_cities.csv'
    
    return np.loadtxt(path, delimiter=',', unpack=False,
                      usecols=[1,2], dtype=int, skiprows=1)

def write_cities_lkh(cities, name='santa_cities.tsp'):

    Nc = cities.shape[0]
    assert(Nc > 0)
    f = file(name, mode='w')
    
    f.write('NAME : santa_cities\n')
    f.write('TYPE : TSP\n')
    f.write('DIMENSION : ' + str(Nc) + '\n')
    f.write('EDGE_WEIGHT_TYPE : EUC_2D\n')
    f.write('NODE_COORD_SECTION \n')
    
    indicies = np.arange(Nc).reshape([Nc,1]) + 1
    
    np.savetxt(f, np.concatenate([indicies, cities], axis=1), delimiter=' ', fmt='%d')
    
    f.close()

def read_route_lkh(path='route.tour'):
    
    route = np.loadtxt(path, dtype=int, skiprows=6) 
    
    return route-1

def write_forbidden(route=read_route_lkh()):

    f = file('Forbidden.c', mode='w')
    f.write('#include "LKH.h"\n')
    f.write('#include <stdio.h>\n')
    f.write('int Forbidden(const Node * ta, const Node * tb) {\n')
    
    Nc = route.shape[0]
    assert(Nc > 0)
    '''
    f.write('static int route[' + Nc + '] = [')
    for ic in xrange(Nc):
        f.write(route[ic])
        if (ic != Nc-1):
            f.write(
    '''
    assert(0)
    for ic in xrange(Nc-1):
        if (ic == 0):
            f.write('if ')
        else:
            f.write('else if ')
        f.write('((ta->Id == ' + str(int(route[ic]+1)) + ' && tb->Id == ' + str(int(route[ic+1]+1)) + ') || (ta->Id == '\
                    + str(int(route[ic+1]+1)) + ' && tb->Id == ' + str(int(route[ic]+1)) + '))\n')
        f.write('\t return 1;\n')

    f.write('else\n')
    f.write('\t return 0;\n')
    f.write('}')
    
    return
    
def load_route(path='../data/random_paths_benchmark.csv'):
    
    tmp = np.loadtxt(path, delimiter=',', unpack=False,
                      usecols=[0,1], dtype=int, skiprows=1)
    
    return [tmp[:,0], tmp[:,1]]
    
def write_route(route, name='myroute'):
    print 'writing route ' + name + '...'
    f = file(name+'.csv', mode='w')
    f.write('path1,path2\n')
    np.savetxt(f, np.asarray(route).T, delimiter=',', fmt='%d')
    
    f.close()
