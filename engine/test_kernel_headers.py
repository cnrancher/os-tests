# coding = utf-8
# Create date: 2018-11-6
# Author :Bowen Lee


def test_kernel_headers(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo system-docker inspect kernel-headers'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_kernel_headers.yml'.format(url=cloud_config_url))

    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('kernel-headers' in output)
