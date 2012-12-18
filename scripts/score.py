import numpy as np
import santa_io as io
import scipy.sparse as sparse
from tools import euclid_dist

def calc_score(cities=io.load_cities(), route=io.load_route()):
    Nc = cities.shape[0]
    assert(Nc == 150000)  # is there any reason for looking at subset of cities?

    # first make sure all cities are visited exactly once for both paths
    np.testing.assert_array_equal(np.sort(route[:,0]), np.arange(Nc))
    np.testing.assert_array_equal(np.sort(route[:,1]), np.arange(Nc))

    # use sparse matrix to ensure paths are disjoint
    # XXXX is there a better way? seems to be slow...
    adj = sparse.lil_matrix((Nc,Nc), dtype=bool)
    
    dist = np.array([0.0, 0.0])
    for ic in xrange(Nc-1):
        for ir in range(2):
            assert(route[ic,ir] != route[ic+1,ir])
            if (route[ic,ir] < route[ic+1,ir]):
                ii = route[ic,ir]
                jj = route[ic+1,ir]
            else:
                ii = route[ic+1,ir]
                jj = route[ic,ir]
            assert(adj[ii,jj] == False)
            adj[ii, jj] = True
            dist[ir] += euclid_dist(cities[route[ic,ir], :], cities[route[ic+1,ir], :])
    
    
    return int(np.max(dist))
