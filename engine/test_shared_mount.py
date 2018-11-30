# coding = utf-8
# Create date: 2018-11-14
# Author :Hailong


def test_shared_mount(ros_kvm_init, cloud_config_url):
    command = 'sudo mkdir /mnt/shared &&  \
               sudo touch /test &&  \
               sudo system-docker run  \
                   --privileged  \
                   -v /mnt:/mnt:shared  \
                   -v /test:/test busybox  \
                   mount --bind / /mnt/shared &&  \
               ls /mnt/shared'
    feed_back = 'test'
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)
