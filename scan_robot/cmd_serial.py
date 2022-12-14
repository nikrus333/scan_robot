from time import sleep, time
from math import pi, sin, cos, tan, sqrt, radians
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from geometry_msgs.msg import Quaternion

class TfBroadCast(Node):
    def __init__(self):
        super().__init__('tf_camera')
        self.odom_broadcaster = TransformBroadcaster(self)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.x = -0.7
        self.y = -4.5
        self.theta = 0.0

        self.angle = 0

        self.x_camera = 0.0
        self.y_camera = 0.0
        self.z_camera = 0.3
        self.timeold = self.get_clock().now().nanoseconds
        timer_period = 0.01  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        
        self.tf_call()

    def tf_call(self):
        now =  self.get_clock().now()
        quaternion = Quaternion()
        quaternion.x = 0.0
        quaternion.y = 0.0
        quaternion.z = sin(2/ 2)
        quaternion.w = cos(0.5/ 2)
        transform_stamped_msg = TransformStamped()
        transform_stamped_msg.header.stamp = now.to_msg()
        transform_stamped_msg.header.frame_id = 'world'
        transform_stamped_msg.child_frame_id = 'copter_desired'
        transform_stamped_msg.transform.translation.x = self.x
        transform_stamped_msg.transform.translation.y = self.y
        transform_stamped_msg.transform.translation.z = 0.5
        transform_stamped_msg.transform.rotation.x = quaternion.x
        transform_stamped_msg.transform.rotation.y = quaternion.y
        transform_stamped_msg.transform.rotation.z = quaternion.z
        transform_stamped_msg.transform.rotation.w = quaternion.w
        self.odom_broadcaster.sendTransform(transform_stamped_msg)

        transform_stamped_msg1 = TransformStamped()
        transform_stamped_msg1.header.stamp = now.to_msg()
        transform_stamped_msg1.header.frame_id = 'world'
        transform_stamped_msg1.child_frame_id = 'camera_desired'
        self.x_camera, self.y_camera = self._physics_process(self.angle)
        transform_stamped_msg1.transform.translation.x = self.x_camera
        transform_stamped_msg1.transform.translation.y = self.y_camera
        transform_stamped_msg1.transform.translation.z = self.z_camera
        #roll, pitch, yaw = self.coord_to_angle()
        #q = self.quaternion_from_euler(roll, pitch, yaw)
        x_norm, y_norm, z_norm = self.normalize()
        quaternion.x = x_norm
        quaternion.y = y_norm
        quaternion.z = z_norm
        quaternion.w = 0.6
        transform_stamped_msg1.transform.rotation.x = quaternion.x
        transform_stamped_msg1.transform.rotation.y = quaternion.y
        transform_stamped_msg1.transform.rotation.z = quaternion.z
        transform_stamped_msg1.transform.rotation.w = quaternion.w
        self.tf_broadcaster.sendTransform(transform_stamped_msg1)
    
    def quaternion_from_euler(self, roll, pitch, yaw):    
        cy = cos(yaw * 0.5)
        sy = sin(yaw * 0.5)
        cp = cos(pitch * 0.5)
        sp = sin(pitch * 0.5)
        cr = cos(roll * 0.5)
        sr = sin(roll * 0.5)
        q = [0] * 4
        q[0] = cy * cp * cr + sy * sp * sr
        q[1] = cy * cp * sr - sy * sp * cr
        q[2] = sy * cp * sr + cy * sp * cr
        q[3] = sy * cp * cr - cy * sp * sr
        return q
    
    def _physics_process(self, delta):
        self.angle += 0.01
        r = 1
        if self.angle >= 360:
            self.angle = 0
        y = r*sin(self.angle)
        x = r*cos(self.angle)
        return x ,y

    def coord_to_angle(self):
        roll = sqrt(self.x_camera*2 + self.y_camera*2 + self.z_camera*2)
        pitch = math.atan(sqrt(self.x_camera*2 + self.y_camera*2)/ self.z_camera)
        yaw = math.atan(self.y_camera / self.x_camera) + pi
        return roll , pitch, yaw

    def normalize(self):
        len_vectorr = sqrt(self.x_camera**2 + self.y_camera**2 + self.z_camera**2)
        x_norm = self.x_camera * (1/len_vectorr)
        y_norm = self.y_camera * (1/len_vectorr)
        z_norm = self.z_camera * (1/len_vectorr)
        return x_norm, y_norm, z_norm
        

def main(args=None):
    rclpy.init(args=args)
    minimal_subscriber = TfBroadCast()
    rclpy.spin(minimal_subscriber)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()