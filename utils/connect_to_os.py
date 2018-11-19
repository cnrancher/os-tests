# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from __future__ import print_function

import time

import paramiko


def connection(ip):
    for _ in range(30):
        time.sleep(10)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(hostname=ip,
                        username='rancher',
                        password='')
            if ssh.get_transport().active:
                break
        except:
            ssh.close()

    return ssh


def executor(client, command, seconds=40):
    assert (client and command is not None)
    stdin, stdout, stderr = client.exec_command(command, timeout=seconds)
    output = stdout.read().decode('utf-8')
    return output
