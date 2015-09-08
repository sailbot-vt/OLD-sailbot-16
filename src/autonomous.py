#!/usr/bin/python
import threading, modules.calc, logging, socket, time, sys, curses
from modules.data import DataThread
from modules.logic import LogicThread
from modules.utils import SocketType, socket_connect

logger = logging.getLogger('log')

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
    threading.current_thread().setName('Main')

    modules.utils.setup_locations(values['target_locations'], values['boundary_locations'])
    modules.utils.spawn_processes()

    time.sleep(0.5)
    logger.info('Starting SailBOT!')
    time.sleep(0.5)

    data_thread = DataThread(name='Data', kwargs={'values': values, 'data': data})
    logic_thread = LogicThread(name='Logic', kwargs={'values': values, 'data': data, 'data_thread': data_thread})
    data_thread.start()
    logic_thread.start()

    arduino_sock = socket_connect(SocketType.arduino)

    while True:
        try:
            time.sleep(0.5)
            modules.utils.update_terminal_display(data, values)
        except KeyboardInterrupt:
            logger.critical('Program terminating!')

            # Stop the threads
            data_thread.stop()
            logic_thread.stop()

            # Join the threads into the main threads
            data_thread.join()
            logic_thread.join()
            modules.utils.shutdown_terminal()
            # Terminate the program
            logger.critical('Autonomous gracefully exited!')

            sys.exit()

if __name__ == '__main__':
    modules.utils.setup_terminal_logging()
    main()
