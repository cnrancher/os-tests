# coding = utf-8
# Create date: 2019-4-4
# Author :Hailong

from utils.connect_to_os import executor


def test_zfs(ros_kvm_init, cloud_config_url):
    kwargs = dict(cloud_config='{url}default.yml'.format(url=cloud_config_url), is_install_to_hard_drive=True,
                  is_second_hd=True)
    tuple_return = ros_kvm_init(**kwargs)
    client = tuple_return[0]

    c_enable_zfs = 'sudo ros service enable zfs && \
                    sudo ros service up zfs'
    executor(client, c_enable_zfs, 1800)
    o_ls_zfs_mod = executor(client, 'lsmod | grep zfs')
    assert ('zfs' in o_ls_zfs_mod)

    # Creating ZFS pools
    c_create_zfs_pools = 'sudo zpool create zpool1 -m /mnt/zpool1 /dev/vdb && \
                            sudo cp /etc/* /mnt/zpool1 && \
                            docker run --rm -it -v /mnt/zpool1/:/data alpine ls -la /data'
    # ZFS storage for Docker on RancherOS
    c_use_zfs = 'sudo system-docker stop docker && \
                    sudo rm -rf /var/lib/docker/* && \
                    sudo zfs create zpool1/docker && \
                    sudo zfs list -o name,mountpoint,mounted && \
                    sudo ros config set rancher.docker.storage_driver "zfs" && \
                    sudo ros config set rancher.docker.graph /mnt/zpool1/docker && \
                    sudo system-docker start docker && \
                    sleep 5'
    executor(client, c_create_zfs_pools)
    executor(client, c_use_zfs)

    o_zpool_ls = executor(client, 'sudo zpool list')
    o_zfs_ls = executor(client, 'sudo zfs list')
    o_docker_storage_driver = executor(client, 'docker info --format "{{json .Driver}}"')
    assert ('zpool1' in o_zpool_ls and 'zpool1' in o_zfs_ls)
    assert ('zfs' in o_docker_storage_driver)
