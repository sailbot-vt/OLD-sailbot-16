import json

class Data:
    
    def __init__(self, **kwds):
        self.__dict__.update(kwds)
        
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)