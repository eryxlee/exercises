# -*- coding: utf-8 -*-
#
# collections 练习和测试用例

import collections

# 非对象的defaultdict
g = collections.defaultdict(lambda: 1)
g['a'] += 1
print g['a']
# 2

# setdefault使用
dictionary = {}
mylist = dictionary.setdefault("list", [])
mylist.append("list_item")
print dictionary
# {'list': ['list_item']}
print mylist
# ['list_item']