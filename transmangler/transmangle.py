import sys
import random
import string
from googletrans import Translator

finnish = [
    "bugle", "trumpet", "signal horn", "dirty", "bongpelz", "perkele", "clock", "bell", "devil", "shit", "bröther"
    "cursed", "horn", "orchestra", "drummer", "boi", "doorbell", "doot", "lit", "bad", "special", "kisser", "uber röck", 
    "glue boi", "moist", "mole", "doobie", "fat", "thicc", "nice", "existential",
    "funny", "unholy", "war", "machine", "pump", "turbine", "reactor", "singularity", "idiot", "perkele", "royale"
]

finnishpasses = 1 # Finnish passes
frenchpasses = 1  # French passes
germanpasses = 1  # German passes
chinesepasses = 1 # Chinese passes
dutchpasses = 1   # Dutch passes
swedishpasses = 1 # Swedish passes

weirdness = 0.0   # 0 to 1
loops = 10

umlautability = weirdness * 0.3
corruptability = weirdness * 0.02
randomstuff = weirdness * 0.3

lastRand = None
lastWordWasEOS = True
lastWord = None
usedWords = []

mode = None
tfile = None

if len(sys.argv) > 1:
    tfile = sys.argv[1]
if len(sys.argv) > 2:
    mode = sys.argv[2]

if tfile is None:
    tfile = "bell.txt"

if mode is None:
    mode = "english"

def decide(probability):
    return random.random() < probability

def upperconv(upper, l):
    if upper:
        return l.upper()
    else:
        return l

def randomWord():
    global lastRand
    result = random.choice(finnish)
    if result is lastRand:
            result = randomWord()
    lastRand = result
    return result

def fixGrammar(text):
    lastWordWasEOS = True
    ltext = ""

    words = text.split(' ')
    for word in words:
        if lastWordWasEOS:
            lastWordWasEOS = False
            word = word.capitalize()
        else:
            word = word.lower()

        for l in word:
            if l == ".":
                lastWordWasEOS = True

        ltext = ltext + word + " "

    return ltext


def mangleText(text):
    global lastWord
    global usedWords
    words = text.split(' ')
    ltext = ""
    for word in words:
        randWord = randomWord()
        if decide(randomstuff) and randWord not in usedWords and lastWord not in finnish:
            usedWords.append(randWord)
            ltext = ltext + randWord + " " 
        elif lastWord != word:
            lastWord = word
            ltext = ltext + mangleWord(word) + " "
        
    return ltext

def mangleWord(word):
    global lastWordWasEOS

    lstr = ""
    for l in word:
        upper = l.istitle()
        if decide(umlautability):
            if l is "a":
                l = "ä"
            elif l is "o":
                l = "ö"
            elif l is "u":
                l = "ü"
            l = upperconv(upper, l)
        elif decide(corruptability):
            l = random.choice(string.ascii_letters + " ").lower()
        lstr = lstr + l
    return lstr

def transMangleDefine(text, lang, passes):
    for x in range(passes):
        print("Transmangle pass " + str(x) + " for lang " + lang + ".")
        text = translator.translate(text, lang, "en").text
        text = translator.translate(text, "en", lang).text
    return text

def transMangle(text):
    text = transMangleDefine(text, "fi", finnishpasses)
    text = transMangleDefine(text, "fr", frenchpasses)
    text = transMangleDefine(text, "de", germanpasses)
    text = transMangleDefine(text, "zh-TW", chinesepasses)
    text = transMangleDefine(text, "nl", dutchpasses)
    text = transMangleDefine(text, "sv", swedishpasses)
    return text

with open(tfile, 'r') as cfile:
    text = cfile.read().rstrip()

translator = Translator()

print("Initializing Transmangler")

for i in range(loops):
    print("Finnishification...")
    text = translator.translate(text, "fi", "en").text
    print("Running Text Mangler")
    text = mangleText(text)
    print("Running Translation Mangler")
    text = transMangle(text)
    print("Translating back to English")
    text = translator.translate(text, "en", "fi").text
    print("Running Grammar Fixer")
    text = fixGrammar(text)
    print("Translating to desired language")
    if mode == "finnish":
        text = translator.translate(text, "fi", "en").text
    elif mode == "german":
        text = translator.translate(text, "de", "en").text
    elif mode == "latin":
        text = translator.translate(text, "la", "en").text
    elif mode == "french":
        text = translator.translate(text, "fr", "en").text
    elif mode == "chinese":
        text = translator.translate(text, "zh-TW", "en").text
    elif mode == "dutch":
        text = translator.translate(text, "nl", "en").text
    elif mode == "swedish":
        text = translator.translate(text, "sv", "en").text

print(text)
