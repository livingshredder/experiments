#hexin = "37DB 5069 64 F8 6C 30 76 A3 1A B2".split(" ")
hexin = 0x37DB506964F86C3076A31AB2
hexout = hexin // 0xB2

#out = ""
result = hexout.to_bytes(100, 'big').decode("ascii")


#"50 73 91 9B AA 26"
#"50 55 4E 41 49 4E 45 4E 54 55"

#for item in hexin:
 #   hx = int("0x" + item, 16)
  #  out += chr(hx / 0xB2)

print(result)