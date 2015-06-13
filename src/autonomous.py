#!/usr/bin/python
import threading, modules.calc, logging, socket, time, sys
from modules.data import DataThread
from modules.logic import LogicThread

# Variables and constants
data = {'category': 'data', 'timestamp': 0, 'location': { "latitude": 0, "longitude": 0 },
        'heading': 0, 'speed': 0, 'wind_dir': 0, 'roll': 0, 'pitch': 0,
        'yaw': 0}

# Specifies the default values
values = {'event': 'default', 'debug': False, 'port': 80, 'transmission_delay': 5, 'eval_delay': 5, 'current_desired_heading': 0,
          'direction': 0, 'absolute_wind_direction': 0, 'max_turn_rate_angle': 70, 'max_rudder_angle': 40, 'max_winch_angle': 70,
          'tack_angle': 45, 'gybe_angle': 20, 'preferred_tack': 0, 'preferred_gybe': 0, 'winch_angle': 0, 'rudder_angle': 0, 'start_time': 0,
          'target_locations': [], 'boundary_locations': [], 'location_pointer': 0 }

def main():
    try:
        threading.current_thread().setName('Main')

        # Sets up the program configuration
        modules.utils.setup_config(values)
        if values['debug']:
            modules.utils.setup_logging()
            
        modules.utils.setup_locations(values['target_locations'], values['boundary_locations'])

        logging.info('Starting SailBOT!')

        data_thread = DataThread(name='Data', kwargs={'values': values, 'data': data})
        logic_thread = LogicThread(name='Logic', kwargs={'values': values, 'data': data, 'data_thread': data_thread})

        # Start the threads
        data_thread.start()
        logic_thread.start()

        # Create the Arduino socket
        try:
            arduino_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            arduino_sock.connect(("localhost", 7893))
        except socket.error:
            logging.critical("Could not connect to Arduino socket")
            pass

        time.sleep(5)

        while True:
            try:
                # Query the Arduino socket
                arduino_sock.send(str(0).encode('utf-8'))
                states = json.loads(arduino_sock.recv(128).decode('utf-8'))

                # If the RC controller switch is turned off, leave the main loop and kill the threads
                if not states['switch']:
                    logging.critical('Autonomous shutting down! Going back to manual control!')

                    # Stop the threads
                    data_thread.stop()
                    logic_thread.stop()

                    # Join the threads into the main threads
                    data_thread.join()
                    logic_thread.join()

                    # Terminate the program
                    logging.critical('Autonomous gracefully exited!')
                    break

            except socket.error:
                logging.critical("Could not connect to the Arduino socket, check your wiring!")

            modules.utils.print_terminal(data, values)
            time.sleep(0.005)

    except KeyboardInterrupt:
        logging.critical('Program terminating!')
        # Stop the threads
        data_thread.stop()
        logic_thread.stop()

        # Join the threads into the main threads
        data_thread.join()
        logic_thread.join()

        # Terminate the program
        logging.critical('Program exited!')
        sys.exit()

if __name__ == '__main__':
    main()
            