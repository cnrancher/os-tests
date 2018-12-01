# coding = utf-8
# Create date: 2018-11-29
# Author :Hailong

from utils.connect_to_os import executor


def test_nonexistent_state(ros_kvm_init):
    kwargs = dict(kernel_parameters='--no-format '
                                    'rancher.state.dev=LABEL=NONEXISTENT '
                                    'rancher.state.autoformat=[/dev/sda,/dev/vda]',
                  is_kernel_parameters=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output = executor(client, 'sudo ros config get rancher.state.dev')
    assert ('LABEL=NONEXISTENT' in output)
