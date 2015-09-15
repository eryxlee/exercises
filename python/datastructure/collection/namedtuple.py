# -*- coding: utf-8 -*-
#
# collections 练习和测试用例

import json
import simplejson
import collections

# 生成namedtuple 对象，并导出
LightObject = collections.namedtuple('LightObject', ['shortname', 'otherprop'])
obj = LightObject('short name', 'some other things')

print(obj)
# LightObject(shortname='short name', otherprop='some other things')
print(json.dumps(obj))
# ["short name", "some other things"]
print(simplejson.dumps(obj, namedtuple_as_object=True))
# {"shortname": "short name", "otherprop": "some other things"}

