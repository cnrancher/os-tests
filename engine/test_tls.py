# coding = utf-8
# Create date: 2018-10-31
# Author :Hailong
# Editor:Bowen Lee


def test_tls(ros_kvm_with_paramiko, cloud_config_url):
    command = 'set -e -x && sudo ros tls gen && docker --tlsverify version'
    feed_back = 'Client'
    client = ros_kvm_with_paramiko(cloud_config='{url}/test_tls.yml'.format(url=cloud_config_url))
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    # Must be save in local constant
    output_content = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output_content)
