# coding = utf-8
# Create date: 2018-11-20
# Author :Hailong
from utils.connect_to_os import executor, connection


def test_oem(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True,
                  is_second_hd=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    ip = tuple_return[1]
    c_add_ome_config = 'set -x && ' \
                       'set -e && ' \
                       'sudo mkfs.ext4 -L RANCHER_OEM /dev/vdb && ' \
                       'sudo mount /dev/vdb /mnt &&' \
                       'echo -e "#cloud-config \nrancher:\n  upgrade:\n    url: \'foo\'" > /tmp/oem-config.yml &&' \
                       'sudo cp /tmp/oem-config.yml /mnt &&' \
                       'sudo umount /mnt'
    executor(client, c_add_ome_config)

    executor(client, 'sudo reboot')

    second_client = connection(ip, None)
    c_ls_oem = 'ls /usr/share/ros/oem'
    output_ls_oem = executor(second_client, c_ls_oem)
    assert ('oem-config.yml' in output_ls_oem)

    c_get_oem = 'sudo ros config get rancher.upgrade.url'
    output_get_oem = executor(second_client, c_get_oem)
    second_client.close()
    assert ('foo' in output_get_oem)
