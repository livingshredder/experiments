from pprint import pprint
from importlib import import_module
import sys


def decode_data(data):
    mod = 'pyroute2.netlink.rtnl.rtmsg.rtmsg'
    mod = mod.replace('/', '.')

    mstrs = mod.split('.')
    package = '.'.join(mstrs[:-1])
    module = mstrs[-1]
    mname = import_module(package)
    met = getattr(mname, module)

    offset = 0
    while offset < len(data):
        msg = met(data[offset:])
        msg.decode()
        #print(hexdump(msg.data))
        pprint(msg)
        #print('.' * 40)
        offset += msg['header']['length']

RD = bytearray.fromhex(sys.argv[1])
decode_data(RD)
