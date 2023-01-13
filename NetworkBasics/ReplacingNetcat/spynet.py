import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    # Remove spaces at the beginning and at the end of the string:
    cmd = cmd.strip()
    if not cmd:
        return

    # Run command with arguments and return its output.
    output = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.STDOUT)
    # To also capture standard error in the result, use stderr=subprocess.STDOUT:
    # shlex.split() is designed to work like the shell's split mechanism.
    return output.decode()


class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # creating a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # SO_REUSEADDR Specifies that the rules used in validating addresses supplied to bind() should allow reuse of
        # local addresse and this in a boolean option
        # To set options at the socket level, specify the level argument as SOL_SOCKET

    def run(self):
        if self.args.listen:  # setting up a listener
            self.listen()  # call the listen method
        else:
            self.send()  # otherwise, calling the send method

    def send(self):
        # setup a connection to target
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            # if we have a buffer, sends it to target first
            self.socket.send(self.buffer)
        # Then we set up a try/catch block so we can manually close the connection with CTRL-C
        try:
            while True:  # starting a loop to receive data
                recv_len = 1
                response = ''
                while recv_len:
                    # receiving data in byte format
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    # decoding the received data to a string an concat it to the response
                    response += data.decode()
                    if recv_len < 4096:
                        break  # If there is no more data, we break out of the loop
                if response:
                    print(response)
                    buffer = input('> ')  # pause to get interactive input
                    buffer += '\n'
                    self.socket.send(buffer.encode())  # sending the input
        except KeyboardInterrupt:
            print('User terminated!')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        # This denotes maximum number of connections that can be queued for this socket by the operating system
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket, ))
            # passing the connected socket to the handle method
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            # sending the output to the client
            client_socket.send(output.encode())
        elif self.args.upload:
            file_buffer = b''  # b represents the bytes format
            while True:  # setting up a loop
                # receives data until no more data coming in
                data = client_socket.recv(4096)
                if data:  # if there is data it is going to be concated to file_buffer
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as file:  # wb means write and binary
                file.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''  # creating a empty buffer to send
            while True:
                try:
                    # waiting for interactive input
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():  # creating a loop that recevies a message until the \n char
                        cmd_buffer += client_socket.recv(64)
                    # execute the command and assing it outpu as a response
                    response = execute(cmd_buffer.decode())
                    if response:
                        # returning the output to the sender
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='SpyNet (Networking Tool)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            '''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=badfile.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute a command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''
        ))

    parser.add_argument('-c', '--command',
                        action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int,
                        default=5555, help='specified port')
    parser.add_argument(
        '-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''  # invoke the NetCat object with an empty buffer string
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())  # Creating a NetCat object
    nc.run()
