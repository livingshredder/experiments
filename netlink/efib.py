from pyroute2 import IPRoute
#import pprint

RTM_F_CLONED = 0x200

with IPRoute() as ipr:
    routes = ipr.route('dump')
    print('ok')
    for i in range(len(routes)):
        route = routes[i]
        if not (route['flags'] & RTM_F_CLONED):
            continue
        print(route)
        #pprint.pprint(route)