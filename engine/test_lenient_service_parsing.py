# coding = utf-8
# Create date: 2018-11-6
# Author :Bowen Lee


def test_lenient_service_parsing(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo system-docker ps -a | grep test-parsing'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_lenient_service_parsing.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('test-parsing' in output)
