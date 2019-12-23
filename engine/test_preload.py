# coding = utf-8
# Create date: 2018-11-19
# Author :Bowen Lee

from utils.connect_to_os import connection, executor
import time


def test_preload(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    ip = tuple_return[1]
    c_com_img = 'wait-for-docker \
                        && docker pull busybox \
                        && sudo docker save -o /var/lib/rancher/preload/system-docker/busybox.tar busybox \
                        && sudo gzip /var/lib/rancher/preload/system-docker/busybox.tar \
                        && sudo system-docker pull alpine \
                        && sudo system-docker save -o /var/lib/rancher/preload/docker/alpine.tar alpine'
    executor(client, c_com_img)

    c_ls_sys_docker_img = 'test -f /var/lib/rancher/preload/system-docker/busybox.tar.gz ; ' \
                          'echo $?'
    output_sys_docker = executor(client, c_ls_sys_docker_img).replace('\n', '')
    assert ('0' == output_sys_docker)

    c_ls_user_docker_img = 'test -f /var/lib/rancher/preload/docker/alpine.tar ; ' \
                           'echo $?'
    output_user_docker = executor(client, c_ls_user_docker_img).replace('\n', '')
    assert ('0' == output_user_docker)

    executor(client, 'sudo reboot')
    second_client = connection(ip, seconds=30)

    output_sys_docker = executor(second_client, 'sudo system-docker images | grep busybox')
    assert ('busybox' in output_sys_docker)
    time.sleep(10)
    output_user_docker = executor(second_client, 'docker images | grep alpine')
    assert ('alpine' in output_user_docker)
