# coding = utf-8
# Create date: 2018-11-22
# Author :Bowen Lee

import time
from utils.connect_to_os import executor, connection


def test_ssh_key_merge(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    set_metadata = 'echo -e ' \
                   '"SSHPublicKeys: \n "0": zero \n "1": one\n "2": two"  ' \
                   '> /var/lib/rancher/conf/metadata'

    set_ssh_aut_key = 'echo -e ' \
                      '"$(sudo ros config get ssh_authorized_keys | head -1)\n- zero\n- one\n- two\n" ' \
                      '> expected'

    set_current = 'sudo ros config get ssh_authorized_keys > current_config'

    executor(client, 'sudo rm /var/lib/rancher/conf/cloud-config.yml')
    executor(client, 'sudo chmod -R 777 /var/lib/rancher/conf/')
    executor(client, set_metadata)
    executor(client, set_ssh_aut_key)
    executor(client, set_current)
    output = executor(client, 'diff expected current_config && echo $?').replace('\n', '')
    assert (output == '0')
