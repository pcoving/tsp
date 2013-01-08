import numpy as np
import scipy.sparse as sparse

def calc_score(cities, route):
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
    score = int(np.max(dist))
    print "score: ", score, dist
    return score

def city_dist(cities, ic0, ic1):
    # for debugging...
    #assert(ic0 >= 0)
    #assert(ic1 >= 0)
    
    #Nc = cities.shape[0]
    #assert(ic0 < Nc)
    #assert(ic1 < Nc)
    
    return np.sqrt(np.power(cities[ic1, 0] - cities[ic0, 0], 2) + 
                   np.power(cities[ic1, 1] - cities[ic0, 1], 2))
    

