# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee


def test_dhcp_hostname(ros_kvm_init, cloud_config_url):
    command = 'hostname'
    feed_back = 'rancher'
    kwargs = dict(cloud_config='{url}test_dncp_hostname.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    assert (feed_back in output)

    command_etc = 'cat /etc/hosts'
    stdin, stdout, stderr = client.exec_command(command_etc, timeout=60)
    output_etc = stdout.read().decode('utf-8')
    client.close()
    assert (output_etc in output_etc)
