# coding = utf-8
# Create date: 2018-11-14
# Author :Hailong


def test_shared_mount(ros_kvm_with_paramiko, cloud_config_url):
    command = 'sudo mkdir /mnt/shared &&  \
               sudo touch /test &&  \
               sudo system-docker run  \
                   --privileged  \
                   -v /mnt:/mnt:shared  \
                   -v /test:/test busybox  \
                   mount --bind / /mnt/shared &&  \
               ls /mnt/shared'
    feed_back = 'test'
    client = ros_kvm_with_paramiko(cloud_config='{url}/default.yml'.format(url=cloud_config_url))

    stdin, stdout, stderr = client.exec_command(command, timeout=20)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)
