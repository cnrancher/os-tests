# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

import time


def test_mounts(ros_kvm_with_paramiko, cloud_config_url):
    command = 'cat /home/rancher/test | grep test'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_mounts.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    assert ('test' in output)

    command_mk = 'sudo mkfs.ext4 /dev/vdb && sudo cloud-init-execute'
    client.exec_command(command_mk, timeout=20)
    # Network delay
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command('mount', timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('/home/rancher/a' in output
            and '/home/rancher/b' in output
            and '/home/rancher/c' in output
            and '/home/rancher/d' in output)
