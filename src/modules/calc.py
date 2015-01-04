#!/usr/bin/python

import math

""" The file contains help methods to logic functions.
    These are object independent; they only need the data given as parameters
    to return a result.
"""

def direction_to_point(current, target):
    dist_lat = 111132.954 - 559.822 * math.cos(2 * current.latitude) \
        + 1.1175 * math.cos(4 * current.latitude)
    dist_lon = math.pi / 180 * 6367449 * math.cos(current.latitude)

    lat_meter = math.fabs(math.fabs(target.latitude) - math.fabs(current.latitude)) * dist_lat
    lon_meter = math.fabs(math.fabs(target.longitude) - math.fabs(current.longitude)) * dist_lon

    difference = lat_meter / lon_meter
    degree = math.fabs(math.atan(difference) * 180 / math.pi)

    angle = 0

    if (target.latitude >= current.latitude) & (target.longitude >= current.longitude):
        angle = 90 - degree
    elif (target.latitude <= current.latitude) & (target.longitude >= current.longitude):                                                              
        angle = 90 + degree
    elif (target.latitude <= current.latitude) & (target.longitude <= current.longitude):
        angle = 270 - degree
    elif (target.latitude >= current.latitude) & (target.longitude <= current.longitude):
        angle = 270 + degree

    return angle

def point_proximity(current, target):
    a = math.sin(math.radians(current.latitude))
    b = math.sin(math.radians(target.latitude))
    c = math.cos(math.radians(current.latitude))
    d = math.cos(math.radians(target.latitude))
    
    e = a * b + c * d * math.cos((math.radians(target.longitude - current.longitude)))
    f = math.acos(e)
    distance = f * 6371 * 1000
    
    return (distance <= 5) # point_proximity_radius can be changed


            