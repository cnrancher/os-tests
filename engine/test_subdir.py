# coding = utf-8
# Create date: 2018-11-14
# Author :Hailong


def test_subdir(ros_kvm_for_kernel_parameters):
    command = 'mkdir x &&  \
              sudo mount $(sudo ros dev LABEL=RANCHER_STATE) x &&  \
              test -d x/ros_subdir/home/rancher;  \
              echo $?'
    feed_back = '0'
    client = ros_kvm_for_kernel_parameters(kernel_parameters='rancher.state.directory=ros_subdir')

    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8').replace('\n', '')
    assert (feed_back == output)
