import numpy as np
import innout as io
from scipy.spatial import cKDTree
from tools import city_dist

def NN_wrapper():
    
    cities=io.load_cities()
    
    start_min = None
    score_min = 1e20
    while (1):
        start = np.random.randint(low=0, high=150000, size=2)
        route, score = NN(cities=cities, start=start)
        if (score < score_min):
            score_min = score
            start_min = start
            print "score_min, start_min: ", score_min, start_min

def NN(cities=io.load_cities(), start=np.array([0,0])):
    '''
    Nearest neighbor algorithm
    Routes are built incrementally in a greedy fashion
    '''
    
    Nc = cities.shape[0]
        
    assert((start[0] < Nc) & (start[1] < Nc) &
           (start[0] >= 0) & (start[1] >= 0))
    
    myroute = [np.zeros(Nc, dtype=int),
               np.zeros(Nc, dtype=int)]
    myroute[0][0] = start[0]
    myroute[1][0] = start[1]
            
    '''
    the edges array keeps track of edges incident 
    to a city for each route
    for example, if city 10 is incident to cities 
    97 and 436 in route 0,
    edges[0][10,0] = 97 
    edges[0][10,1] = 436
    because it is a tour, each city will have at 
    most 2 edges incident to it
    a -1 indicates no edge
    '''
    edges = [-np.ones([Nc,2], dtype=int), 
             -np.ones([Nc,2], dtype=int)]
    
    # starting points get dummy edges since we don't
    # need to end up here
    edges[0][myroute[0][0], 0] = 999999
    edges[1][myroute[1][0], 0] = 999999

    # keep track of distance as we go...
    dist = np.array([0.0, 0.0])
    
    tree = cKDTree(cities)
    for ic in xrange(Nc-1):
        for ir in range(2):
            #if (ic%10000 == 0):
            #    print "working on city: ", ic, int(np.max(dist))
                
            thiscity = myroute[ir][ic] 
            
            assert(edges[ir][thiscity, 0] >= 0)
            assert(edges[ir][thiscity, 1] == -1)
            
            knbrs = 10
            nextcity = -1
            while(nextcity == -1):
                nbrs_dist, nbrs = tree.query(cities[thiscity], knbrs)
                for nbr in nbrs:
                    if (nbr == Nc):
                        print "failed to find next city"
                        return
                    # check if we've already been here...
                    if (edges[ir][nbr,0] == -1):
                        # eliminate edges in other route...
                        if ((edges[(ir+1)%2][thiscity, 0] != nbr) &
                            (edges[(ir+1)%2][thiscity, 1] != nbr)):
                            nextcity = nbr
                            break
                
                knbrs *= 2
                        
            myroute[ir][ic+1] = nextcity
            dist[ir] += city_dist(cities, thiscity, nextcity)
            edges[ir][thiscity, 1] = nextcity
            edges[ir][nextcity, 0] = thiscity
                
    score = int(np.max(dist))
    print "start, score: ", start, score
    return myroute, score

def greedy(cities=io.load_cities()):
    
    return
