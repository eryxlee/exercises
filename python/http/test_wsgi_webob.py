# -*- coding: utf-8 -*-

import webob

from wsgiref.simple_server import make_server


def app(environ, start_response):
    response_body = [
        '%s: %s' % (key, value) for key, value in sorted(environ.items())
        ]

    req = webob.Request(environ)

    name = req.params.get('name', '')
    mails = req.params.getall('mail')
    fullname = req.params.get('fullname', '')
    addresses = req.params.getall('address')

    response_body.append('name: %s' % name)
    response_body.append('mails: %s' % mails)
    response_body.append('fullname: %s' % fullname)
    response_body.append('addresses: %s' % addresses)

    response_body = '\n'.join(response_body)

    status = '200 OK'
    response_headers = [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(response_body)))
    ]
    start_response(status, response_headers)

    # webob得到的是unicode，但wsgiref只接收str，要转成str
    return [str(response_body)]


if __name__ == "__main__":
    import time
    import requests

    from threading import Thread


    class MyReq(Thread):
        def __init__(self):
            Thread.__init__(self)

        def run(self):
            time.sleep(10)
            params = dict(
                fullname='My Full Nmae',
                address=['123', '456']
            )
            res = requests.post("http://127.0.0.1:6543?name=myname&mail=w<e>@163.com&mail=you@163.com", params)
            print res.text


    httpd = make_server(
        '127.0.0.1',
        6543,
        app
    )

    req = MyReq()
    req.start()

    httpd.handle_request()
