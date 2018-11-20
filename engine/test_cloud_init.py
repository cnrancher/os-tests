# coding = utf-8
# Create date: 2018-11-20
# Author :Hailong
from utils.connect_to_os import executor, connection


def test_cloud_init(ros_kvm_return_ip, cloud_config_url):
    client, ip = ros_kvm_return_ip(cloud_config='{url}/test_cloud_init.yml'.format(url=cloud_config_url))
    c_export_config = 'sudo ros c export'
    output_export_config = executor(client, c_export_config, seconds=30)
    assert ('debug' in output_export_config)

    # Create a datasource file locally
    # test_cloud_init.txt
    # # cloud-config
    #      rancher:
    #          log: true
    c_create_ds = 'sudo tee /var/lib/rancher/conf/cloud-config.d/datasources.yml << EOF \
                    rancher: \
                      cloud_init: \
                        datasources: \
                        - url:https://gist.githubusercontent.com/Aisuko/4914974de1cf2a3d5127fd482e2c001a/raw/\
                        ed1e30a8a096c6e10d485d02092eaaf8ca8871bd/test_cloud_init.txt \
                    EOF'

    # Reboot
    c_reboot = 'sudo reboot'
    executor(client, c_create_ds + c_reboot)

    second_client = connection(ip)

    c_ros_log = 'sudo ros config get rancher.log'
    output_ros_log = executor(second_client, c_ros_log, seconds=10).replace('\n', '')
    second_client.close()
    assert ('true' == output_ros_log)
