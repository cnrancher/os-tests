# coding = utf-8
# Create date: 2018-11-6
# Author :Bowen Lee


def test_lenient_service_parsing(ros_kvm_init, cloud_config_url):
    command = 'sudo system-docker ps -a | grep test-parsing'
    kwargs = dict(cloud_config='{url}test_lenient_service_parsing.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('test-parsing' in output)
