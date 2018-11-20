# coding = utf-8
# Create date: 2018-11-19
# Author :Hailong


def test_b2d_autoformat_boot_initrd(ros_kvm_for_kernel_parameters):
    command = 'blkid'
    feed_back = 'B2D_STATE'
    client = ros_kvm_for_kernel_parameters(kernel_parameters=None, b2d=True)

    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)

