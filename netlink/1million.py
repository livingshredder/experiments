import sys
from pyroute2 import IPRoute


ADDR_PREFIX = "10.50"

RANGE_1 = 16
RANGE_2 = 255
RANGE_3 = 255

ROUTE_TOTAL = RANGE_1*RANGE_2*RANGE_3

def route_oper(ipr, oper, addr):
    return ipr.route(oper,
        dst=addr,
        mask=32,
        gateway="10.2.0.2",
        prefsrc="185.167.182.4",
        oif=6,
        metrics={
            "attrs": [
                ["RTA_PRIORITY", 32],
            ]
        }
    )


def add_routes():
    print(f'adding {ROUTE_TOTAL} routes')
    with IPRoute() as ipr:
        for x in range(RANGE_1):
            for y in range(RANGE_2):
                for z in range(RANGE_3):
                    route_oper(ipr, 'add', f'10.{str(50+x)}.{y}.{z}')
        

def del_routes():
    print(f'deleting {ROUTE_TOTAL} routes')
    with IPRoute() as ipr:
        for x in range(RANGE_1):
            for y in range(RANGE_2):
                for z in range(RANGE_3):
                    route_oper(ipr, 'del', f'10.{str(50+x)}.{y}.{z}')

oper = sys.argv[1]

if oper == "add":
    add_routes()
elif oper == "del":
    del_routes()
else:
    raise Exception("invalid operation")
