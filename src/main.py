import time
from server import ServerThread
from data import Data
import threading
 
## ----------------------------------------------------------
                
class DataThread(threading.Thread):
    """ Transmits the data object to the server thread
    """
    
    def run(self):
        print("Starting the data thread!")
        DELAY_PERIOD = 5 # time between transmission in seconds
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
        set("servo", str(angle))
        
    def configureServos(self):
        set("delayed", "0")
        set("mode", "servo")
        set("servo_max", "180")
        set("active", "1")
        
    def run(self):
        self.configureServos()
            
            
## ----------------------------------------------------------

print("Beginning SailBOT autonomous navigation routines\n");

# Variables and constants
data = Data(timestamp=0, lat=0, long=0, target_lat=0, target_long=0, heading=0,
          speed=0, wind_dir=0, roll=0, pitch=0, yaw=0, state=0)

DELAY_PERIOD = 0.01

data_thread = DataThread()
motor_thread = MotorThread()
logic_thread = LogicThread()

data_thread.start()
motor_thread.start()
logic_thread.start()

