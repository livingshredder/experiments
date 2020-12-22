binin = "001000000 001000000 010100100 011011110 010110000 010101000 001111010".split(" ")
binout = ""
ascout = ""

for item in binin:
    ascout += chr(255-int(item,2))

print(ascout)