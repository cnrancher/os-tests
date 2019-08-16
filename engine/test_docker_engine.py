# coding = utf-8
# Create date: 2019-8-16
# Author :Hailong


def test_docker_engine(ros_kvm_init, cloud_config_url):
    kwargs = dict(is_install_to_hard_drive=True, cloud_config='{url}test_docker_engine.yml'.format(url=cloud_config_url))
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    command_ros_engine = 'sudo ros engine list | grep current'
    stdin, stdout, stderr = client.exec_command(command_ros_engine, timeout=10)
    output_ros_engine = stdout.read().decode('utf-8')
    assert ('docker-19.03.1' in output_ros_engine)

    command_docker_info = 'docker info'
    stdin, stdout, stderr = client.exec_command(command_docker_info, timeout=10)
    output_docker_info = stdout.read().decode('utf-8')
    assert ('19.03.1' in output_docker_info)

