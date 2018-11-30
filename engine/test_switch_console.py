# coding = utf-8
# Create date: 2018-11-20
# Author :Bowen Lee

from utils.connect_to_os import executor, connection


def test_switch_console(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    ip = tuple_return[1]
    output = executor(client, 'sudo ros console list')
    list_of_console = output.split('\n')

    list_of_console.pop(-1)

    current_version = None

    list_console_v = []

    for number, console_v in enumerate(list_of_console):
        if console_v.startswith('current'):
            current_version = console_v.split(' ')[2]
        else:
            list_console_v.append(console_v.split(' ')[1])

    for console_v in list_console_v:
        client = connection(ip, None)

        executor(client, 'sudo ros console switch -f {console_version}'.format(console_version=console_v))

        client = connection(ip, None)
        version = executor(client, 'sudo ros console list |grep current')

        assert (console_v in version)

        executor(client, 'sudo ros console switch -f {console_version}'.format(console_version=current_version))
