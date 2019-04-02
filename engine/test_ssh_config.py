# coding = utf-8
# Create date: 2019-4-2
# Author: Hailong
# Issue: https://github.com/rancher/os/issues/2581

from utils.connect_to_os import executor, connection


def test_check_ssh_config_when_reboot(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    ip = tuple_return[1]
    output = executor(client, 'sudo ros console list | grep -v default')
    list_of_console = output.split('\n')
    list_of_console.pop(-1)

    console_list = []

    for console in list_of_console:
        console_list.append(console.split(' ')[1])

    for console_v in console_list:
        client = connection(ip, None)
        executor(client, 'sudo ros console switch -f {console_version}'.format(console_version=console_v))
        client = connection(ip, None)
        executor(client, 'sudo reboot')
        client = connection(ip, None)
        output_get_current_console = executor(client, 'sudo ros console list | grep current')

        assert (console_v in output_get_current_console)

        ssh_config_items = ['UseDNS no', 'PermitRootLogin no', 'ServerKeyBits 2048', 'AllowGroups docker']
        for ssh_config_item in ssh_config_items:
            output_ssh_config = executor(client, 'grep "^{ssh_config_item}" /etc/ssh/sshd_config | wc -l'.format(
                ssh_config_item=ssh_config_item)).replace('\n', '')

            assert (int(output_ssh_config) <= 1)
