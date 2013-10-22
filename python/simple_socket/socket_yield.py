import socket


def receive_connections(addr):
  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
  s.bind(addr)
  s.listen(5)
  while True:
    client = s.accept()
    print client
    yield client

for c,a in receive_connections(("",9000)):
  print a
  c.send("Hello World\n")
  c.close()