__author__ = 'jbs'

import ship_data

#wind angles that make the sail fully-in and sail fully-out
sail_in_wind_angle = 60
sail_out_wind_angle = 120

#winch servo fully-in and fully-out values
winch_min = 40
winch_max = 85

def setRudderAngle(targetHeading):
    current_heading = ship_data.boat_heading
    angleToTurn = targetHeading - current_heading

    ship_data.rudder_servo_angle = 90 - angleToTurn/10

    socket_communicator.set_rudder_servo_angle(ship_data.rudder_servo_angle)

def setWinchAngle(targetHeading):
    wind_angle_ratio = (ship_data.relative_wind_heading - sail_in_wind_angle)/(sail_out_wind_angle - sail_in_wind_angle)

    if(wind_angle_ratio > 1):
        wind_angle_ratio = 1
    if(wind_angle_ratio < 0):
        wind_angle_ratio = 0

    ship_data.winch_servo_angle = winch_angle = (winch_min + winch_max)/2 + (winch_max - winch_min)*(wind_angle_ratio)

    socket_communicator.set_winch_servo_angle(ship_data.winch_servo_angle)