import numpy as np
import innout as io
from scipy.spatial import cKDTree
from tools import city_dist, calc_score

def NN_wrapper():
    
    cities=io.load_cities()
    
    start_min = None
    score_min = 1e20
    while (1):
        start = np.random.randint(low=0, high=150000, size=2)
        route, score = greeyNN(cities=cities, start=start)
        if (score < score_min):
            score_min = score
            start_min = start
            print "score_min, start_min: ", score_min, start_min

def greedyNN(cities, start=np.array([0,0])):
    '''
    Nearest neighbor algorithm
    Routes are built incrementally in a greedy fashion
    '''
    
    Nc = cities.shape[0]
    assert(Nc > 0)
    
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
        if (ic%10000 == 0):
            print "working on city: ", ic, int(np.max(dist))
        for ir in range(2):
        
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
                        return None, 99999999999
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

def opt2(cities, route, name='test', look_ahead=9999999, checkpoint=50):

    '''
    next step: how to generalize 2-opt so that it includes
    both paths?  one path demonstrates significant 'bow-tieing'
    and could benefit from a more 'holistic' approach
    '''
    Nc = cities.shape[0]
    assert(Nc > 0)

    route = [route[0].copy(),
             route[1].copy()]

    edges = [-np.ones([Nc,2], dtype=int), 
             -np.ones([Nc,2], dtype=int)]
            
    dist = np.array([0.0, 0.0])
    for ir in range(2):
        edges[ir][route[ir][0], 0] = 999999
        edges[ir][route[ir][Nc-1], 1] = 999999
        for ic in xrange(Nc-1):
            dist[ir] += city_dist(cities, route[ir][ic], route[ir][ic+1])
            edges[ir][route[ir][ic], 1] = route[ir][ic+1]
            edges[ir][route[ir][ic+1], 0] = route[ir][ic]
            
        
    if (dist[0] > dist[1]):
        ir = 0
    else:
        ir = 1
    iter = 0
    while (1):
        ic = np.random.randint(low=0, high=Nc-1, size=2)
        ic.sort()
        if ((ic[1] > (ic[0]+1)) & (ic[1] < (ic[0]+look_ahead))):
            rr = route[ir]
            if ((edges[(ir+1)%2][rr[ic[0]], 0] != rr[ic[1]]) &
                (edges[(ir+1)%2][rr[ic[0]], 1] != rr[ic[1]]) &
                (edges[(ir+1)%2][rr[ic[0]+1], 0] != rr[ic[1]+1]) &
                (edges[(ir+1)%2][rr[ic[0]+1], 1] != rr[ic[1]+1])):

                dist_old = city_dist(cities, rr[ic[0]],   rr[ic[0]+1]) +\
                           city_dist(cities, rr[ic[1]],   rr[ic[1]+1])
                dist_new = city_dist(cities, rr[ic[0]],   rr[ic[1]]) +\
                           city_dist(cities, rr[ic[0]+1], rr[ic[1]+1])
                if (dist_new < dist_old):
                    route_new = rr.copy();
                    
                    count = ic[0]+1
                    for ii in xrange(ic[1], ic[0], -1):
                        route_new[count] = rr[ii]
                        count = count + 1

                    edges[ir][route[ir][0], 0] = 999999
                    edges[ir][route[ir][Nc-1], 1] = 999999
                    for ic in xrange(Nc-1):
                        edges[ir][route[ir][ic], 1] = route[ir][ic+1]
                        edges[ir][route[ir][ic+1], 0] = route[ir][ic]
                                                                
                    route[ir] = route_new
                    dist[ir] += (dist_new - dist_old)
                    
                    iter += 1
                    score = int(np.max(dist))
                    print score
                    if (iter%checkpoint == 0):
                        calc_score(cities, route)
                        io.write_route(route, name + '_' + str(score))
                    
        if (dist[ir] < dist[(ir+1)%2]):
            ir = (ir+1)%2

    return route

def contruct_lkh(cities):
    Nc = cities.shape[0]
    assert(Nc > 0)
    
    rr = io.read_route_lkh()

    myroute = [rr, np.zeros(Nc, dtype=int)]
    edges = [-np.ones([Nc,2], dtype=int), 
             -np.ones([Nc,2], dtype=int)]
    edges[0][myroute[0][0], 0] = 999999
    edges[1][myroute[1][0], 0] = 999999

    for ic in xrange(Nc-1):
        edges[0][myroute[0][ic],   1] = myroute[0][ic+1]
        edges[0][myroute[0][ic+1], 0] = myroute[0][ic]

    dist = np.array([0.0])
    tree = cKDTree(cities)
    for ic in xrange(Nc-1):
        if (ic%10000 == 0):
            print "working on city: ", ic, int(np.max(dist))
        
        thiscity = myroute[1][ic] 
        
        assert(edges[1][thiscity, 0] >= 0)
        assert(edges[1][thiscity, 1] == -1)

        knbrs = 10
        nextcity = -1
        while(nextcity == -1):
            nbrs_dist, nbrs = tree.query(cities[thiscity], knbrs)
            for nbr in nbrs:
                if (nbr == Nc):
                    print "failed to find next city"
                    return None, 99999999999
                    # check if we've already been here...
                if (edges[1][nbr,0] == -1):
                    # eliminate edges in other route...
                    if ((edges[0][thiscity, 0] != nbr) &
                        (edges[0][thiscity, 1] != nbr)):
                        nextcity = nbr
                        break
                
            knbrs *= 2
            
        myroute[1][ic+1] = nextcity
        dist += city_dist(cities, thiscity, nextcity)
        edges[1][thiscity, 1] = nextcity
        edges[1][nextcity, 0] = thiscity

    '''
    myroute = [rr, rr.copy()]
    ir = 0
    for ii in xrange(0,Nc,5):
        myroute[(ir+1)%2][ii]   = myroute[ir][ii]
        myroute[(ir+1)%2][ii+1] = myroute[ir][ii+3]
        myroute[(ir+1)%2][ii+2] = myroute[ir][ii+1]
        if (ii+4 < Nc):
            myroute[(ir+1)%2][ii+3] = myroute[ir][ii+4]
            myroute[(ir+1)%2][ii+4] = myroute[ir][ii+2]

        ir = (ir+1)%2
    # 0 3 1 4 2 5 8 6 9 7 10 
    '''

    return myroute
