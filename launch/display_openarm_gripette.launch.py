import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch import LaunchContext
from launch_ros.actions import Node


def nodes_spawner(context: LaunchContext, use_fake_hardware):
    use_fake_str = context.perform_substitution(use_fake_hardware)

    urdf_path = os.path.join(
        get_package_share_directory("openarm_gripette_description"),
        "urdf", "openarm_right_gripette.urdf"
    )
    with open(urdf_path, "r") as f:
        robot_description = f.read()

    rviz_config_path = os.path.join(
        get_package_share_directory("openarm_description"),
        "rviz", "openarm_gripette.rviz"
    )

    nodes = [
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{"robot_description": robot_description}],
        ),
        Node(
            package="rviz2",
            executable="rviz2",
            name="rviz2",
            arguments=["--display-config", rviz_config_path],
            output="screen",
        ),
    ]

    # With fake hardware, add the GUI slider to drive joint states manually.
    # With real hardware, joint states come from the running ros2_control stack.
    if use_fake_str.lower() == "true":
        nodes.append(Node(
            package="joint_state_publisher_gui",
            executable="joint_state_publisher_gui",
            name="joint_state_publisher_gui",
        ))

    return nodes


def generate_launch_description():
    use_fake_hardware_arg = DeclareLaunchArgument(
        "use_fake_hardware",
        default_value="true",
        description="Use joint_state_publisher_gui instead of real hardware joint states.",
    )

    return LaunchDescription([
        use_fake_hardware_arg,
        OpaqueFunction(
            function=nodes_spawner,
            args=[LaunchConfiguration("use_fake_hardware")],
        ),
    ])
