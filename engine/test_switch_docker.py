# coding = utf-8
# Create date: 2018-11-15
# Author :Bowen Lee

import time
from utils.connect_to_os import executor, connection


def test_switch_docker(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output = executor(client, 'sudo ros engine list')
    list_of_docker = output.split('\n')
    list_of_docker.pop(-1)
    # Revert
    list_of_docker = list_of_docker[::-1]

    current_version = None

    special_version = 'docker-1.12.6'
    special2_version = 'docker-1.13.1'
    special3_version = 'docker-17.03.2-ce'

    list_docker_v = []

    for number, docker_v in enumerate(list_of_docker):
        if docker_v.startswith('current '):
            current_version = docker_v.split(' ')[2]
        else:
            list_docker_v.append(docker_v.split(' ')[1])

    list_of_checking_docker_v = list_docker_v[:5] + [special_version, special2_version, special3_version]

    executor(client, 'sudo ros config set rancher.docker.storage_driver overlay2')

    for docker_v in list_of_checking_docker_v:
        executor(client, 'sudo ros engine switch {docker_version}'.format(docker_version=docker_v))
        time.sleep(20)
        version = executor(client, 'sudo docker -v', seconds=20)
        assert (docker_v.replace('docker-', '') in version)

        executor(client, 'sudo ros engine switch {docker_version}'.format(docker_version=current_version))
