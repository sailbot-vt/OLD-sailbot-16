import time
from server import ServerThread

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

DELAY_PERIOD = 0.01

print("Beginning SailBOT autonomous navigation routines\n");
configureServos()

# start server thread
server_thread = ServerThread()
server_thread.start()

server_thread.send_data("Ping!")

while True:
    for angle in range(0, 180):
        # setServo(angle)
        time.sleep(DELAY_PERIOD)
    for angle in range(0, 180):
        # setServo(180 - angle)
        time.sleep(DELAY_PERIOD)

