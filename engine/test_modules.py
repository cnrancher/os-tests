# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee


def test_modules(ros_kvm_for_kernel_parameters):
    command = 'lsmod'
    client = ros_kvm_for_kernel_parameters(kernel_parameters='rancher.modules=[btrfs]')
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('btrfs' in output)
