#!/bin/bash
set -e

BASEPATH=$(cd `dirname $0`; pwd)
PROJECTPATH=$(cd $BASEPATH/..; pwd)
CCROOT=${BASEPATH}/cloud-config
rm -rf ${CCROOT}
mkdir -p ${CCROOT}

USER_DATA=${CCROOT}/openstack/latest/user_data
mkdir -p $(dirname ${USER_DATA})

echo "#cloud-config" > ${USER_DATA}
echo "ssh_authorized_keys:" >> ${USER_DATA}
echo "- $(<${PROJECTPATH}/assets/rancher.key.pub)" >> ${USER_DATA}
truncate --size 2M ${BASEPATH}/configdrive.img
mkfs.vfat -n config-2 ${BASEPATH}/configdrive.img
mcopy -osi ${BASEPATH}/configdrive.img ${CCROOT}/* ::
