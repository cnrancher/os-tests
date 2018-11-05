# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee

from __future__ import print_function

import os
import random
import string
from xml.etree.ElementTree import ElementTree

import paramiko

from config import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def init_ssh_client(ip):
    """

    :param ip:
    :return:
    """
    try:
        paramiko.util.log_to_file(BASE_DIR + '/logs/ssh.log')
        config = _get_hvm_config()
        key = paramiko.RSAKey.from_private_key_file(config.get('amazon_hvm').get('private_key_path'))
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=ip,
                       username=config.get('amazon_hvm').get('username'),
                       pkey=key, allow_agent=False, look_for_keys=False)
    except Exception as e:
        client.close()
        raise e
    else:
        return client


def pull_file():
    """
    Upload file to remote server.
    :return:
    """
    try:
        global IP_OR_HOST
        paramiko.util.log_to_file(BASE_DIR + '/logs/amazon_os.log')
        config = _get_hvm_config()
        key = paramiko.RSAKey.from_private_key_file(config.get('amazon_hvm').get('private_key_path'))
        transport = paramiko.Transport(IP_OR_HOST, 22)
        transport.connect(username=config.get('amazon_hvm').get('username'), pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        p = sftp.put(BASE_DIR + '/logs/amazon_os.log', '/etc/test/amazon_os.log')
        # sftp.get('remove_path', 'local_path')
        transport.close()
    except Exception as e:
        transport.close()
        raise e
    else:
        return transport


def _get_hvm_config():
    """
    Get hvm config
    :return:
    """
    return hvm_configs


def get_ip_tuple():
    """

    :return:
    """
    ip_tuple = hvm_configs.get('amazon_hvm').get('ip')
    if not ip_tuple:
        raise Exception('Config is None')
    else:
        return ip_tuple


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
