import numpy as np
import innout as io
import route

cities = io.load_cities()
rr = io.load_route('optstart_7479503.csv')
#rr, sc = route.NN(cities, start=np.array([137433, 145655]))
#io.write_route(route=rr, name='optstart')
rr_new = route.opt2(cities, route=rr, look_ahead=20000, name='optstart', checkpoint=250)
