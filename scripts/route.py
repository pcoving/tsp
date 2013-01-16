import numpy as np
import innout as io
from scipy.spatial import cKDTree
from tools import city_dist, calc_score

def NN_wrapper():
    '''
    Wraps the nearest neighbor algorithm, trying different starting
    points.  Prints to screen the minimum score while running.
    Here some of the best ones:
    7844999 [137433 145655]
    7834793 [45951 97080]
    '''
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

def NN(cities, start=np.array([0,0])):
    '''
    Nearest neighbor algorithm
    Input are indicies of starting cities
    Routes are built incrementally in a greedy fashion, cycling
    from one route to another
    gives solutions in the 7.9M range
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
    
    # build kdtree once for cities
    tree = cKDTree(cities)
    for ic in xrange(Nc-1):
        for ir in range(2):
        
            thiscity = myroute[ir][ic] 
        
            # make sure this city has degree exactly equal to 1
            assert(edges[ir][thiscity, 0] >= 0)
            assert(edges[ir][thiscity, 1] == -1)
            
            # start looking at the nearest 10 neighbors,
            # increasing this number until a valid city is found
            # to continue the tour
            knbrs = 10
            nextcity = -1
            while(nextcity == -1):
                nbrs_dist, nbrs = tree.query(cities[thiscity], knbrs)
                for nbr in nbrs:
                    # it's possible that there are no valid cities left,
                    # right at the end - rare, but has happened
                    # i.e. the last edge is already used by the other tour
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
                # we didn't find a valid city, so increase number of neighbors...
                knbrs *= 2
                        
            # add next city to route and add distance
            myroute[ir][ic+1] = nextcity
            dist[ir] += city_dist(cities, thiscity, nextcity)
            
            # fill in edges array
            edges[ir][thiscity, 1] = nextcity
            edges[ir][nextcity, 0] = thiscity
                
    score = int(np.max(dist))
    return myroute, score

def greedy():

    '''
    To be done...
    '''
    
    return

def opt2(cities, route, look_ahead=9999999, checkpoint=50, name='test'):

    '''
    opt-2 takes a route and shortens it by taking 
    two edges and un-bowties them like so:
    
 
    *     *      *-----*
     \   /
      \ /
      /\    ==>    
     /  \
    *    *       *-----*

    checkpoint is number of edges un-bowtied before writing out
    the route as name_<dist>.csv
    look_ahead is an attempt to make it more efficient - for a given edge,
    will only look for edges to perform 2-opt a specified number ahead in route
    '''
    
    Nc = cities.shape[0]
    assert(Nc > 0)
    
    # don't want to modify input route...
    route = [route[0].copy(),
             route[1].copy()]

    # fill edges (defined in NN above) and compute distance
    # for input route
    edges = [-np.ones([Nc,2], dtype=int), 
             -np.ones([Nc,2], dtype=int)]
    
    dist = np.array([0.0, 0.0])
    for ir in range(2):
        edges[ir][route[ir][0],    0] = 999999
        edges[ir][route[ir][Nc-1], 1] = 999999
        for ic in xrange(Nc-1):
            dist[ir] += city_dist(cities, route[ir][ic], route[ir][ic+1])
            edges[ir][route[ir][ic],   1] = route[ir][ic+1]
            edges[ir][route[ir][ic+1], 0] = route[ir][ic]
    
    # route we're currently optimizing is stored in ir 
    # (always trying to push down maximum distance)
    if (dist[0] > dist[1]):
        ir = 0
    else:
        ir = 1
    iter = 0
    while (1):
        # pick two random cities
        ic0 = np.random.randint(low=0,     high=Nc-2)
        ic1 = np.random.randint(low=ic0+1, high=np.min([ic0+look_ahead, Nc-1]))
        
        # just an alias to make things shorter...
        rr = route[ir]
        
        dist_old = city_dist(cities, rr[ic0],   rr[ic0+1]) +\
                   city_dist(cities, rr[ic1],   rr[ic1+1])
        dist_new = city_dist(cities, rr[ic0],   rr[ic1]) +\
                   city_dist(cities, rr[ic0+1], rr[ic1+1])
        if (dist_new < dist_old):
    
            # check if un-bowtieing conflicts with other tour...
            if ((edges[(ir+1)%2][rr[ic0], 0] != rr[ic1]) &
                (edges[(ir+1)%2][rr[ic0], 1] != rr[ic1]) &
                (edges[(ir+1)%2][rr[ic0+1], 0] != rr[ic1+1]) &
                (edges[(ir+1)%2][rr[ic0+1], 1] != rr[ic1+1])):
                                
                route_new = rr.copy();
                # rearrange route and update edges
                count = ic0+1
                edges[ir][rr[ic0], 1] = rr[ic1]
                edges[ir][rr[ic1], 0] = rr[ic0]
                for ii in xrange(ic1, ic0, -1):
                    route_new[count] = rr[ii]
                    edges[ir][rr[ii], 1] = rr[ii-1]
                    if (ii != ic0+1):
                        edges[ir][rr[ii-1], 0] = rr[ii]
                    count += 1
                edges[ir][rr[ic1+1], 0] = rr[ic0+1]
                edges[ir][rr[ic0+1], 1] = rr[ic1+1]
                    
                route[ir] = route_new                    
                dist[ir] += (dist_new - dist_old)
                
                iter += 1
                score = int(np.max(dist))
                print score
                if (iter%checkpoint == 0):
                    # when we checkpoint make sure tours are disjoint and valid
                    print score, calc_score(cities, route)
                    #assert(score == calc_score(cities, route))
                    io.write_route(route, name + '_' + str(score))
        
        # switch to other route if it's longer
        if (dist[ir] < dist[(ir+1)%2]):
            ir = (ir+1)%2

    return route


def opt3(cities, route, look_ahead=9999999, checkpoint=50, name='test'):
        
    Nc = cities.shape[0]
    assert(Nc > 0)
    
    # don't want to modify input route...
    route = [route[0].copy(),
             route[1].copy()]

    # fill edges (defined in NN above) and compute distance
    # for input route
    edges = [-np.ones([Nc,2], dtype=int), 
             -np.ones([Nc,2], dtype=int)]
    
    dist = np.array([0.0, 0.0])
    for ir in range(2):
        edges[ir][route[ir][0],    0] = 999999
        edges[ir][route[ir][Nc-1], 1] = 999999
        for ic in xrange(Nc-1):
            dist[ir] += city_dist(cities, route[ir][ic], route[ir][ic+1])
            edges[ir][route[ir][ic],   1] = route[ir][ic+1]
            edges[ir][route[ir][ic+1], 0] = route[ir][ic]
    
    # route we're currently optimizing is stored in ir 
    # (always trying to push down maximum distance)
    if (dist[0] > dist[1]):
        ir = 0
    else:
        ir = 1
    iter = 0
    while (1):
        # pick three random cities
        ic = np.zeros(3, dtype=int)
        ic[0] = np.random.randint(low=0,     high=Nc-3)
        ic[1] = np.random.randint(low=ic[0]+1, high=np.min([ic[0]+look_ahead, Nc-2]))
        ic[2] = np.random.randint(low=ic[1]+1, high=np.min([ic[1]+look_ahead, Nc-1]))
        #ic = np.array([137293, 137367, 137369])       
        rr = route[ir]
        
        found = False
    
        dist_old = city_dist(cities, rr[ic[0]], rr[ic[0]+1]) +\
            city_dist(cities, rr[ic[1]], rr[ic[1]+1]) +\
            city_dist(cities, rr[ic[2]], rr[ic[2]+1]) 
        
        dist_new = city_dist(cities, rr[ic[0]], rr[ic[1]+1]) +\
            city_dist(cities, rr[ic[2]], rr[ic[0]+1]) +\
            city_dist(cities, rr[ic[1]], rr[ic[2]+1])
        if (dist_new < dist_old):
            if ((edges[(ir+1)%2][rr[ic[0]], 0] != rr[ic[1]+1]) &
                (edges[(ir+1)%2][rr[ic[0]], 1] != rr[ic[1]+1]) &
                (edges[(ir+1)%2][rr[ic[2]], 0] != rr[ic[0]+1]) &
                (edges[(ir+1)%2][rr[ic[2]], 1] != rr[ic[0]+1]) &
                (edges[(ir+1)%2][rr[ic[1]], 0] != rr[ic[2]+1]) &
                (edges[(ir+1)%2][rr[ic[1]], 1] != rr[ic[2]+1]) ):
                print 0
                route_new = rr.copy();
                # rearrange route
                count = ic[0]+1
                for ii in xrange(ic[1]+1, ic[2]+1):
                    route_new[count] = rr[ii]
                    count += 1
                for ii in xrange(ic[0]+1, ic[1]+1):
                    route_new[count] = rr[ii]
                    count += 1
                for ii in xrange(ic[2]+1, ic[0]+1):
                    route_new[count] = rr[ii]
                    count += 1
                    
                route[ir] = route_new                    
                dist[ir] += (dist_new - dist_old)
                
                found = True
        
        if (found != True):
            dist_new = city_dist(cities, rr[ic[0]],   rr[ic[1]+1]) +\
                       city_dist(cities, rr[ic[2]],   rr[ic[1]]) +\
                       city_dist(cities, rr[ic[0]+1], rr[ic[2]+1])
            if (dist_new < dist_old):
                if ((edges[(ir+1)%2][rr[ic[0]], 0]   != rr[ic[1]+1]) &
                    (edges[(ir+1)%2][rr[ic[0]], 1]   != rr[ic[1]+1]) &
                    (edges[(ir+1)%2][rr[ic[2]], 0]   != rr[ic[1]]) &
                    (edges[(ir+1)%2][rr[ic[2]], 1]   != rr[ic[1]]) &
                    (edges[(ir+1)%2][rr[ic[0]+1], 0] != rr[ic[2]+1]) &
                    (edges[(ir+1)%2][rr[ic[0]+1], 1] != rr[ic[2]+1]) ):
                    print 1
                    route_new = rr.copy();
                    
                    count = ic[0]+1
                    for ii in xrange(ic[1]+1, ic[2]+1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[1], ic[0], -1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[2]+1, ic[0]+1):
                        route_new[count] = rr[ii]
                        count += 1
                    
                    route[ir] = route_new                    
                    dist[ir] += (dist_new - dist_old)
                
                    found = True
        
        if (found != True):
            dist_new = city_dist(cities, rr[ic[0]],   rr[ic[2]]) +\
                       city_dist(cities, rr[ic[1]+1], rr[ic[0]+1]) +\
                       city_dist(cities, rr[ic[1]],   rr[ic[2]+1])
            if (dist_new < dist_old):
                if ((edges[(ir+1)%2][rr[ic[0]], 0]   != rr[ic[2]]) &
                    (edges[(ir+1)%2][rr[ic[0]], 1]   != rr[ic[2]]) &
                    (edges[(ir+1)%2][rr[ic[1]+1], 0] != rr[ic[0]+1]) &
                    (edges[(ir+1)%2][rr[ic[1]+1], 1] != rr[ic[0]+1]) &
                    (edges[(ir+1)%2][rr[ic[1]], 0]   != rr[ic[2]+1]) &
                    (edges[(ir+1)%2][rr[ic[1]], 1]   != rr[ic[2]+1]) ):
                    print 2
                    route_new = rr.copy();
                    
                    count = ic[0]+1
                    for ii in xrange(ic[2], ic[1], -1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[0]+1, ic[1]+1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[2]+1, ic[0]+1):
                        route_new[count] = rr[ii]
                        count += 1
                    
                    route[ir] = route_new                    
                    dist[ir] += (dist_new - dist_old)
                
                    found = True
                    
        if (found != True):
            dist_new = city_dist(cities, rr[ic[0]],   rr[ic[1]]) +\
                       city_dist(cities, rr[ic[0]+1], rr[ic[2]]) +\
                       city_dist(cities, rr[ic[1]+1], rr[ic[2]+1])
            if (dist_new < dist_old):
                if ((edges[(ir+1)%2][rr[ic[0]], 0]   != rr[ic[1]]) &
                    (edges[(ir+1)%2][rr[ic[0]], 1]   != rr[ic[1]]) &
                    (edges[(ir+1)%2][rr[ic[0]+1], 0] != rr[ic[2]]) &
                    (edges[(ir+1)%2][rr[ic[0]+1], 1] != rr[ic[2]]) &
                    (edges[(ir+1)%2][rr[ic[1]+1], 0] != rr[ic[2]+1]) &
                    (edges[(ir+1)%2][rr[ic[1]+1], 1] != rr[ic[2]+1]) ):
                    print 3
                    route_new = rr.copy();
                    
                    count = ic[0]+1
                    for ii in xrange(ic[1], ic[0], -1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[2], ic[1], -1):
                        route_new[count] = rr[ii]
                        count += 1
                    for ii in xrange(ic[2]+1, ic[0]+1):
                        route_new[count] = rr[ii]
                        count += 1
                    
                    route[ir] = route_new                    
                    dist[ir] += (dist_new - dist_old)
                
                    found = True

        if (found == True):
            # rebuild edges
            edges[ir][route[ir][0],    0] = 999999
            edges[ir][route[ir][Nc-1], 1] = 999999
            for ic in xrange(Nc-1):
                edges[ir][route[ir][ic],   1] = route[ir][ic+1]
                edges[ir][route[ir][ic+1], 0] = route[ir][ic]
                
            iter += 1
            score = int(np.max(dist))
            print score
            if (iter%checkpoint == 0):
                # when we checkpoint make sure tours are disjoint and valid
                print score, calc_score(cities, route)
                #assert(score == calc_score(cities, route))
                io.write_route(route, name + '_' + str(score))
        
        # switch to other route if it's longer
        if (dist[ir] < dist[(ir+1)%2]):
            ir = (ir+1)%2

    return route

def charge_start(cities, route):

    '''
    reroute starting point optimally
    '''
    Nc = cities.shape[0]
    new_route = [np.zeros(Nc, dtype=int),
                 np.zeros(Nc, dtype=int)]

    for ir in range(2):
        max_ind = -1
        max_dist = 0.0
        for ic in xrange(Nc-1):
            dist = city_dist(cities, route[ir][ic], route[ir][ic+1])
            if (dist > max_dist):
                max_dist = dist
                max_ind = ic
        print route[ir][max_ind], route[ir][max_ind+1] 
        count = 0
        for ic in xrange(max_ind+1,Nc):
            new_route[ir][count] = route[ir][ic]
            count += 1
        for ic in xrange(max_ind+1):
            new_route[ir][count] = route[ir][ic]
            count += 1
    
    return new_route

def contruct_lkh(cities):
    '''
    reads in a nearly optimal single tour produced by the LKH package
    and constructs a disjoint tour solution
    route 0: 0 1 2 3 4
    route 1: 0 3 1 4 2
    alternates between tours
    gives solutions in the 8.6M range
    '''

    Nc = cities.shape[0]
    assert(Nc > 0)
    
    rr = io.read_route_lkh()

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

    return myroute
