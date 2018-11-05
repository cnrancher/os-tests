# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee


def test_environment(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo system-docker inspect env | grep A=A'
    feed_back = 'A=A'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_environment.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    assert (feed_back in output)

    command_b = 'sudo system-docker inspect env | grep BB=BB'
    feed_back_b = 'BB=BB'
    stdin, stdout, stderr = client.exec_command(command_b, timeout=10)
    output_b = stdout.read().decode('utf-8')
    assert (feed_back_b in output_b)

    command_c = 'sudo system-docker inspect env | grep BC=BC'
    feed_back_c = 'BC=BC'
    stdin, stdout, stderr = client.exec_command(command_c, timeout=10)
    output_c = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back_c in output_c)
