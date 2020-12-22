from itertools import cycle
import base64

def obfuscate(text, key):
    return base64.b64encode(bytes([a^b for (a,b) in zip(bytes(text, 'utf-8'), cycle(bytes(key, 'utf-8')))])).decode()
def deobfuscate(enc, key):
    return bytes([ a^b for (a,b) in zip(bytes(base64.b64decode(enc)), cycle(bytes(key, 'utf-8')))]).decode()

text = input('Text to encode: ')
encoded = obfuscate(text, 'baisjdwjdiww')

print(encoded)
print(deobfuscate(encoded, 'baisjdwjdiww'))
