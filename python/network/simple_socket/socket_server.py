import socket
import sys
from thread import *

HOST = ""
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'After create socket'

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind error. %s' % msg
    sys.exit()

print 'After bind'

s.listen(10)
print 'After listening'


def clientthread(conn):
    conn.send('Welcome to my server, type something plz\n')
    while 1:
        data = conn.recv(1024).strip()
        print 'len=' + str(len(data))
        reply = 'OK...' + data + '...'
        if not data:
            break
        conn.sendall(reply)
    conn.close()

while 1:
    conn, addr = s.accept()
    print 'Connected from ' + addr[0] + ':' + str(addr[1])

    start_new_thread(clientthread, (conn,))

s.close()

