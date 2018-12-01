# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from __future__ import print_function

import os
import random
import string
import subprocess
import time
import libvirt
import pytest
from utils.connect_to_os import connection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KVM_XML = '''<domain type='kvm'>
        <name>{virtual_name}</name>
        <memory>2048000</memory>
        <currentMemory>2048000</currentMemory>
        <vcpu>1</vcpu>
        <os>
        <type arch='x86_64' machine='pc'>hvm</type>
        <bootmenu enable='no'/>
        </os>
        <features><acpi/><apic/><pae/></features>
        <clock offset='localtime'/>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        <devices>
        <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2'/>
        <source file='/opt/os-tests/images/{v_name_for_source}.qcow2' span="qcow2"/>
        <target dev='vda' bus='virtio'/>
        <boot order='1'/>
        </disk>
        {second_driver_gist}
        <disk type='file' device='disk'>
        <driver name='qemu' type='raw'/>
        <source file='/opt/os-tests/assets/configdrive.img'/>
        <target dev='vdc' bus='virtio'/>
        <readonly/>
        </disk>
        <disk type='file' device='cdrom'>
        <source file='/opt/os-tests/assets/rancheros.iso'/>
        <target dev='hda' bus='ide'/>
        <boot order='2'/>
        </disk>
        <rng model='virtio'>
        <rate period="2000" bytes="1234"/>
        <backend model='random'>/dev/random</backend>
        </rng>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        <mac address="{mac_address}"/>
        </interface>
        {network_xml_gist}
        <input type='mouse' bus='ps2'/>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='en-us'/>
        </devices>
        </domain>'''

SECOND_DRIVE_XML_GIST = '''
        <disk type="file" device="disk">
        <driver name="qemu" type="qcow2"/>
        <source file="/opt/os-tests/images/{second_drive_name}.qcow2"/>
        <target dev="vdb" bus="virtio"/>
        </disk>
'''

NETWORK_XML_GIST = '''
        <interface type='bridge'>
        <source bridge='virbr0'/>
        </interface>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        </interface>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        </interface>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        </interface>      
'''

KERNEL_PARAMETERS_XML = '''<domain type='kvm'>
        <name>{virtual_name}</name>
        <memory>2048000</memory>
        <currentMemory>2048000</currentMemory>
        <vcpu>1</vcpu>
        <os>
        <type arch='x86_64' machine='pc'>hvm</type>
        <kernel>/opt/os-tests/assets/vmlinuz</kernel>
        <initrd>/opt/os-tests/assets/initrd</initrd>
        <cmdline>{kernel_parameters}</cmdline>
        </os>
        <features><acpi/><apic/><pae/></features>
        <clock offset='localtime'/>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        <devices>
        <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2'/>
        <source file='/opt/os-tests/images/{v_name_for_source}.qcow2' span="qcow2"/>
        <target dev='vda' bus='virtio'/>
        </disk>
        <disk type='file' device='disk'>
        <driver name='qemu' type='raw'/>
        <source file='/opt/os-tests/assets/configdrive.img'/>
        <target dev='vdb' bus='virtio'/>
        <readonly/>
        </disk>
        <rng model='virtio'>
        <rate period="2000" bytes="1234"/>
        <backend model='random'>/dev/random</backend>
        </rng>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        <mac address="{mac_address}"/>
        </interface>
        <input type='mouse' bus='ps2'/>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='en-us'/>
        </devices>
        </domain>'''

SSH_KEY_PATH = '/opt/os-tests/assets/id_rsa'
CLOUD_CONFIG_URL = 'https://raw.githubusercontent.com/cnrancher/os-tests/master/assets/'


def _install_to_hdrive(cloud_config, client, extra_install_args=None):
    base_cmd = _get_install_args(cloud_config, extra_install_args)

    client.exec_command(base_cmd)


def _get_install_args(cloud_config, extra_install_args):
    base_cmd = 'sudo ros install -f '
    if extra_install_args:
        base_cmd += extra_install_args

    if cloud_config:
        base_cmd += ' -c {cloud_config} '.format(cloud_config=cloud_config)

    if '-d' not in base_cmd:
        base_cmd += ' -d /dev/vda '
    return base_cmd


def _close_conn(conn, dom, is_define_xml):
    if dom:
        if is_define_xml:
            dom.destroy()
            dom.undefine()
        else:
            dom.destroy()
    if conn:
        conn.close()


def _clean_qcow2(virtual_name):
    """
    The function clean up two virtual machines qcow2.
    :param virtual_name:
    :return:
    """
    # TODO If there is only one the qcow2, Does the command is running?
    if virtual_name:
        st = subprocess.Popen(
            'rm -rf /opt/os-tests/images/{virtual_name}.qcow2 /opt/os-tests/images/{virtual_name_second}.qcow2'.format(
                virtual_name=virtual_name, virtual_name_second=virtual_name + '_second'), shell=True)
        st.wait()


def _get_ip(mac):
    for _ in range(30):
        time.sleep(10)
        obj = subprocess.Popen('arp -an | grep {mac}'.format(
            mac=mac),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        obj.wait()
        content_return = obj.stdout.read()
        if len(content_return) > 0:
            break

    ip = str(content_return, encoding='utf-8').split('(').__getitem__(1).split(')').__getitem__(0)
    return ip


def _create_qcow2(capacity, virtual_name):
    sub_ps = subprocess.Popen(
        'qemu-img create -f qcow2 /opt/os-tests/images/{virtual_name}.qcow2 {capacity}G'.format(
            virtual_name=virtual_name, capacity=capacity), shell=True)
    sub_ps.wait()


def _create_b2d_qcow2(capacity, virtual_name):
    sub_ps = subprocess.Popen(
        'echo "boot2docker, please format-me" | \
            cat - /dev/zero | \
            head -c 5242880 > \
            /opt/os-tests/assets/format-flag.txt && \
        qemu-img convert -f raw /opt/os-tests/assets/format-flag.txt \
            -O qcow2 /opt/os-tests/images/{virtual_name}.qcow2 && \
        qemu-img resize /opt/os-tests/images/{virtual_name}.qcow2 +{capacity}GB > /dev/null 2>&1'.format(
            virtual_name=virtual_name, capacity=capacity), shell=True)
    sub_ps.wait()


def _manage_path():
    """
    Manage path, may extend to add or remove path functions
    :return:
    """

    def _check_path():
        if not os.path.exists('/opt/os-tests/images/'):
            os.makedirs('/opt/os-tests/images/')
        else:
            return

    _check_path()


def pytest_addoption(parser):
    parser.addoption(
        "--cloud-config-url", default=CLOUD_CONFIG_URL,
        help="Cloud config url"
    )


@pytest.fixture
def cloud_config_url(request):
    return request.config.getoption('--cloud-config-url')


def setup_function():
    pass


def teardown_function():
    pass


def _id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _mac_generator():
    mac = [0x52, 0x54, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


@pytest.fixture
def ros_kvm_init():
    dom = None
    conn = None
    virtual_name = None
    is_define_xml = False

    def _ros_kvm_init(**kwargs):
        nonlocal virtual_name
        virtual_name = _id_generator()

        mac = _mac_generator()
        _manage_path()

        if kwargs.get('is_kernel_parameters'):
            kernel_parameters = kwargs.get('kernel_parameters')
            xml_for_virtual = KERNEL_PARAMETERS_XML.format(
                virtual_name=virtual_name,
                mac_address=mac,
                v_name_for_source=virtual_name,
                kernel_parameters=kernel_parameters)
        else:
            if kwargs.get('is_second_hd'):
                second_drive_name = virtual_name + '_second'
                #  Create second_drive
                _create_qcow2('2', second_drive_name)
            else:
                second_drive_name = ''

            if kwargs.get('is_network_gist'):
                network_xml_gist = NETWORK_XML_GIST

            else:
                network_xml_gist = ''

            xml_for_virtual = KVM_XML.format(virtual_name=virtual_name,
                                             mac_address=mac,
                                             v_name_for_source=virtual_name,
                                             second_driver_gist=second_drive_name,
                                             network_xml_gist=network_xml_gist)

        # region    Create qcow2
        if kwargs.get('is_b2d'):
            _create_b2d_qcow2('10', virtual_name)
        else:
            _create_qcow2('10', virtual_name)

        # endregion
        nonlocal conn

        conn = libvirt.open('qemu:///system')

        if not conn:
            raise Exception('Failed to open connection to qemu:///system')
        else:
            nonlocal dom
            nonlocal is_define_xml
            is_define_xml = kwargs.get('is_define_xml')
            if is_define_xml:
                dom = conn.defineXML(xml_for_virtual)
                dom.create()
            else:
                dom = conn.createXML(xml_for_virtual)

        ip = _get_ip(mac)

        if ip:
            if kwargs.get('is_install_to_hard_drive'):
                cloud_config = kwargs.get('cloud_config')

                client = connection(ip=ip, seconds=kwargs.get('seconds_for_install'))
                _install_to_hdrive(cloud_config, client, kwargs.get('extra_install_args'))
                time.sleep(10)

            ssh = connection(ip, seconds=kwargs.get('seconds_for_reconnect'))

            return ssh, ip, virtual_name, dom
        else:
            return None

    yield _ros_kvm_init

    _close_conn(conn, dom, is_define_xml)

    _clean_qcow2(virtual_name)
