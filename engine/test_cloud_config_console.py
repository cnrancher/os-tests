# coding = utf-8
# Create date: 2018-11-12
# Edit date: 2018-11-19
# Author :Bowen Lee


def test_cloud_config_console(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_cloud_config_console.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command('sudo ros console list | grep default', timeout=60)
    output = stdout.read().decode('utf-8')
    assert ('default' in output and 'disabled' in output)

    stdin, stdout, stderr = client.exec_command('sudo ros console list | grep debian', timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('debian' in output and 'current' in output)
