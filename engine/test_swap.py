# coding = utf-8
# Create date: 2018-11-09
# Author :Bowen Lee

import time


def test_swap(ros_kvm_with_paramiko, cloud_config_url):
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_swap.yml'.format(url=cloud_config_url))
    client.exec_command('sudo mkswap /dev/vdb && sudo cloud-init-execute', timeout=10)
    # Network delay
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command('cat /proc/swaps | grep /dev/vdb', timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('/dev/vdb' in output)
