import json

class Location(object):
    """ Stores latitude and longitude coordinate points
    """

    def __init__(self, latitude_, longitude_):
        self.latitude = latitude_
        self.longitude = longitude_

    def __str__(self):
        return "(%s, %s)" % (self.latitude, self.longitude) 

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
