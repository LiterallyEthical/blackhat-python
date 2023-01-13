import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT)) #The bind() method of Python's socket class assigns an IP address and a port number to a socket instance.
    server.listen(5) #It specifies the number of unaccepted connections that the system will allow before refusing new connections.
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        client, address = server.accept() #unpacking tuple to client as a socket object and address to address variable
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client, )) #creating a thread, passing a function and it's arguments as a parameter
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock: # with .. as works like a try-catch block, after the execution of block will be completed it will close the connection
        request = sock.recv(1024) #If no error occurs, recv returns the bytes received. 
        print(f'[*] Received: {request.decode("utf-8")}') #Decoding the  bytes that reveived
        sock.send(b'ACK')

if __name__ == '__main__':
    main()
        


    
