# coding = utf-8
# Create date: 2018-11-19
# Author :Bowen Lee

from utils.connect_to_os import connection, executor


def test_upgrade(ros_kvm_return_ip, cloud_config_url):
    client, ip = ros_kvm_return_ip(cloud_config='{url}/default.yml'.format(url=cloud_config_url))
    output = executor(client, 'sudo ros os list')
    list_of_os = output.split('\n')
    current_version = None

    # Trailing whitespace removed
    for number, ros_v in enumerate(list_of_os):
        list_of_os[number] = str(ros_v).rstrip()

    list_ros_v = []

    for number, ros_v in enumerate(list_of_os):
        if ros_v.endswith('running'):
            current_version = ros_v.split(' ')[0]
        else:
            list_ros_v.append(ros_v.split(' ')[0])

    list_ros_check = list_ros_v[:3]

    for ros_v in list_ros_check:
        client = connection(ip)

        executor(client, 'sudo ros os upgrade -f -i {os_version}'.format(os_version=ros_v))

        client = connection(ip)
        output = executor(client, "sudo ros -v | awk  '{print $2}'").replace('\n', '')
        assert (output in ros_v)
        executor(client, 'sudo ros os upgrade -f -i {os_version}'.format(os_version=current_version))
