# -*- coding: utf-8 -*-
#
# requests 模块的一些联系和测试用例。
#
# HTTP Request & Response Service: http://httpbin.org/

import shutil
import requests
import tempfile

STREAM_URL = "http://httpbin.org/stream-bytes/2048"

r = requests.get(STREAM_URL, stream=True)
if r.status_code == 200:
    with tempfile.TemporaryFile() as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

r = requests.get(STREAM_URL, stream=True)
if r.status_code == 200:
    with tempfile.TemporaryFile() as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            print len(chunk)  # 指定了块大小

r = requests.get(STREAM_URL, stream=True)
if r.status_code == 200:
    with tempfile.TemporaryFile() as f:
        for chunk in r:
            f.write(chunk)
            print len(chunk)   # 未指定。默认为128
