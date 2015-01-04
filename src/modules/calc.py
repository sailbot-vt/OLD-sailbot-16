#!/usr/bin/python

import math

""" The file contains help methods to logic functions.
    These are object independent; they only need the data given as parameters
    to return a result.
"""

def direction_to_point(current, target):
    a = math.radians(current.latitude)
    b = math.radians(target.latitude)
    d = math.radians(target.longitude - current.longitude)
    
    y = math.sin(d) * math.cos(b)
    x = math.cos(a) * math.sin(b) - math.sin(a) * math.cos(b) * math.cos(d)
    
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def point_proximity(current, target):
    a = math.sin(math.radians(current.latitude))
    b = math.sin(math.radians(target.latitude))
    c = math.cos(math.radians(current.latitude))
    d = math.cos(math.radians(target.latitude))
    
    e = a * b + c * d * math.cos((math.radians(target.longitude - current.longitude)))
    f = math.acos(e)
    distance = f * 6371 * 1000
    
    return (distance <= 5) # point_proximity_radius can be changed


            