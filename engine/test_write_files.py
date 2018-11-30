# coding = utf-8
# Create date: 2018-10-31
# Author :Hailong


def test_write_files(ros_kvm_init, cloud_config_url):
    command = 'sudo cat /test'
    feed_back = 'console content'
    kwargs = dict(cloud_config='{url}test_write_files.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    assert (feed_back in output)

    command_b = 'sudo cat /test2'
    feed_back_b = 'console content'

    stdin, stdout, stderr = client.exec_command(command_b, timeout=60)
    output_b = stdout.read().decode('utf-8')
    assert (feed_back_b in output_b)

    command_c = 'sudo system-docker exec ntp cat /test'
    feed_back_c = 'ntp content'
    stdin, stdout, stderr = client.exec_command(command_c, timeout=60)
    output_c = stdout.read().decode('utf-8')
    assert (feed_back_c in output_c)

    command_d = 'sudo system-docker exec syslog cat /test'
    feed_back_d = 'syslog content'
    stdin, stdout, stderr = client.exec_command(command_d, timeout=60)
    output_d = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back_d in output_d)
