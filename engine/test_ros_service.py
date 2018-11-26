# coding = utf-8
# Create date: 2018-11-15
# Author :Bowen Lee

from utils.connect_to_os import executor


def test_ros_local_service(ros_kvm_with_paramiko, cloud_config_url):
    client = ros_kvm_with_paramiko(cloud_config=
                                   '{url}/default.yml'.format(url=cloud_config_url))

    create_test_image = 'echo "FROM $(sudo system-docker images --format '"{{.Repository}}:{{.Tag}}"' | grep os-base)" > Dockerfile'
    build_test_image = 'sudo system-docker build -t test_image .'
    executor(client, create_test_image, seconds=10)
    executor(client, build_test_image, seconds=15)
    add_contents = 'echo "test:" > test.yml && echo "  image: test_image" >> test.yml ' \
                   '&& echo "  entrypoint: ls" >> test.yml && echo "  labels:" >> test.yml ' \
                   '&& echo "    io.rancher.os.scope: system" >> test.yml ' \
                   '&& echo "    io.rancher.os.after: console" >> test.yml'

    executor(client, add_contents, seconds=10)

    executor(client, 'sudo cp test.yml /var/lib/rancher/conf/test.yml', seconds=20)
    executor(client, 'sudo ros service enable /var/lib/rancher/conf/test.yml', seconds=20)
    executor(client, 'sudo ros service up test', seconds=30)
    output = executor(client, 'sudo ros service logs test | grep bin', seconds=20)
    assert ('bin' in output)


def test_ros_local_service_user(ros_kvm_with_paramiko, cloud_config_url):
    client = ros_kvm_with_paramiko(cloud_config=
                                   '{url}/default.yml'.format(url=cloud_config_url))
    create_test_image = 'echo "FROM alpine" > Dockerfile'
    executor(client, create_test_image, seconds=10)
    build_test_image = 'sudo docker build -t test_image_user .'
    executor(client, build_test_image, seconds=40)
    add_contents = 'echo "test:" > test.yml && echo "  image: test_image_user" >> test.yml ' \
                   '&& echo "  entrypoint: ls" >> test.yml && echo "  labels:" >> test.yml ' \
                   '&& echo "    io.rancher.os.scope: user" >> test.yml ' \
                   '&& echo "    io.rancher.os.after: console" >> test.yml'

    executor(client, add_contents, seconds=20)
    executor(client, 'sudo cp test.yml /var/lib/rancher/conf/test.yml', seconds=20)
    executor(client, 'sudo ros service enable /var/lib/rancher/conf/test.yml', seconds=20)
    executor(client, 'sudo ros service up test', seconds=30)
    output = executor(client, 'sudo ros service logs test | grep bin', seconds=20)
    assert ('bin' in output)
