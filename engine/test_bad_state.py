# coding = utf-8
# Create date: 2018-11-29
# Author :Hailong

from utils.connect_to_os import executor


def test_bad_state(ros_kvm_init):
    kwargs = dict(
        kernel_parameters='--no-format rancher.state.dev=LABEL=BAD_STATE rancher.state.autoformat=[/dev/sda,/dev/vda]',
        is_kernel_parameters=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output = executor(client, 'mount | grep /var/lib/docker')
    client.close()
    assert ('rootfs' in output)


def test_bad_state_with_wait(ros_kvm_init):
    kwargs = dict(
        kernel_parameters='--no-format rancher.state.dev=LABEL=BAD_STATE rancher.state.wait rancher.state.autoformat=[/dev/sda,/dev/vda]',
        is_kernel_parameters=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    outptu = executor(client, 'mount | grep /var/lib/docker')
    client.close()
    assert ('rootfs' in outptu)
