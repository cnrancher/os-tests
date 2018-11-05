# coding = utf-8
# Create date: 2018-10-29
# Author :Bowen Lee


import os

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':

    try:
        pytest.main(
            ["-s",
             BASE_DIR + '{script_package}'.format(script_package='/project_path/engine/'),
             '--cloud_config_url={url}'.format(url='http://192.168.1.24/ros')])
    except Exception as e:
        print(e.args[0])
