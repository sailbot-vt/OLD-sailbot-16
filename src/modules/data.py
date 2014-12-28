import json

class Data:
    """ Data types included in this class:
        timestamp, lat, long, target_lat, target_long, heading, speed, wind_dir,
        roll, pitch, yaw, state
    """
    
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
    
    def update_attribute(self, name, value):
        if name in self.__dict__.keys():
            self.__dict__[name] = value;
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
