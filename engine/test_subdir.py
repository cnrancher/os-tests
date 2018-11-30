# coding = utf-8
# Create date: 2018-11-14
# Author :Hailong


def test_subdir(ros_kvm_init):
    command = 'mkdir x &&  \
              sudo mount $(sudo ros dev LABEL=RANCHER_STATE) x &&  \
              test -d x/ros_subdir/home/rancher;  \
              echo $?'
    feed_back = '0'
    kwargs = dict(is_kernel_parameters=True,
                  kernel_parameters='rancher.state.directory=ros_subdir rancher.state.dev=LABEL=RANCHER_STATE rancher.state.autoformat=[/dev/sda,/dev/vda]')
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8').replace('\n', '')
    assert (feed_back == output)
