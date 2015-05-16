#!/usr/bin/python
import math

""" The file contains help methods to logic functions.
    These are object independent; they only need the data given as parameters
    to return a result.
"""

point_proximity_radius = 5

def direction_to_point(current_point, target_point):
    a = math.radians(current_point.latitude)
    b = math.radians(target_point.latitude)
    d = math.radians(target_point.longitude - current_point.longitude)
    
    y = math.sin(d) * math.cos(b)
    x = math.cos(a) * math.sin(b) - math.sin(a) * math.cos(b) * math.cos(d)
    
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def get_heading_angle(heading, current_point, target_point):
    angle = direction_to_point(current_point, target_point)
    
    return heading - angle

def point_proximity(current_point, target_point):
    a = math.sin(math.radians(current_point.latitude))
    b = math.sin(math.radians(target_point.latitude))
    c = math.cos(math.radians(current_point.latitude))
    d = math.cos(math.radians(target_point.latitude))
    
    e = a * b + c * d * math.cos((math.radians(target_point.longitude - current_point.longitude)))
    f = math.acos(e)
    distance = f * 6371 * 1000
    
    return (distance <= point_proximity_radius)


            