# coding = utf-8
# Create date: 2019-4-1
# Author :Hailong

from utils.connect_to_os import executor


def test_cli_config_merge(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]
    c_set_console = '''
        echo "#cloud-config" >> config.yml
        echo "rancher: " >> config.yml
        echo "  console: debian" >> config.yml
        '''
    executor(client, c_set_console)
    executor(client, 'cat config.yml | sudo ros config merge')
    output_get_console = executor(client, 'sudo ros config get rancher.console')
    assert ('debian' in output_get_console)

    c_set_debug = '''
        echo "#cloud-config" >> config1.yml
        echo "rancher: " >> config1.yml
        echo "  debug: true" >> config1.yml
        '''
    executor(client, c_set_debug)
    executor(client, 'sudo ros config merge -i config1.yml')
    output_get_debug = executor(client, 'sudo ros config get rancher.debug')
    assert ('true' in output_get_debug)
