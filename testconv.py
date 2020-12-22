import sys
import math

grains = int(sys.argv[1])
ftpersec = int(sys.argv[2])

def lbstokg(x):
    return x*(1/2.2)

def grains_to_lb(grains):
    return (0.002285*(grains)/16)

def grains_to_kg(grains):
    return lbstokg(grains_to_lb(grains))

print(math.ceil(ftpersec*12*(grains_to_kg(grains))*3.5))