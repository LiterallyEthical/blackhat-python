import paramiko
import getpass


def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()  # creating the SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(ip, port=port, username=user, password=passwd)

    # unpacking tuple to stdout and stderr
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('---Output---')
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    # user = getpass.getuser() #gets username from the current environment
    # since our username is different on the two machines, we explicitly ask for the username
    user = input('Username: ')
    password = getpass.getpass()  # prompts for a password

    # Asking for input and set the defualt for otherwise
    ip = input('Enter server IP:') or '192.168.1.39'
    port = input('Enter port or <CR>: ') or 22
    cmd = input('Enter command or <CR>:') or 'id'
    ssh_command(ip, port, user, password, cmd)
