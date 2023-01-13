import socket

target_host = '0.0.0.0'
target_port = 9998

#create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send some data
client.sendto(b"HELLOOOOO", (target_host, target_port))

#receive some data
data, addr = client.recvfrom(4096)

print(data.decode())
client.close()
