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
    httpd = make_server(
        '127.0.0.1',
        6543,
        app
    )
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."

    import webbrowser
    webbrowser.open('http://localhost:6543?name=myname&mail=w<e>@163.com&mail=you@163.com')

    httpd.handle_request()

