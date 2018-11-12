# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from __future__ import print_function

import os
import random
import string
import subprocess
import time
from xml.etree.ElementTree import ElementTree
import libvirt
import pexpect
import pytest
import paramiko

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
        <source file='/opt/{v_name_for_source}.qcow2' span="qcow2"/>
        <target dev='vda' bus='virtio'/>
        <boot order='1'/>
        </disk>
        <disk type="file" device="disk">
        <driver name="qemu" type="qcow2"/>
        <source file="/opt/{second_drive}.qcow2"/>
        <target dev="vdb" bus="virtio"/>
        </disk>
        <disk type='file' device='disk'>
        <driver name='qemu' type='raw'/>
        <source file='/opt/configdrive.img'/>
        <target dev='vdc' bus='virtio'/>
        <readonly/>
        </disk>
        <disk type='file' device='cdrom'>
        <source file='/opt/os-tests/rancheros.iso'/>
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
        <input type='mouse' bus='ps2'/>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='en-us'/>
        </devices>
        </domain>'''

KERNEL_PARAMETERS_XML = '''<domain type='kvm'>
        <name>{virtual_name}</name>
        <memory>2048000</memory>
        <currentMemory>2048000</currentMemory>
        <vcpu>1</vcpu>
        <os>
        <type arch='x86_64' machine='pc'>hvm</type>
        <kernel>/opt/vmlinuz</kernel>
        <initrd>/opt/initrd</initrd>
        <cmdline>rancher.state.dev=LABEL=RANCHER_STATE 
        rancher.state.autoformat=[/dev/sda,/dev/vda] 
        rancher.password=rancher {kernel_parameters}</cmdline>
        </os>
        <features><acpi/><apic/><pae/></features>
        <clock offset='localtime'/>
        <on_poweroff>destroy</on_poweroff>
        <on_reboot>restart</on_reboot>
        <on_crash>destroy</on_crash>
        <devices>
        <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2'/>
        <source file='/opt/{v_name_for_source}.qcow2' span="qcow2"/>
        <target dev='vda' bus='virtio'/>
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

CLOUD_CONFIG_URL = 'https://raw.githubusercontent.com/cnrancher/os-tests/master/assets/'


@pytest.fixture
def ros_kvm_with_paramiko():
    dom = None
    conn = None
    virtual_name = None

    def _ros_kvm_with_paramiko(cloud_config):
        nonlocal virtual_name
        virtual_name = _id_generator()
        second_drive = virtual_name + '_second'
        mac = _mac_generator()

        xml_for_virtual = KVM_XML.format(virtual_name=virtual_name,
                                         mac_address=mac,
                                         v_name_for_source=virtual_name,
                                         second_drive=second_drive)

        sub_ps = subprocess.Popen(
            'qemu-img create -f qcow2 /opt/{virtual_name}.qcow2 10G'.format(
                virtual_name=virtual_name), shell=True)
        sub_ps.wait()

        sub_ps2 = subprocess.Popen(
            'qemu-img create -f qcow2 /opt/{virtual_name}.qcow2 2G'.format(
                virtual_name=second_drive), shell=True
        )
        sub_ps2.wait()

        nonlocal conn
        conn = libvirt.open('qemu:///system')
        if not conn:
            raise Exception('Failed to open connection to qemu:///system')
        else:
            nonlocal dom
            dom = conn.createXML(xml_for_virtual)
            for _ in range(90):
                time.sleep(1)
                obj = subprocess.Popen('arp -an | grep {mac}'.format(
                    mac=mac),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True).stdout.read()
                if len(obj) > 0:
                    break
                else:
                    continue

            ip = str(obj, encoding='utf-8').split('(').__getitem__(1).split(')').__getitem__(0)

            time.sleep(60)
            if ip:
                ssh_client_for_reinstall = pexpect.spawn('ssh {username}@{ip}'.format(
                    username='rancher',
                    ip=ip))
                ssh_client_for_reinstall.sendline(
                    'sudo ros install -c {cloud_config} -d /dev/vda -f'.format(
                        cloud_config=cloud_config))

                time.sleep(90)
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh.connect(hostname=ip,
                            username='rancher',
                            password='')
                return ssh
            else:
                return None

    yield _ros_kvm_with_paramiko

    _close_conn(conn, dom, virtual_name)


def _close_conn(conn, dom, virtual_name):
    if dom:
        dom.destroy()
    if conn:
        conn.close()
    st = subprocess.Popen('rm -rf /opt/{virtual_name}.qcow2 /opt/{virtual_name_second}.qcow2'.format(
        virtual_name=virtual_name, virtual_name_second=virtual_name + '_second'), shell=True)
    st.wait()


@pytest.fixture
def ros_kvm_for_kernel_parameters():
    dom = None
    conn = None
    virtual_name = None

    def _ros_kvm_for_kernel_parameters(kernel_parameters):
        nonlocal virtual_name
        virtual_name = _id_generator()
        mac = _mac_generator()
        xml_for_virtual = KERNEL_PARAMETERS_XML.format(
            virtual_name=virtual_name,
            mac_address=mac,
            v_name_for_source=virtual_name,
            kernel_parameters=kernel_parameters)
        sub_ps = subprocess.Popen(
            'qemu-img create -f qcow2 -o size=10G /opt/{virtual_name}.qcow2'.format(
                virtual_name=virtual_name), shell=True)
        sub_ps.wait()
        nonlocal conn
        conn = libvirt.open('qemu:///system')
        if not conn:
            raise Exception('Failed to open connection to qemu:///system')
        else:
            nonlocal dom
            dom = conn.createXML(xml_for_virtual)
            for _ in range(90):
                time.sleep(1)
                obj = subprocess.Popen('arp -an | grep {mac}'.format(
                    mac=mac),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True).stdout.read()
                if len(obj) > 0:
                    break
                else:
                    continue
            time.sleep(60)
            ip = str(obj, encoding='utf-8').split('(').__getitem__(1).split(')').__getitem__(0)
            if ip:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=ip,
                            username='rancher',
                            password='rancher')
                return ssh
            else:
                return None

    yield _ros_kvm_for_kernel_parameters

    _close_conn(conn, dom, virtual_name)


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


def _if_match(node, kv_map):
    for key in kv_map:
        if node.get(key) != kv_map.get(key):
            return False
    return True


def _create_xml(config_path, mac, virtual_name):
    try:
        if os.path.exists(config_path):
            tree = _read_xml(config_path)

            # Insert virtual machine name
            nodes_kvm_name = _find_nodes(tree, 'name')

            _change_node_text(nodes_kvm_name, virtual_name)
            assert (tree.findtext('name') == virtual_name)

            # Insert disk typed 'qcow2'
            nodes_kvm_spice = _find_nodes(tree, 'devices/disk/source')
            node_kvm_spice = _get_node_by_key_value(nodes_kvm_spice, {'span': 'qcow2'})

            _change_node_attribute(node_kvm_spice,
                                   {'file': '/opt/{machine_name}.qcow2'.format(machine_name=virtual_name)})
            # Check machine qcow2
            _check_node_attribute(node_kvm_spice,
                                  {'file': '/opt/{machine_name}.qcow2'.format(machine_name=virtual_name)})

            # Insert MAC address
            node_kvm_mac = _find_nodes(tree, 'devices/interface/mac')
            _change_node_attribute(node_kvm_mac, {'address': mac})

            # Check mac address
            _check_node_attribute(node_kvm_mac, {'address': mac})

            # Return XMl config

            tree.write(BASE_DIR + '/config/{virtualenv_name}.xml'.format(virtualenv_name=virtual_name),
                       encoding="utf-8",
                       xml_declaration=True)

        else:
            raise Exception('Config path is none')
    except Exception as e:
        raise Exception(e.args.__getitem__(0))


def _load_xml(path):
    if os.path.exists(path):
        with open(path, 'r') as xml_reader:
            return xml_reader.read()
    else:
        raise Exception('XMl is None.')


def _id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _mac_generator():
    mac = [0x52, 0x54, 0x00,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


def _change_node_text(nodelist, text):
    for node in nodelist:
        node.text = text


def _change_node_attribute(nodelist, attribute_dic):
    for node in nodelist:
        for key in attribute_dic:
            node.set(key, attribute_dic.get(key))


def _check_node_attribute(nodelist, attribute_dic):
    for node in nodelist:
        for key in attribute_dic:
            assert (node.get(key) == attribute_dic.get(key))


def _get_node_by_key_value(nodelist, kv_map):
    result_nodes = []
    for node in nodelist:
        if _if_match(node, kv_map):
            result_nodes.append(node)
    return result_nodes


def _read_xml(in_path):
    tree = ElementTree()
    tree.parse(in_path)
    return tree


def _find_nodes(tree, path):
    return tree.findall(path)


def _get_nodes_text(tree, path):
    return tree.findtext(path)
