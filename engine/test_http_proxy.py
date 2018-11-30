# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee


def test_http_proxy(ros_kvm_init, cloud_config_url):
    command = 'sudo system-docker inspect docker'
    config_http = 'HTTP_PROXY=invalid'
    config_https = 'HTTPS_PROXY=invalid'
    config_no_proxy = 'NO_PROXY=invalid'
    kwargs = dict(cloud_config='{url}test_http_proxy.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ((config_http in output)
            and (config_https in output)
            and (config_no_proxy in output))
