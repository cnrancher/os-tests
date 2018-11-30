# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from utils.connect_to_os import connection, executor


def test_modules(ros_kvm_init):
    command = 'lsmod | grep btrfs'
    kwargs = dict(is_kernel_parameters=True,
                  kernel_parameters='rancher.state.dev=LABEL=RANCHER_STATE rancher.modules=[btrfs] rancher.state.autoformat=[/dev/sda,/dev/vda]')
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output = executor(client, command)
    assert ('btrfs' in output)


def test_cloud_config_modules(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_cloud_config_modules.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    output = executor(client, 'lsmod | grep btrfs')
    assert ('btrfs' in output)
