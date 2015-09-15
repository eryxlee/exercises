import socket, select

if __name__ == '__main__':

    CONN_LIST = []
    RECV_BUFF = 4096
    PORT = 8080

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    CONN_LIST.append(server_socket)

    print 'Listen on port %d' % PORT

    while 1:
        read_sockets, write_sockets, error_sockets = select.select(CONN_LIST, [], [])
        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONN_LIST.append(sockfd)
                print "client (%s, %s) connected" % addr
            else:
                try:
                    data = sock.recv(RECV_BUFF)
                    if data:
                        sock.send('OK...' + data)
                except:
                    broadcast_data(sock, "Client (%s, %s) if offline" % addr)
                    print "Client (%s, %s) is offline" % addr
                    sock.close()
                    CONN_LIST.remove(sock)
                    continue
    server_socket.close()

