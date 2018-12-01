# coding = utf-8
# Create date: 2018-11-28
# Author :Hailong

from utils.connect_to_os import executor

data_source_url = 'https://gist.githubusercontent.com/kingsd041/310b5f0ab89567e93edadf1bbed822fb/' \
                  'raw/1ef388e085ffb4b6bb352c8383aa4b7ad3dafd33/test_network_from_url.txt'


def test_network_from_cloud_cfg(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_network_from_cloudcfg.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True, is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    # Verify mtu
    output_mtu = executor(client, 'ip address show bond0')
    assert ('mtu 1450' in output_mtu)

    # Verify vlan
    output_eth1_100 = executor(client, 'ip address show eth1.100')
    assert ('eth1.100@eth1' in output_eth1_100)
    output_foobar = executor(client, 'ip address show foobar')
    assert ('foobar@eth1' in output_foobar)

    # Verify Bridging
    output_eth2 = executor(client, 'ip address show eth2')
    assert ('master br0' in output_eth2)
    output_br0 = executor(client, 'ip address show br0')
    assert ('inet 192.168.122' in output_br0)

    # Verify NIC bonding
    output_bond0 = executor(client, 'ip address show bond0')
    assert ('inet 192.168.122.252' in output_bond0)
    output_bond_mode = executor(client, 'cat /sys/class/net/bond0/bonding/mode')
    assert ('active-backup 1' in output_bond_mode)
    output_eth3 = executor(client, 'ip address show eth3')
    assert ('master bond0' in output_eth3)
    output_eth4 = executor(client, 'ip address show eth4')
    client.close()
    assert ('master bond0' in output_eth4)


def test_network_cmds(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_network_cmds.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True, is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output = executor(client, 'cat /var/log/net.log')
    net_check_output = '''pre_cmds
pre_up eth0
post_up eth0
pre_up eth1
post_up eth1
pre_up eth2
post_up eth2
post_cmds
'''
    client.close()
    assert (net_check_output in output)


def test_network_boot_cfg(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True,
                  extra_install_args='--append "rancher.network.interfaces.eth1.address=192.168.122.251/24 '
                                     'rancher.network.interfaces.eth1.gateway=192.168.122.250 '
                                     'rancher.network.interfaces.eth0.dhcp=true"', is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output_eth1 = executor(client, 'ip address show eth1')
    assert ('inet 192.168.122.251' in output_eth1)

    output_eth1_gw = executor(client, 'ip route show dev eth1')
    client.close()
    assert ('default via 192.168.122.250' in output_eth1_gw)


def test_network_boot_and_cloud_cfg(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_network_boot_and_cloudcfg.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True,
                  extra_install_args='--append "rancher.network.interfaces.eth1.address=10.1.0.52/24 '
                                     'rancher.network.interfaces.eth1.gateway=10.1.0.2 '
                                     'rancher.network.interfaces.eth0.dhcp=true '
                                     'rancher.network.interfaces.eth3.dhcp=true"', is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    # This shows that the boot cmdline wins over the cloud-config
    output_eth1_ip = executor(client, 'ip address show eth1')
    assert ('inet 10.1.0.52/24' in output_eth1_ip)
    output_eth1_gw = executor(client, 'ip route show dev eth1')
    assert ('default via 10.1.0.2' in output_eth1_gw)

    output_eth2_ip = executor(client, 'ip address show eth2')
    assert ('inet 10.31.168.85/24' in output_eth2_ip)
    # Known issue https://github.com/rancher/os/issues/2587
    # output_eth2_gw = executor(client, 'ip route show dev eth2')
    # assert ('default via 10.31.168.1' in output_eth2_gw)

    output_eth3_ip = executor(client, 'ip address show eth3')
    client.close()
    assert ('inet 192.168.122' in output_eth3_ip)


def test_network_cloud_cfg(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}test_network_boot_and_cloudcfg.yml'.format(url=cloud_config_url),
                  is_install_to_hard_drive=True, is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output_eth1_ip = executor(client, 'ip address show eth1')
    assert ('inet 10.1.0.41/24' in output_eth1_ip)
    output_eth1_gw = executor(client, 'ip route show dev eth1')
    assert ('default via 10.1.0.1' in output_eth1_gw)

    output_eth2_ip = executor(client, 'ip address show eth2')
    assert ('inet 10.31.168.85/24' in output_eth2_ip)
    # Known issue https://github.com/rancher/os/issues/2587
    output_eth2_gw = executor(client, 'ip route show dev eth2')
    client.close()

    assert ('default via 10.31.168.1' in output_eth2_gw)


def test_network_from_url(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True,
                  extra_install_args=' --append "rancher.cloud_init.datasources=[url:{datasource_url}]"'.format(
                      datasource_url=data_source_url), is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    output_br0 = executor(client, 'ip addr show br0 ; echo $?')
    assert ('0' in output_br0)

    output_br0_100 = executor(client, 'ip addr show br0.100')
    assert ('inet 123.123.123.123' in output_br0_100)

    output_eth1_100 = executor(client, 'ip addr show eth1.100')
    assert ('master br0' in output_eth1_100)

    c_get_dns = 'cat /etc/resolv.conf'
    output_dns = executor(client, c_get_dns)
    client.close()
    assert ('search mydomain.com example.com' in output_dns)
    assert ('nameserver 208.67.222.123' in output_dns)
    assert ('nameserver 208.67.220.123' in output_dns)


def test_set_network_from_network_service(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True,
                  is_network_gist=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    c_set_network = '''
        echo "rancher:" >> config.yml
        echo "  network:" >> config.yml
        echo "    interfaces:" >> config.yml
        echo "      eth2:" >> config.yml
        echo "        dhcp: true" >> config.yml
        echo "      eth3:" >> config.yml
        echo "        dhcp: false" >> config.yml
        echo "      eth1:" >> config.yml
        echo "        address: 192.168.122.253/24" >> config.yml
        echo "        dhcp: false" >> config.yml
        echo "        gateway: 192.168.122.254" >> config.yml
        echo "        mtu: 1500" >> config.yml
        '''
    executor(client, c_set_network)
    executor(client, 'cat config.yml | sudo ros config merge')
    executor(client, 'sudo ros service restart network && sleep 5')
    executor(client, 'sleep 2')

    output_eth1 = executor(client, 'ip address show eth1')
    assert ('inet 192.168.122.253' in output_eth1)

    output_route = executor(client, 'ip route show dev eth1')
    assert ('default via 192.168.122.254' in output_route)

    output_eth2 = executor(client, 'ip address show eth2')
    assert ('inet 192.168.122' in output_eth2)

    output_eth3 = executor(client, 'ip address show eth3')
    client.close()
    assert ('inet 192.168.122' not in output_eth3)
