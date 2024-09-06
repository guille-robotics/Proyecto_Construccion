#include <ros/ros.h>
#include <sensor_msgs/Imu.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/TransformStamped.h>

class IMUTransformPublisher
{
public:
    IMUTransformPublisher()
    {
        // Suscribirse al tópico del IMU
        imu_sub_ = nh_.subscribe("/imu/data", 10, &IMUTransformPublisher::imuCallback, this);
    }

    void imuCallback(const sensor_msgs::Imu::ConstPtr& imu_msg)
    {
        // Obtener roll, pitch, yaw desde el mensaje de IMU
        double roll = imu_msg->orientation.x;
        double pitch = imu_msg->orientation.y;
        double yaw = imu_msg->orientation.z;

        // Convertir a cuaternión
        tf2::Quaternion q;
        q.setRPY(roll, pitch, yaw);

        // Crear el mensaje de transformación
        geometry_msgs::TransformStamped transformStamped;
        transformStamped.header.stamp = ros::Time::now();
        transformStamped.header.frame_id = "base_link"; // El frame base de tu robot
        transformStamped.child_frame_id = "imu_link";   // El frame donde está el IMU

        // Posición
        transformStamped.transform.translation.x = 0.0;
        transformStamped.transform.translation.y = 0.0;
        transformStamped.transform.translation.z = 0.0;

        // Orientación
        transformStamped.transform.rotation.x = q.x();
        transformStamped.transform.rotation.y = q.y();
        transformStamped.transform.rotation.z = q.z();
        transformStamped.transform.rotation.w = q.w();

        // Publicar la transformación
        tf_broadcaster_.sendTransform(transformStamped);
    }

private:
    ros::NodeHandle nh_;
    ros::Subscriber imu_sub_;
    tf2_ros::TransformBroadcaster tf_broadcaster_;
};

int main(int argc, char** argv)
{
    ros::init(argc, argv, "imu_transform_publisher");

    IMUTransformPublisher imu_transform_publisher;

    ros::spin();

    return 0;
}

