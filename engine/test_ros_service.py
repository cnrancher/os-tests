# coding = utf-8
# Create date: 2018-11-15
# Author :Bowen Lee

from utils.connect_to_os import executor, connection


def test_ros_local_service(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    create_test_image = 'echo "FROM $(sudo system-docker images --format '"{{.Repository}}:{{.Tag}}"' | grep os-base)" > Dockerfile'
    build_test_image = 'sudo system-docker build -t test_image .'
    executor(client, create_test_image)
    executor(client, build_test_image)
    add_contents = 'echo "test:" > test.yml && echo "  image: test_image" >> test.yml ' \
                   '&& echo "  entrypoint: ls" >> test.yml && echo "  labels:" >> test.yml ' \
                   '&& echo "    io.rancher.os.scope: system" >> test.yml ' \
                   '&& echo "    io.rancher.os.after: console" >> test.yml'

    executor(client, add_contents)

    executor(client, 'sudo cp test.yml /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service enable /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service up test')
    output = executor(client, 'sudo ros service logs test')
    assert ('bin' in output)


def test_ros_local_service_user(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    create_test_image = 'docker pull alpine && echo "FROM alpine" > Dockerfile'
    executor(client, create_test_image)
    build_test_image = 'sudo docker build -t test_image_user .'
    executor(client, build_test_image)
    add_contents = 'echo "test:" > test.yml && echo "  image: test_image_user" >> test.yml ' \
                   '&& echo "  entrypoint: ls" >> test.yml && echo "  labels:" >> test.yml ' \
                   '&& echo "    io.rancher.os.scope: user" >> test.yml ' \
                   '&& echo "    io.rancher.os.after: console" >> test.yml'

    executor(client, add_contents)
    executor(client, 'sudo cp test.yml /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service enable /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service up test')
    output = executor(client, 'sudo ros service logs test')
    assert ('bin' in output)
