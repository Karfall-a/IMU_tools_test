import os
from ament_index_python.packages import get_package_share_directory

from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition


def generate_launch_description():

    '''
        Launch-file for testing imu_tools package.\n

        INPUT:\n
        
        filter - arg that define the type of used filter (none by default)\n
        rosbag_name - arg that define used rosbag-file (imu_dataset from demo by default). Rosbag-file must be in imu_launcher/rosbag directory.\n

        HOW TO USE:\n

        Enter in Terminal:\n

        ros2 launch imu_launcher imu_tools_test.launch.py filter:={complementary, madgwick, none} rosbag_name:={your_rosbag}\n

        After it, you will see the visualisation of choosen filter in Rviz2.\n

        Made by A. Kopan for test stage in Polytech Voltage Machine.\n
    '''

    # Getting the path to the package
    package_name = 'imu_launcher'
    package_path = get_package_share_directory(package_name)

    #Declaring the filter arg
    filtering = DeclareLaunchArgument(
        name='filter',
        default_value='none',
        description='Choosen type of filter: madgwick, complementary or none (default)'
    )

    #Getting paths for Rviz configs for every filter type
    rviz_config_none_path = os.path.join(package_path, 'rviz', 'none.rviz')
    rviz_config_madgwick_path = os.path.join(package_path, 'rviz', 'madgwick.rviz')
    rviz_config_complementary_path = os.path.join(package_path, 'rviz', 'complementary.rviz')

    #Choosing the Rviz config by filter type
    rviz_config_path = PythonExpression([
        '"', 
        rviz_config_complementary_path, '" if "', LaunchConfiguration('filter'), '" == "complementary" else ',
        '"', rviz_config_madgwick_path, '" if "', LaunchConfiguration('filter'), '" == "madgwick" else ',
        '"', rviz_config_none_path, '"'
    ])

    #Declaring the rosbag_name arg
    rosbag_name = DeclareLaunchArgument(
        name='rosbag_name',
        default_value='imu_dataset.db3',
        description='ROS bag file name'
    )

    #Getting the path of rosbag-file
    rosbag_path = PythonExpression([
        '"', package_path, '/rosbag/', LaunchConfiguration('rosbag_name'), '"'
    ])


    #Playing the rosbag
    start_rosbag = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', rosbag_path],
        output='screen',
    )

    #Starting Rviz with configuration
    start_rviz_imu = ExecuteProcess(
        cmd=['rviz2', '-d', rviz_config_path],
        output='screen',
    )

    #Starting complementary filter node (if it has been chosen)
    start_complementary = Node(
        package='imu_complementary_filter',
        executable='complementary_filter_node',
        name='complementary_filter_gain_node',
        output='screen',
        parameters=[
            {'do_bias_estimation': True},
            {'do_adaptive_gain': True},
            {'use_mag': False},
            {'gain_acc': 0.01},
            {'gain_mag': 0.01},
        ],
        condition=IfCondition(PythonExpression(['"', LaunchConfiguration('filter'), '" == "complementary"']))
    )

    #Starting madgwick filter node (if it has been chosen)
    config_dir = os.path.join(get_package_share_directory('imu_filter_madgwick'), 'config')
    start_madgwick = Node(
        package='imu_filter_madgwick',
        executable='imu_filter_madgwick_node',
        name='imu_filter',
        output='screen',
        parameters=[os.path.join(config_dir, 'imu_filter.yaml')],
        condition=IfCondition(PythonExpression(['"', LaunchConfiguration('filter'), '" == "madgwick"']))
    )

    return LaunchDescription([
        #args
        filtering,
        rosbag_name,

        #filter
        start_complementary,
        start_madgwick,

        #rviz
        start_rviz_imu,

        #rosbag
        start_rosbag
    ])