# coding = utf-8
# Create date: 2018-10-31
# Author :Hailong


def test_write_files(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo cat /test'
    feed_back = 'console content'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_write_files.yml'.format(url=cloud_config_url))

    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    assert (feed_back in output)

    command_b = 'sudo cat /test2'
    feed_back_b = 'console content'

    stdin, stdout, stderr = client.exec_command(command_b, timeout=10)
    output_b = stdout.read().decode('utf-8')
    assert (feed_back_b in output_b)

    command_c = 'sudo system-docker exec ntp cat /test'
    feed_back_c = 'ntp content'
    stdin, stdout, stderr = client.exec_command(command_c, timeout=10)
    output_c = stdout.read().decode('utf-8')
    assert (feed_back_c in output_c)

    command_d = 'sudo system-docker exec syslog cat /test'
    feed_back_d = 'syslog content'
    stdin, stdout, stderr = client.exec_command(command_d, timeout=10)
    output_d = stdout.read().decode('utf-8')
    assert (feed_back_d in output_d)
