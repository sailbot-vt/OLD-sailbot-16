__author__ = 'jbs'

import ship_data

def test():
    print ship_data.boat_heading
    ship_data.boat_heading = 7
    print ship_data.boat_heading

test()