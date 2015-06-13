
import logging, socket, time, modules.calc
from .control_thread import StoppableThread

class LogicThread(StoppableThread):
    
    data = None
    values = None

    def __init__(self, *args, **kwargs):
        super(LogicThread, self).__init__(*args, **kwargs)

        global data
        data = self._kwargs['data']

        global values
        values = self._kwargs['values']

    
    def station_keeping(self):
        
        time_elapsed = time.time() - values['start_time']
        
        logging.debug("Station keeping elapsed time: %s" % time_elapsed)
	
        # If the correct amount of time has elapsed (converting minutes to seconds), switch targets
        if time_elapsed > (values['station_keeping_timeout'] * 60):
            for i in range(len(target_locations)):
                    target_locations[i] = Location(0, 0)
            logging.warn("Switched targets!")
	

    def run(self):

        logging.info("Beginning autonomous navigation routines....")
        logging.warn("The angle is: %d" % data['wind_dir'])

        values['start_time'] = time.time()

        while True:

            if self.stopped():
                break

            # Update direction
            values['direction'] = modules.calc.direction_to_point(data['location'], values['target_locations'][values['location_pointer']])
            values['absolute_wind_direction'] = data['wind_dir'] + data['heading']
            
            time.sleep(values['eval_delay'])
            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d, Current Desired Heading: %d, Preferred Tack: %d, Preferred Gybe: %d" % (data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction'], values['current_desired_heading'], values['preferred_tack'], values['preferred_gybe']))
            logging.debug("Upwind: %r, Downwind: %r" % (self.upwind(values['target_locations'][values['location_pointer']]), self.downwind(values['target_locations'][values['location_pointer']])))

            # If it's sailable, go straight to it
            if self.sailable(values['target_locations'][values['location_pointer']]):
                values['current_desired_heading'] = values['direction']
                values['preferred_tack'] = 0
                values['preferred_gybe'] = 0

            # It's not sailable; if it's upwind, tack
            elif self.upwind(values['target_locations'][values['location_pointer']]):
    
                if values['preferred_tack'] == 0:  # If the target's upwind and you haven't chosen a tack, choose one
                    values['preferred_tack'] = (180 - ((data['heading'] - values['absolute_wind_direction']) % 360)) / math.fabs(180 - ((data['heading'] - values['absolute_wind_direction']) % 360))
    
                if values['preferred_tack'] == -1:  # If the boat is on a left-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] - values['tack_angle'] + 360) % 360
                    
                elif values['preferred_tack'] == 1: # If the boat is on a right-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + values['tack_angle'] + 360) % 360
                    
                else:
                    logging.error("The preferred tack was %d" % values['preferred_tack'])

            # Otherwise, gybe
            elif self.downwind(values['target_locations'][values['location_pointer']]):
    
                if values['preferred_gybe'] == 0:  # If the target's downwind and you haven't chosen a gybe, choose one
                    values['preferred_gybe'] = (180 - ((data['heading'] - values['absolute_wind_direction']) % 360)) / math.fabs(180 - ((data['heading'] - values['absolute_wind_direction']) % 360))
    
                if values['preferred_gybe'] == -1:  # If the boat is on a left-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + 180 + values['gybe_angle'] + 360) % 360
                    
                elif values['preferred_gybe'] == 1: # If the boat is on a right-of-wind tack
                    values['current_desired_heading'] = (values['absolute_wind_direction'] + 180 - values['gybe_angle'] + 360) % 360
                    
                else:
                    logging.error("The preferred gybe was %d" % values['preferred_gybe'])

            else:
                logging.critical('Critical logic error!')
                    
            # Deal with events
            if values['event'] == 'station_keeping':
                self.station_keeping()

            self.turn_rudder()
            self.turn_winch()
            self.check_locations()

            logging.debug("Heading: %d, Direction: %d, Wind: %d, Absolute Wind Direction: %d, Current Desired Heading: %d, Sailable: %r\n" % (data['heading'], values['direction'], data['wind_dir'], values['absolute_wind_direction'], values['current_desired_heading'], self.sailable(values['target_locations'][values['location_pointer']])))

    # Checks to see if the target location is within a sailable region 
    def sailable(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360

        if angle_of_target_off_the_wind < values['tack_angle']:
            return False

        if angle_of_target_off_the_wind > (360 - values['tack_angle']):
            return False
        
        if (angle_of_target_off_the_wind > (180 - values['gybe_angle'])) and (angle_of_target_off_the_wind < (180 + values['gybe_angle'])):
            return False

        return True

    def upwind(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        return (angle_of_target_off_the_wind < values['tack_angle']) or (angle_of_target_off_the_wind > (360 - values['tack_angle']))

    def downwind(self, target_location):
        angle_of_target_off_the_wind = (values['direction'] - values['absolute_wind_direction'] + 360) % 360
        return (angle_of_target_off_the_wind > (180 - values['gybe_angle'])) and (angle_of_target_off_the_wind < (180 + values['gybe_angle']))

    def check_locations(self):
        global location_pointer
        logging.debug('Trying to sail to %s, %s m away' % (values['target_locations'][values['location_pointer']], modules.calc.distance(data['location'], values['target_locations'][values['location_pointer']])))

        if modules.calc.point_proximity(data['location'], values['target_locations'][values['location_pointer']]):
            logging.debug('Location %s has been reached! Now traveling to %s!' % (values['target_locations'][values['location_pointer']], values['target_locations'][values['location_pointer'] + 1]))
            location_pointer += 1

    def turn_rudder(self):
        # Heading differential
        a = ((values['current_desired_heading'] - data['heading']) + 360) % 360
        if (a > 180):
            a -= 360

        # Cap the turn speed
        if (a > values['max_turn_rate_angle']):
            a = values['max_turn_rate_angle']

        # Cap the turn speed
        if (a < (-1 * values['max_turn_rate_angle'])):
            a = -1 * values['max_turn_rate_angle']

        values['rudder_angle'] = a * (values['max_rudder_angle'] / values['max_turn_rate_angle'])

        logging.debug('Set the rudder angle to: %f' % values['rudder_angle'])
        self._kwargs['data_thread'].set_rudder_angle(values['rudder_angle'])


    def turn_winch(self):
        a = data['wind_dir']

        if data['wind_dir'] > 180:
            a = 360 - a

        if a > (180 - values['gybe_angle']):
            a = 180 - values['gybe_angle']

        elif a < values['tack_angle']:
            a = values['tack_angle']

        a -= values['tack_angle']

        values['winch_angle'] = 80 - 40 * (a / (180 - values['gybe_angle'] - values['tack_angle']))

        logging.debug('Set the winch angle to: %f' % values['winch_angle'])
        self._kwargs['data_thread'].set_winch_angle(values['winch_angle'])