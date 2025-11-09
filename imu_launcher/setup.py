from setuptools import setup
import os
from glob import glob

package_name = 'imu_launcher'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'rosbag'), glob('rosbag/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')), 
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='karfall',
    maintainer_email='karfall115@gmail.com',
    description='Launcher for testing of imu_tools package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
