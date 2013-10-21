

#
#cat t.txt|python token.py | sort | python reduce.py

import sys

for line in sys.stdin:
    print ''.join(sorted(line.rstrip())), line,