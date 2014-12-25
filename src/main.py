import time
from server import ServerThread
from data import Data
import threading

def set(property, value):
    try:
        f = open("/sys/class/rpi-pwm/pwm0/" + property, 'w')
        f.write(value)
        f.close()    
    except:
        print("Error writing to: " + property + " value: " + value)

def setServo(angle):
    set("servo", str(angle))
    
def configureServos():
    set("delayed", "0")
    set("mode", "servo")
    set("servo_max", "180")
    set("active", "1")

## ----------------------------------------------------------

print("Beginning SailBOT autonomous navigation routines\n");

# Variables and constants
data = Data(timestamp=0, lat=0, long=0, target_lat=0, target_long=0, heading=0,
          speed=0, wind_dir=0, roll=0, pitch=0, yaw=0, state=0)

DELAY_PERIOD = 0.01

# Setup methods
configureServos()


## ----------------------------------------------------------

class Thread01(threading.Thread):

    def run(self):
        while True:
            
            for angle in range(0, 180):
                # setServo(angle)
                time.sleep(DELAY_PERIOD)
            for angle in range(0, 180):
                # setServo(180 - angle)
                time.sleep(DELAY_PERIOD)

