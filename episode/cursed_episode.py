import wikipedia
import json
import os
import re

global_words = [
    'reactor',
    'nuclear',
    'overheat',
    'critical',
    'explosion',
    'explode',
    'meltdown',
    'melt down',
    'deep space',
    'jettison'
]

with open('episode_list.txt', 'r') as f:
    episode_list = f.readlines()
    episode_list = [x.strip() for x in episode_list]

episode_cache = {}
if os.path.exists('episode_cache.json'):
    with open('episode_cache.json', 'r') as f:
        episode_cache = json.load(f)

results = {}
scores = {}
for episode in episode_list:
    results[episode] = {}
    if episode not in episode_cache:
        print(f'Page \"{episode}\" not in cache, downloading.')
        episode_cache[episode] = wikipedia.page(episode).content

    score = []
    for word in global_words:
        matches = [m.start() for m in re.finditer(word, episode_cache[episode])]
        #for match in matches:
        #    print(episode_cache[episode][(match - 50):(match + 50)])
        if len(matches) > 0:
            score.append(word)
    if len(score) > 0:
        scores[episode] = score

for pair in scores.items():
    print(pair)

with open('episode_cache.json', 'w') as f:
    json.dump(episode_cache, f)
