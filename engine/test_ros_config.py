# coding = utf-8
# Create date: 2018-11-07
# Author :Hailong


def test_ros_config(ros_kvm_init, cloud_config_url):
    fb_cc_hostname = 'hostname3'
    command_cc_hostname = 'sudo ros config get hostname'
    kwargs = dict(cloud_config='{url}test_ros_config.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command_cc_hostname, timeout=60)
    output_cc_hostname = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cc_hostname == output_cc_hostname)

    # Customize hostname and verify
    fb_cli_hostname = 'rancher-test'
    command_cli_hostname = 'sudo ros config set hostname {}'.format(fb_cli_hostname)
    stdin, stdout, stderr = client.exec_command(command_cli_hostname + '&&' + command_cc_hostname, timeout=60)
    output_cli_hostname = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cli_hostname == output_cli_hostname)

    # Verify that rancher.log
    fb_cc_log = 'true'
    command_cc_log = 'sudo ros config get rancher.log'
    stdin, stdout, stderr = client.exec_command(command_cc_log, timeout=60)
    output_cc_log = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cc_log == output_cc_log)

    fb_cli_log = 'false'
    command_cli_log = 'sudo ros config set rancher.log {}'.format(fb_cli_log)
    stdin, stdout, stderr = client.exec_command(command_cli_log + '&&' + command_cc_log, timeout=60)
    output_cli_log = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cli_log == output_cli_log)

    # Verify that rancher.debug
    fb_cc_debug = 'false'
    command_cc_debug = 'sudo ros config get rancher.debug'
    stdin, stdout, stderr = client.exec_command(command_cc_debug, timeout=60)
    output_cc_debug = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cc_debug == output_cc_debug)

    fb_cli_debug = 'true'
    command_cli_debug = 'sudo ros config set rancher.debug {}'.format(fb_cli_debug)
    stdin, stdout, stderr = client.exec_command(command_cli_debug + '&&' + command_cc_debug, timeout=60)
    output_cli_debug = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cli_debug == output_cli_debug)

    # Customize rancher.network.dns.search and verify
    fb_cli_dns = '- a\n- b'
    command_cli_set_dns = 'sudo ros config set rancher.network.dns.search "[a,b]"'
    command_cli_get_dns = 'sudo ros config get rancher.network.dns.search'
    stdin, stdout, stderr = client.exec_command(command_cli_set_dns + '&&' + command_cli_get_dns, timeout=60)
    output_cli_dns = stdout.read().decode('utf-8')
    assert (fb_cli_dns in output_cli_dns)

    fb_cli_dns_empty = '[]'
    command_cli_set_dns_empty = 'sudo ros config set rancher.network.dns.search "{}"'.format(fb_cli_dns_empty)
    stdin, stdout, stderr = client.exec_command(command_cli_set_dns_empty + '&&' + command_cli_get_dns, timeout=60)
    output_cli_dns_empty = stdout.read().decode('utf-8').replace('\n', '')
    assert (fb_cli_dns_empty == output_cli_dns_empty)

    # Verify "PRIVATE KEY"
    fb_cli_private_key = 'PRIVATE KEY'
    output_cli_get_export = _get_export(client)
    assert (fb_cli_private_key not in output_cli_get_export)

    output_cli_get_private_export = _get_private_export(client)
    assert (fb_cli_private_key in output_cli_get_private_export)

    output_cli_get_full_export = _get_private_and_full_export(client)
    assert (fb_cli_private_key in output_cli_get_full_export)

    # Verify udev
    fb_cli_udev = 'udev'
    output_cli_get_export = _get_full_export(client)
    assert (fb_cli_udev in output_cli_get_export)

    # Verify ntp
    fb_cli_ntp = 'ntp'
    output_cli_get_export = _get_private_and_full_export(client)
    assert (fb_cli_ntp in output_cli_get_export)

    # Verify labels
    fb_cli_labels = 'labels'
    output_cli_get_export = _get_full_export(client)
    client.close()
    assert (fb_cli_labels in output_cli_get_export)


def _get_export(client):
    command = 'sudo ros config export'
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    return output


def _get_private_export(client):
    command = 'sudo ros config export --private'
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    return output


def _get_full_export(client):
    command = 'sudo ros config export --full'
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    return output


def _get_private_and_full_export(client):
    command = 'sudo ros config export --private --full'
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    return output
