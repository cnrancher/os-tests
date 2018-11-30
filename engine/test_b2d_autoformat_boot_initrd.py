# coding = utf-8
# Create date: 2018-11-19
# Author :Hailong


def test_b2d_autoformat_boot_initrd(ros_kvm_init):
    command = 'blkid'
    feed_back = 'B2D_STATE'
    kwargs = dict(is_b2d=True, is_kernel_parameters=True,
                  kernel_parameters='rancher.state.dev=LABEL=RANCHER_STATE rancher.state.autoformat=[/dev/sda,/dev/vda]')
    tuple_return = ros_kvm_init(**kwargs)

    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)
