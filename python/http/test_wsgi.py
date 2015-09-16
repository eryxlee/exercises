# -*- coding: utf-8 -*-

from cgi import escape
from urlparse import parse_qs
from wsgiref.simple_server import make_server


def app(environ, start_response):
    response_body = [
        '%s: %s' % (key, value) for key, value in sorted(environ.items())
        ]

    # 解析GET参数
    params_get = parse_qs(environ['QUERY_STRING'])

    # 返回单个值
    name = params_get.get('name', [''])[0]
    # 返回多个值
    mails = params_get.get('mail', [])

    name = escape(name)
    mails = [escape(mail) for mail in mails]

    response_body.append('name: %s' % name)
    response_body.append('mails: %s' % mails)

    # 解析POST参数
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    request_body = environ['wsgi.input'].read(content_length)
    params_post = parse_qs(request_body)

    # 获取数据
    fullname = params_post.get('fullname', [''])[0]
    addresses = params_post.get('address', [])

    fullname = escape(fullname)
    addresses = [escape(addr) for addr in addresses]

    response_body.append('fullname: %s' % fullname)
    response_body.append('addresses: %s' % addresses)

    response_body = '\n'.join(response_body)

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)

    # 注意，这里最好返回一个包含一个字符串的数组。因为是字符串response_body也是可迭代的，它的每一次迭代只能得到1 byte的数据量。
    # 这也意味着每一次只向客户端发送1 byte的数据，直到发送完毕为止，这会导致WSGI程序的响应变慢。
    return [response_body]


if __name__ == "__main__":
    import time
    import requests

    from threading import Thread


    class MyReq(Thread):
        def __init__(self):
            Thread.__init__(self)

        def run(self):
            time.sleep(5)
            params = dict(
                fullname='My Full Nmae',
                address=['123', '456']
            )
            res = requests.post("http://127.0.0.1:6543?name=myname&mail=we@163.com&mail=you@163.com", params)
            print res.text


    httpd = make_server(
        '127.0.0.1',
        6543,
        app
    )

    req = MyReq()
    req.start()

    httpd.handle_request()
