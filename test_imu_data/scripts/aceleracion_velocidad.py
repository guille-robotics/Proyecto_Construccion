#!/usr/bin/env python3

import rospy
from sensor_msgs.msg import Imu
from SerialHandler import SerialHandler
from XbusPacket import XbusPacket
from DataPacketParser import DataPacketParser, XsDataPacket
from SetOutput import set_output_conf

def on_live_data_available(packet):
    xbus_data = XsDataPacket()
    DataPacketParser.parse_data_packet(packet, xbus_data)

    imu_msg = Imu()

    # Inicializa roll, pitch, yaw, rate_of_turn y acceleration con valores predeterminados
    roll, pitch, yaw = 0.0, 0.0, 0.0
    rate_of_turn = [0.0, 0.0, 0.0]
    acceleration = [0.0, 0.0, 0.0]

    if xbus_data.eulerAvailable:
        roll, pitch, yaw = xbus_data.euler
        
        # Asignamos los valores de roll, pitch y yaw a la orientación
        imu_msg.orientation.x = roll
        imu_msg.orientation.y = pitch
        imu_msg.orientation.z = yaw
        imu_msg.orientation.w = 0  # Puedes calcular o asignar w si lo necesitas

    if xbus_data.rotAvailable:
        rate_of_turn = [
            xbus_data.rot[0],  # Velocidad angular en rad/s alrededor del eje X
            xbus_data.rot[1],  # Velocidad angular en rad/s alrededor del eje Y
            xbus_data.rot[2]   # Velocidad angular en rad/s alrededor del eje Z
        ]
        imu_msg.angular_velocity.x = rate_of_turn[0]
        imu_msg.angular_velocity.y = rate_of_turn[1]
        imu_msg.angular_velocity.z = rate_of_turn[2]

    if xbus_data.accAvailable:
        acceleration = [
            xbus_data.acc[0],  # Aceleración en m/s² en el eje X
            xbus_data.acc[1],  # Aceleración en m/s² en el eje Y
            xbus_data.acc[2]   # Aceleración en m/s² en el eje Z
        ]
        imu_msg.linear_acceleration.x = acceleration[0]
        imu_msg.linear_acceleration.y = acceleration[1]
        imu_msg.linear_acceleration.z = acceleration[2]

    # Publicar el mensaje IMU
    imu_pub.publish(imu_msg)
    rospy.loginfo(f"Published Roll, Pitch, Yaw: [{roll:.2f}, {pitch:.2f}, {yaw:.2f}], "
                  f"Angular Velocity: [{rate_of_turn[0]:.2f}, {rate_of_turn[1]:.2f}, {rate_of_turn[2]:.2f}], "
                  f"Acceleration: [{acceleration[0]:.2f}, {acceleration[1]:.2f}, {acceleration[2]:.2f}]")

def main():
    rospy.init_node('imu_publisher', anonymous=True)
    global imu_pub
    imu_pub = rospy.Publisher('/imu/raw', Imu, queue_size=10)

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

