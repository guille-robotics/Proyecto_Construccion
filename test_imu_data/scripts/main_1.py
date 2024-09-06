#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Imu
from geometry_msgs.msg import TransformStamped
import tf2_ros
from SerialHandler import SerialHandler
from XbusPacket import XbusPacket
from DataPacketParser import DataPacketParser, XsDataPacket
from SetOutput import set_output_conf

def on_live_data_available(packet):
    xbus_data = XsDataPacket()
    DataPacketParser.parse_data_packet(packet, xbus_data)

    if xbus_data.eulerAvailable:
        roll, pitch, yaw = xbus_data.euler
        imu_msg = Imu()
        
        # Asignar los valores de Roll, Pitch, Yaw a la orientación
        imu_msg.orientation.x = roll
        imu_msg.orientation.y = pitch
        imu_msg.orientation.z = yaw
        imu_msg.orientation.w = 0  # Puedes calcular o asignar w si lo necesitas

        imu_pub.publish(imu_msg)
        rospy.loginfo(f"Published Roll, Pitch, Yaw: [{roll:.2f}, {pitch:.2f}, {yaw:.2f}]")

        # Publicar la transformación
        t = TransformStamped()
        t.header.stamp = rospy.Time.now()
        t.header.frame_id = "map"
        t.child_frame_id = "imu_link"
        t.transform.translation.x = 0
        t.transform.translation.y = 0
        t.transform.translation.z = 0
        t.transform.rotation.x = roll
        t.transform.rotation.y = pitch
        t.transform.rotation.z = yaw
        t.transform.rotation.w = 1.0  # Ajustar según sea necesario
        tf_broadcaster.sendTransform(t)

def main():
    rospy.init_node('imu_publisher', anonymous=True)
    global imu_pub, tf_broadcaster
    imu_pub = rospy.Publisher('/imu/data_raw', Imu, queue_size=10)
    tf_broadcaster = tf2_ros.TransformBroadcaster()

    try:
        serial = SerialHandler("/dev/ttyUSB0", 115200)  # Cambia el puerto y baudrate según tu configuración
        packet = XbusPacket(on_data_available=on_live_data_available)

        go_to_config = bytes.fromhex('FA FF 30 00')
        go_to_measurement = bytes.fromhex('FA FF 10 00')
        serial.send_with_checksum(go_to_config)
        set_output_conf(serial)
        serial.send_with_checksum(go_to_measurement)

        rospy.loginfo("Listening for packets...")

        while not rospy.is_shutdown():
            byte = serial.read_byte()
            packet.feed_byte(byte)

    except Exception as e:
        rospy.logerr(f"Error: {e}")
        return 1

    return 0

if __name__ == '__main__':
    main()

