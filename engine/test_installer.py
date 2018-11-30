# coding = utf-8
# Create date: 2018-11-23
# Author :Hailong

import subprocess
import libvirt
import time
from utils.connect_to_os import connection, executor


def test_install_msdos_mbr(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    command = 'sudo parted /dev/vda print'
    feed_back = 'Partition Table: msdos'
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)


def test_install_gpt_mbr(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True, extra_install_args='-t gptsyslinux')

    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    command = 'sudo parted /dev/vda print'
    feed_back = 'Partition Table: gpt'
    stdin, stdout, stderr = client.exec_command(command, timeout=10)
    output = stdout.read().decode('utf-8')
    client.close()
    assert (feed_back in output)


def test_auto_resize(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_define_xml=True,
                  is_install_to_hard_drive=True)

    client, ip, virtual_name, dom = ros_kvm_init(**kwargs)
    c_get_vda_size = "sudo fdisk -l /dev/vda | head -1 | awk '{print $3}'"
    c_get_vda1_size = "sudo fdisk -l /dev/vda | grep vda1 | awk '{print $6}'"

    output_vda_size = executor(client, c_get_vda_size).replace('\n', '')
    output_vda1_size = executor(client, c_get_vda1_size).replace('\n', '')
    assert ('10' == output_vda_size)
    assert ('10G' == output_vda1_size)

    c_reset_device = 'sudo ros config set rancher.resize_device /dev/vda'
    executor(client, c_reset_device)

    # reboot domain
    dom.shutdown()
    _confirm_shutdown(dom)
    _resize_disk(virtual_name, 30)
    dom.create()

    second_client = connection(ip, None)

    output_vda_size = executor(second_client, c_get_vda_size).replace('\n', '')
    output_vda1_size = executor(second_client, c_get_vda1_size).replace('\n', '')
    client.close()
    assert ('40' == output_vda_size)
    assert ('40G' == output_vda1_size)


def _resize_disk(virtual_name, capacity):
    subprocess.Popen('sudo qemu-img resize /opt/os-tests/images/{virtual_name}.qcow2 +{capacity}G '
                     '> /dev/null 2>&1'.format(virtual_name=virtual_name, capacity=capacity), shell=True)


def _confirm_shutdown(dom):
    for _ in range(60):
        time.sleep(2)
        state, _ = dom.state()
        if state == libvirt.VIR_DOMAIN_SHUTOFF:
            return True
        else:
            continue
    # TODO Need to return bool
