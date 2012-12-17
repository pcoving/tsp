import numpy as np
import santa_io as io
import scipy.sparse as sparse
def euclid_dist(x,y):
    return np.sqrt(np.power(x,2) + np.power(y,2))

def calc_score(cities=io.load_cities(), route=io.load_route()):
    Nc = cities.shape[0]
    assert(Nc == 150000)  # is there any reason for looking at subset of cities?

    # first make sure all cities are visited exactly once for both paths
    np.testing.assert_array_equal(np.sort(route[:,0]), np.arange(Nc))
    np.testing.assert_array_equal(np.sort(route[:,1]), np.arange(Nc))
    
    # use sparse matrix to ensure paths are disjoint
    # XXXX is there a better way? seems to be slow...
    adj = sparse.lil_matrix((Nc,Nc),dtype=int)

    dist = np.array([0.0, 0.0])
    for ic in xrange(Nc-1):
        for ir in range(2):
            adj[route[ic,ir], route[ic+1,ir]] += 1
            dist[ir] += euclid_dist(cities[route[ic+1,ir],0] - cities[route[ic,0],0], cities[route[ic+1,ir],1] - cities[route[ic,ir],1])
    
    adj = adj + adj.T
    assert(np.max(adj.data) == 1)
    
    return int(np.max(dist))
