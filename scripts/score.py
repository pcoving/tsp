import numpy as np
import innout as io
import scipy.sparse as sparse
from tools import city_dist

def calc_score(cities, route=io.load_route()):
    Nc = cities.shape[0]
    
    # first make sure all cities are visited exactly once for both paths
    np.testing.assert_array_equal(np.sort(route[0]), np.arange(Nc))
    np.testing.assert_array_equal(np.sort(route[1]), np.arange(Nc))

    # use sparse matrix to ensure paths are disjoint
    # I purposefully did this differently than the routing
    # for double checking, but seems to be much slower...
    adj = sparse.lil_matrix((Nc,Nc), dtype=bool)
    
    def mycity_dist(ic0, ic1):
        return city_dist(cities, ic0, ic1)

    dist = np.array([0.0, 0.0])
    for ic in xrange(Nc-1):
        for ir in range(2):
            assert(route[ir][ic] != route[ir][ic+1])
            
            assert(adj[route[ir][ic], route[ir][ic+1]] == False)
            assert(adj[route[ir][ic+1], route[ir][ic]] == False)
            
            adj[route[ir][ic], route[ir][ic+1]] = True
            adj[route[ir][ic+1], route[ir][ic]] = True
            
            dist[ir] += mycity_dist(route[ir][ic], route[ir][ic+1])
    
    print dist
    return int(np.max(dist))
