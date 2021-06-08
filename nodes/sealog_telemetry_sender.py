#!/usr/bin/env python

import math
import socket
import rospy
import datetime
import tf2_ros
from nav_msgs.msg import Odometry
from tf2_geometry_msgs import do_transform_pose
from tf.transformations import euler_from_quaternion
import project11

rospy.init_node('send_telemetry_to_sealog')
host = rospy.get_param('~host')
port = rospy.get_param('~port')
period = rospy.get_param('~period', 1.0)

outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

tfBuffer = tf2_ros.Buffer()
tfListener = tf2_ros.TransformListener(tfBuffer)

lastReportTime = None

def odometryCallback( data):
  global lastReportTime
  if lastReportTime is None or data.header.stamp - lastReportTime > rospy.Duration(period):

    try:
      ts = datetime.datetime.utcfromtimestamp(data.header.stamp.to_sec())
      #print("odom frame_id:", data.header.frame_id)
      odom_to_earth = tfBuffer.lookup_transform("earth", data.header.frame_id, data.header.stamp, rospy.Duration(period))
      ecef = do_transform_pose(data.pose, odom_to_earth).pose.position
      position = project11.wgs84.fromECEFtoLatLong(ecef.x, ecef.y, ecef.z)
      lat, lon = math.degrees(position[0]), math.degrees(position[1])
      
      o = data.pose.pose.orientation
      q = (o.x, o.y, o.z, o.w)
      heading = (90-math.degrees(euler_from_quaternion(q)[2]))%360.0

      cog = (heading-math.degrees(math.atan2(data.twist.twist.linear.y, data.twist.twist.linear.x)))%360.0
      sog = math.sqrt(data.twist.twist.linear.x**2 + data.twist.twist.linear.y**2)

      data_string = ','.join((ts.isoformat(), str(lat), str(lon), str(heading), str(cog), str(sog)))
      #print (data_string)
      outsock.sendto((data_string+'\n').encode('utf-8'), (host,port))
    except Exception as e:
      print(e)

    lastReportTime = data.header.stamp

odom_sub = rospy.Subscriber('odom', Odometry, odometryCallback, queue_size = 1)

rospy.spin()
