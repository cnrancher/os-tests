# coding = utf-8
# Create date: 2018-10-31
# Author :Hailong
# Editor:Bowen Lee


def test_tls(ros_kvm_init, cloud_config_url):
    command = 'set -e -x && sudo ros tls gen && docker --tlsverify version'
    feed_back = 'Client'
    kwargs = dict(cloud_config='{url}/test_tls.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    # Must be save in local constant
    output_content = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output_content)
