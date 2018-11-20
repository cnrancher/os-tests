# coding = utf-8
# Create date: 2018-11-19
# Author :Hailong


def test_b2d_autoformat_boot_iso(ros_kvm_with_paramiko_b2d):
    command = 'blkid'
    feed_back = 'B2D_STATE'
    client = ros_kvm_with_paramiko_b2d()

    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)
