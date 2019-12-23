# coding = utf-8
# Create date: 2018-11-6
# Author :Bowen Lee
import time


def test_misc(ros_kvm_init, cloud_config_url):
    command = "sudo ros env printenv FLANNEL_NETWORK"
    kwargs = dict(cloud_config='{url}test_misc.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    stdin, stdout, stderr = client.exec_command(command, timeout=60)
    output = stdout.read().decode('utf-8')
    assert ('10.244.0.0/16' in output)

    command_dncp = "ps -ef"
    stdin, stdout, stderr = client.exec_command(command_dncp, timeout=60)
    output_dncp = stdout.read().decode('utf-8')

    assert ('dhcpcd -M' in output_dncp)

    command_tls = "set -e -x " \
                  "&& sudo ros tls gen --server -H localhost " \
                  "&& sudo ros tls gen" \
                  "&& sudo ros c set rancher.docker.tls true" \
                  "&& sudo system-docker restart docker"
    client.exec_command(command_tls, timeout=60)
    time.sleep(30)
    command_check_docker = 'docker --tlsverify version'
    stdin, stdout, stderr = client.exec_command(command_check_docker, timeout=60)
    output_docker_info = stdout.read().decode('utf-8')
    assert (('Client' in output_docker_info)
            and ('Server' in output_docker_info))

    stdin, stdout, stderr = client.exec_command('set -e -x &&'
                                                'pidof system-dockerd', timeout=60)

    assert ('1' in stdout.read().decode('utf-8'))
    client.close()
