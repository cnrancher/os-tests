# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from __future__ import print_function

import time

import paramiko

SSH_KEY_PATH = '/opt/os-tests/assets/id_rsa'


def connection(ip, seconds):
    for _ in range(40):
        if seconds:
            time.sleep(seconds)
        else:
            time.sleep(10)
        try:
            ssh = paramiko.SSHClient()
            private_key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(hostname=ip,
                        username='rancher',
                        password='',
                        pkey=private_key)
            # The issue can solve 'SSH session not active'  https://github.com/paramiko/paramiko/issues/928
            if ssh.get_transport().active:
                break
        except:
            ssh.close()
    return ssh


def executor(client, command, seconds=100):
    assert (client and command is not None)
    stdin, stdout, stderr = client.exec_command(command, timeout=seconds)
    output = stdout.read().decode('utf-8')
    return output
