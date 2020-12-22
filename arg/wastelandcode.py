import random
from random import shuffle

c_answer = "OTHERSIDE"
c_rightperson = "ALBERTHARTMAN"
c_question = "WHATCONNECTSALLTHESE"
c_truth = "IFYOUKNOWITJUSTSAYITTHENYOUGETITREDRAVEN"

ciphers = {
    "A": c_answer,
    "R": c_rightperson,
    "Q": c_question,
    "T": c_truth
}

mode = "encode"
text = "ANSWER LIVE UNDERGROUND"
keylist = list(ciphers.keys())

def encode(text):
    output = ""

    # use a random cipher that has a character we can use
    for char in text:
        if char == " ":
            output += char
            continue

        ctmp = keylist.copy()
        match = None
        cipher = None
        for i in range(0, len(keylist)):
            cipher = random.choice(ctmp)
            tmp = ciphers[cipher]

            if char not in tmp:
                # or try another cipher
                ctmp.remove(cipher)
                continue

            match = tmp.index(char)
        if match is None:
            print("Could not find a matching character for " + char + " in any cipher.")
            exit(1)
        output += cipher + "." + str(match + 1) + " "
    return output

def decode(text):
    output = ""
    strs = text.split(" ")
    for block in strs:
        if block == "":
            output += block
            continue

        sub = block.split(".")
        print(sub)
        cipher = ciphers[sub[0]]
        match = cipher[int(sub[1]) - 1]
        if match is None:
            print("Failed to match block " + block)
            exit(1)
        output += match
    return output

encoded = encode(text)
print(encoded)
#print(decode(encoded))