# coding = utf-8
# Create date: 2018-11-05
# Author :Hailong


def test_start_commands(ros_kvm_with_paramiko, cloud_config_url):
    command = 'ls /home/rancher | grep "test[0-5]"  | wc -l'
    feed_back = '5'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_start_commands.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    assert (feed_back in output)

    command_b = 'docker ps | grep busybox'
    feed_back_b = 'busybox'
    stdin, stdout, stderr = client.exec_command(command_b, timeout=60)
    output_b = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back_b in output_b)
