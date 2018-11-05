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
        <vcpu>2</vcpu>
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
        <emulator>/usr/bin/kvm-spice</emulator>
        <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2'/>
        <source file='/opt/{v_name_for_source}.qcow2' span="qcow2"/>
        <target dev='hda' bus='ide'/>
        <boot order='1'/>
        </disk>
        <disk type='file' device='cdrom'>
        <source file='/opt/os-tests/rancheros.iso'/>
        <target dev='hdb' bus='ide'/>
        <boot order='2'/>
        </disk>
        <disk type='file' device='disk'>
        <driver name='qemu' type='raw'/>
        <source file='/state/configdrive.img'/>
        <target dev='hdc' bus='ide'/>
        <address type='drive' controller='0' bus='1' target='0' unit='0'/>
        </disk>
        <interface type='bridge'>
        <source bridge='virbr0'/>
        <mac address="{mac_address}"/>
        </interface>
        <input type='mouse' bus='ps2'/>
        <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0' keymap='en-us'/>
        </devices>
        </domain>'''


@pytest.fixture
def ros_kvm():
    dom = None
    conn = None
    virtual_name = None

    def _ros_kvm(cloud_config):
        nonlocal virtual_name
        virtual_name = _id_generator()
        mac = _mac_generator()

        xml_for_virtual = KVM_XML.format(virtual_name=virtual_name, mac_address=mac, v_name_for_source=virtual_name)

        subprocess.Popen(
            'qemu-img create -f qcow2 /opt/{virtual_name}.qcow2 10G'.format(virtual_name=virtual_name),
            shell=True)

        nonlocal conn
        conn = libvirt.open('qemu:///system')
        if not conn:
            raise Exception('Failed to open connection to qemu:///system')
        else:

            nonlocal dom
            dom = conn.createXML(xml_for_virtual)
            for _ in range(90):
                time.sleep(1)
                obj = subprocess.Popen('arp -an | grep {mac}'.format(mac=mac), stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.read()
                if len(obj) > 0:
                    break
                else:
                    continue

            ip = str(obj, encoding='utf-8').split('(').__getitem__(1).split(')').__getitem__(0)

            time.sleep(60)
            if ip:
                ssh_client_for_reinstall = pexpect.spawn('ssh {username}@{ip}'.format(username='rancher', ip=ip))
                ssh_client_for_reinstall.sendline(
                    'sudo ros install -c {cloud_config} -d /dev/sda -f'.format(
                        cloud_config=cloud_config))

                time.sleep(90)
                ssh = pexpect.spawn('ssh {username}@{ip}'.format(username='rancher', ip=ip))
                return ssh
            else:
                return None

    yield _ros_kvm

    dom.destroy()
    conn.close()
    st = subprocess.Popen('rm -rf /opt/{virtual_name}.qcow2'.format(virtual_name=virtual_name),
                          shell=True)
    st.wait()


@pytest.fixture
def ros_kvm_with_paramiko():
    dom = None
    conn = None
    virtual_name = None

    def _ros_kvm_with_paramiko(cloud_config):
        nonlocal virtual_name
        virtual_name = _id_generator()
        mac = _mac_generator()

        xml_for_virtual = KVM_XML.format(virtual_name=virtual_name, mac_address=mac, v_name_for_source=virtual_name)

        subprocess.Popen(
            'qemu-img create -f qcow2 /opt/{virtual_name}.qcow2 10G'.format(virtual_name=virtual_name),
            shell=True)

        nonlocal conn
        conn = libvirt.open('qemu:///system')
        if not conn:
            raise Exception('Failed to open connection to qemu:///system')
        else:

            nonlocal dom
            dom = conn.createXML(xml_for_virtual)
            for _ in range(90):
                time.sleep(1)
                obj = subprocess.Popen('arp -an | grep {mac}'.format(mac=mac), stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).stdout.read()
                if len(obj) > 0:
                    break
                else:
                    continue

            ip = str(obj, encoding='utf-8').split('(').__getitem__(1).split(')').__getitem__(0)

            time.sleep(60)
            if ip:
                ssh_client_for_reinstall = pexpect.spawn('ssh {username}@{ip}'.format(username='rancher', ip=ip))
                ssh_client_for_reinstall.sendline(
                    'sudo ros install -c {cloud_config} -d /dev/sda -f'.format(
                        cloud_config=cloud_config))

                time.sleep(90)
                # ssh = pexpect.spawn('ssh {username}@{ip}'.format(username='rancher', ip=ip))
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh.connect(hostname=ip,
                            username='rancher', password='')
                return ssh
            else:
                return None

    yield _ros_kvm_with_paramiko

    dom.destroy()
    conn.close()
    st = subprocess.Popen('rm -rf /opt/{virtual_name}.qcow2'.format(virtual_name=virtual_name),
                          shell=True)
    st.wait()


def pytest_addoption(parser):
    parser.addoption(
        "--cloud-config-url", default="http://192.168.1.24", help="Cloud config url"

    )


@pytest.fixture
def cloud_config_url(request):
    return request.config.getoption("--cloud-config-url")


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
