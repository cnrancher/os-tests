# coding = utf-8
# Create date: 2018-11-24
# Author :Bowen Lee

import time
from utils.connect_to_os import connection, executor


def test_cmdline(ros_kvm_init, cloud_config_url):
    extra_args = 'cc.hostname=nope rancher.password=three'
    args = ' --append "cc.something=yes rancher.password=two -- {extra_args}"'.format(
        extra_args=extra_args)
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url),
                  extra_install_args=args,
                  is_install_to_hard_drive=True)

    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    hostname = executor(client, 'hostname')
    assert ('nope\n' == hostname)

    output_of_cmdline = executor(client, 'cat /proc/cmdline')
    assert (extra_args not in output_of_cmdline)

    extra_cmdline = executor(client, 'sudo ros config get rancher.environment.EXTRA_CMDLINE')
    assert ('/init {extra_args}'.format(extra_args=extra_args) in extra_cmdline)

    rancher_password = executor(client, 'sudo ros config get rancher.password')
    assert ('\n' == rancher_password)

    config_password = executor(client, 'sudo ros config export | grep password')
    assert ('EXTRA_CMDLINE: /init cc.hostname=nope rancher.password=three' in config_password)

    test_yml = "echo -e 'test:\n  image: alpine\n  command: \"echo tell me a secret ${EXTRA_CMDLINE}\"\n  labels:\n    io.rancher.os.scope: system\n  environment:\n  - EXTRA_CMDLINE\n'> test.yml"

    executor(client, test_yml)

    executor(client, 'sudo mv test.yml /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service enable /var/lib/rancher/conf/test.yml')
    executor(client, 'sudo ros service up test')
    test_content = 'test_1 | tell me a secret /init cc.hostname=nope rancher.password=three\n'
    output_test = executor(client, 'sudo ros service logs test | grep secret')
    assert (test_content.replace('\n', '') in output_test)
