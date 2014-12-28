import time
from modules.server import ServerThread
from modules.data import Data
import threading
import json
from modules.location import Location


# Variables and constants
data = Data(timestamp=0, lat=0, long=0, target_lat=0, target_long=0, heading=0,
          speed=0, wind_dir=0, roll=0, pitch=0, yaw=0, state=0)
servos = Data(rutter=0, sail=0)
locations = []


def location_decoder(obj):
    return Location(obj['latitude'], obj['longitude'])

def get_locations():
    try:
        with open ("locations.json", "r") as myfile:
                json_data = myfile.read().replace('\n', '')              
        locations = json.loads(json_data, object_hook=location_decoder)
        
        print("Loaded the following locations:")
        for location in locations:
            print(location.__str__())
        print("\n")
        
    except FileNotFoundError:
        print("[E]: The locations JSON file could not be found!")
    except ValueError:
        print("[E]: The locations JSON file is malformed!")

## ----------------------------------------------------------
                
class DataThread(threading.Thread):
    """ Transmits the data object to the server thread
    """
    
    def run(self):
        print("Starting the data thread!")
        DELAY_PERIOD = 5  # time between transmission in seconds
        server_thread = ServerThread()
        server_thread.start()
        
        while True:
            server_thread.send_data(data.to_JSON())
            print("Data sent to the server")
            time.sleep(DELAY_PERIOD)

## ----------------------------------------------------------           
            
class LogicThread(threading.Thread):
    
    def run(self):
        pass

## ----------------------------------------------------------
    
class MotorThread(threading.Thread):
    
    def set(self, property, value):
        try:
            f = open("/sys/class/rpi-pwm/pwm0/" + property, 'w')
            f.write(value)
            f.close()    
        except:
            print("Error writing to: " + property + " value: " + value)
    
    def setServo(self, angle):
        self.set("servo", str(angle))
        
    def configureServos(self):
        self.set("delayed", "0")
        self.set("mode", "servo")
        self.set("servo_max", "180")
        self.set("active", "1")
        
    def run(self):
        self.configureServos()
            
            
## ----------------------------------------------------------

print("Beginning SailBOT autonomous navigation routines\n");

get_locations()

data_thread = DataThread()
motor_thread = MotorThread()
logic_thread = LogicThread()

data_thread.start()
motor_thread.start()
logic_thread.start()


