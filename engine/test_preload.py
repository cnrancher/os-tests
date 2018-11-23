# coding = utf-8
# Create date: 2018-11-19
# Author :Bowen Lee

# coding = utf-8
# Create date: 2018-11-19
# Author :Bowen Lee

from utils.connect_to_os import connection, executor


def test_preload(ros_kvm_return_ip, cloud_config_url):
    client, ip = ros_kvm_return_ip(cloud_config='{url}/default.yml'.format(url=cloud_config_url))
    c_com_img = 'wait-for-docker \
                        && docker pull busybox \
                        && sudo docker save -o /var/lib/rancher/preload/system-docker/busybox.tar busybox \
                        && sudo gzip /var/lib/rancher/preload/system-docker/busybox.tar \
                        && sudo system-docker pull alpine \
                        && sudo system-docker save -o /var/lib/rancher/preload/docker/alpine.tar alpine'
    executor(client, c_com_img, seconds=50)

    c_ls_sys_docker_img = 'test -f /var/lib/rancher/preload/system-docker/busybox.tar.gz && ' \
                          'echo $?'
    output_sys_docker = executor(client, c_ls_sys_docker_img, seconds=10).replace('\n', '')
    assert ('0' == output_sys_docker)

    c_ls_user_docker_img = 'test -f /var/lib/rancher/preload/docker/alpine.tar && ' \
                           'echo $?'
    output_user_docker = executor(client, c_ls_user_docker_img, seconds=10).replace('\n', '')
    assert ('0' == output_user_docker)

    executor(client, 'sudo reboot')
    second_client = connection(ip)

    output_sys_docker = executor(second_client, 'sudo system-docker images | grep busybox', seconds=10)
    assert ('busybox' in output_sys_docker)
    output_user_docker = executor(second_client, 'docker images | grep alpine', seconds=10)
    assert ('alpine' in output_user_docker)
