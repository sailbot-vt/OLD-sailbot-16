import math
import ship_data

def direction_to_point(current_point, target_point):
    a = math.radians(current_point['latitude'])
    b = math.radians(target_point['latitude'])
    d = math.radians(target_point['longitude'] - current_point['longitude'])

    y = math.sin(d) * math.cos(b)
    x = math.cos(a) * math.sin(b) - math.sin(a) * math.cos(b) * math.cos(d)

    return (math.degrees(math.atan2(y, x)) + 360) % 360

def get_heading_angle(heading, current_point, target_point):
    angle = direction_to_point(current_point, target_point)

    return heading - angle

def within_radius_of_target(current_point, target_point):
    return (distance(current_point, target_point) <= ship_data.point_proximity_radius)

def distance(point1, point2):
    a = math.sin(math.radians(point1['latitude']))
    b = math.sin(math.radians(point2['latitude']))
    c = math.cos(math.radians(point1['latitude']))
    d = math.cos(math.radians(point2['latitude']))

    e = a * b + c * d * math.cos((math.radians(point2['longitude'] - point1['longitude'])))
    f = math.acos(e)

    return f * 6371 * 1000
