
# http://my.oschina.net/limodou/blog/170391

import sys
sys.path.insert(0, '..')
from importtest2 import x
print id(x)

from __init__ import x
print id(x)
