import sys

last_token = None
for line in sys.stdin:
    token, word = line.strip().split()
    if last_token and last_token != token:
        print
    print word,
    last_token = token