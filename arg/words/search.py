import json

def load_words():
    with open('words_alpha.txt') as word_file:
        valid_words = set(word_file.read().split())

    return valid_words


found_words = []
if __name__ == '__main__':
    words = load_words()
    for word in words:
        wordc = word.lower()
        if len(wordc) != 6:
            continue
        if wordc[1] != 'c' or wordc[2] != 'b':
            continue
        found_words.append(word)
    
for word in found_words:
    print(word)
print(f'{len(found_words)} words')