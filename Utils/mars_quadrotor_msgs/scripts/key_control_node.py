#!/usr/bin/env python3
# -*- coding: utf-8 -*  
  
import os  
import sys  
import tty, termios  
import roslib 
import rospy
from quadrotor_msgs.msg import PositionCommand_back,PositionCommand
from nav_msgs.msg import Odometry
  
class KeyControlNode():
    def __init__(self):
        rospy.init_node('key_control_node')
        self.pos_cmd  = PositionCommand_back()
        self.x = 0
        self.y = 0
        self.z = 0
        self.pub_planning_pos_cmd = rospy.Publisher('/quad_0/planning/pos_cmd', PositionCommand_back, queue_size=10)
        self.sub_odom = rospy.Subscriber("/quad_0/lidar_slam/odom", Odometry, self.OdometryCallback)
    
    def OdometryCallback(self, data):
        position = data.pose.pose.position
        self.x = position.x
        self.y = position.y
        self.z = position.z

    def keyDetect(self):
        thread_stop = False
        rate = rospy.Rate(10)
        vel = PositionCommand_back().velocity
        dv = 0.5
        dt = 0.8
        while not thread_stop: 
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try :
                tty.setraw( fd )
                ch = sys.stdin.read(1)
            finally :
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print(ch)
            if ch == 'w':  
                vel.x = dv
            elif ch == 's':  
                vel.x = -dv
            elif ch == 'a':  
                vel.y = dv
            elif ch == 'd':  
                vel.y = -dv
            elif ch == 'z':
                vel.z = dv
            elif ch == 'x':
                vel.z = -dv
            elif ch == 'q': 
                thread_stop = True     
            msg_pos_cmd = PositionCommand_back()
            msg_pos_cmd.position.x = self.x + dt * vel.x
            msg_pos_cmd.position.y = self.y + dt * vel.y
            msg_pos_cmd.position.z = self.z + dt * vel.z
            msg_pos_cmd.velocity = vel
            self.pub_planning_pos_cmd.publish(msg_pos_cmd)
            vel.x = 0
            vel.y = 0
            vel.z = 0
            rate.sleep()
   
if __name__ == '__main__':  
    keyControlNode = KeyControlNode()
    keyControlNode.keyDetect()
