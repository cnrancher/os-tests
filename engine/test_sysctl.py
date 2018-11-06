# coding = utf-8
# Create date: 2018-11-05
# Author :Hailong


def test_sysctl(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo cat /proc/sys/kernel/domainname'
    feed_back = 'test'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_sysctl.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8').replace('\n', '')
    assert (feed_back == output)

    command_b = 'sudo cat /proc/sys/dev/cdrom/debug'
    feed_back_b = '1'
    stdin, stdout, stderr = client.exec_command(command_b, timeout=10)
    output_b = stdout.read().decode('utf-8').replace('\n', '')
    client.close()
    assert (feed_back_b == output_b)
