# coding = utf-8
# Create date: 2018-11-09
# Author :Bowen Lee

import time


def test_swap(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_swap.yml'.format(url=cloud_config_url), is_second_hd=True,
                  is_install_to_hard_drive=True)

    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    client.exec_command('sudo mkswap /dev/vdb && sudo cloud-init-execute', timeout=60)
    # Network delay
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command('cat /proc/swaps | grep /dev/vdb', timeout=60)
    output = stdout.read().decode('utf-8')
    client.close()
    assert ('/dev/vdb' in output)
