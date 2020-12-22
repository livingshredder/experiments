import os

def resolve_all() -> str:
    data = ''
    for path, _, files in os.walk('convert'):
        for file in files:
            with open(os.path.join(path, file), 'r') as f:
                data += '<|startoftext|>\n'
                data += f.read()

                if not data.endswith('\n'):
                    data += '\n'
                data += '<|endoftext|>\n'
    return data

with open('data/input.txt', 'w') as f:
    f.write(resolve_all())
