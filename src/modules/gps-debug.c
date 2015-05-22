#include <stdio.h>
#include <stdlib.h>

#include <unistd.h>

// GPSD Specific Libraries
#include <gps.h>
#include "../lib/gpsd_config.h"
#include "../lib/gpsdclient.h"

static time_t status_timer;
static struct fixsource_t source;
static struct gps_data_t gpsdata;

int main(int argc, char * * argv) {
    printf("\033c");
    sleep(2);

    // Close GPS in case of prior inproper shutdown
    gps_close(&gpsdata);

    // Flags for GPSD
    unsigned int flags = WATCH_ENABLE;
    char tbuf[CLIENT_DATE_MAX + 1];

    int count = 0, track = 0, status = 0, heading = 0;
    double latitude = 0, longitude = 0, unix_time = 0;
    double roll = 0, pitch = 0, yaw = 0, speed = 0;

    if (optind < argc) {
        gpsd_source_spec(argv[optind], & source);

    } else {
        gpsd_source_spec(NULL, & source);
    }

    // Open the GPSD stream
    if (gps_open("127.0.0.1", "2947", & gpsdata) != 0) {
        printf("No GPSD running or network error!\n");
        return 1;
    } else {
        printf("GPS port successfully opened! \n\n");
    }

    sleep(2);

    status_timer = time(NULL);

    if (source.device != NULL) {
        flags |= WATCH_DEVICE;
    }

    // Stream GPS Parameters
    (void) gps_stream( & gpsdata, flags, source.device);

    // Infinite loop
    for (;;) {

        // Changes frequency of sampling (10 Hz)
        usleep(100000);

        // Clear terminal
        printf("\033c");						

        if (gps_read(&gpsdata) == -1) {
        	// Print error if GPS isn't read
            printf("GPS not read.\n");
        } else {
            if (isnan(gpsdata.fix.latitude) != 0) {
            	// Don't use GPS data without a Fix
                printf("No GPS Fix.\n");
            }
            else {
            	// Get basic GPS parameters 
                latitude = gpsdata.fix.latitude;
                longitude = gpsdata.fix.longitude;
                unix_time = gpsdata.fix.time;
                track = gpsdata.fix.track;
                speed = gpsdata.fix.speed;

                // Specific to Hemisphere H-102 GPS
                heading = gpsdata.attitude.heading;
                roll = gpsdata.attitude.roll;
                pitch = gpsdata.attitude.pitch;
                yaw = gpsdata.attitude.yaw;
                status = gpsdata.attitude.mag_st;

                if (status == 0) {
                    heading = track;
                }

                if ((isnan(gpsdata.attitude.heading) != 0) || (heading > 360 || heading < 0)) {
                    heading = 0;
                }
                if ((isnan(gpsdata.fix.track) != 0) || (track > 360 || track < 0)) {
                    track = 0;
                }
                if ((isnan(gpsdata.attitude.roll) != 0) || (roll > 360 || roll < 0)) {
                    roll = 0;
                }
                if ((isnan(gpsdata.attitude.pitch) != 0) || (pitch > 360 || pitch < 0)) {
                    pitch = 0;
                }
                if ((isnan(gpsdata.attitude.yaw) != 0) || (yaw > 360 || yaw < 0)) {
                    yaw = 0;
                }
            }
        }


        printf("Time: %s\n", unix_to_iso8601((timestamp_t) time(NULL), tbuf, sizeof(tbuf)));
        printf("GPS time (seconds): %f\n\n", unix_time);
        printf("Boat Latitude: %lf\n", latitude);
        printf("Boat Longitude: %lf\n\n", longitude);
        printf("Heading (degrees, N): %d\n", heading);
        printf("Track (degrees, N): %d\n", track);
        printf("Speed (mph): %lf\n\n", speed);
        printf("Compass Lock Status: %d\n\n", status);
        printf("Roll (degrees): %lf\n", roll);
        printf("Pitch (degrees): %lf\n", pitch);
        printf("Yaw (degrees): %lf\n", yaw);

    }

}
