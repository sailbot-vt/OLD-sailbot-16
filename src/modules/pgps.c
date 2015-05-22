#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <unistd.h>

// Socket specific libraries
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>

// GPSD specific libraries
#include <gps.h>
#include "../lib/gpsd_config.h"
#include "../lib/gpsdclient.h"

static time_t status_timer;
static struct fixsource_t source;
static struct gps_data_t gpsdata;

char json[1024];

// Method prototypes
void build_json(void);
void write_element(char*, float, char*);
void get_data(void);

// GPS variables
int count = 0, track = 0, status = 0, heading = 0;
double latitude = 0, longitude = 0, unix_time = 0;
double roll = 0, pitch = 0, yaw = 0, speed = 0;

// Define error handling methods
void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    printf("[GPS Socket]: Starting the GPS Socket\n");

    // Close GPS in case of prior inproper shutdown
    gps_close(&gpsdata);

    // Flags for GPSD
    unsigned int flags = WATCH_ENABLE;
    char tbuf[CLIENT_DATE_MAX + 1];

    if (optind < argc) {
        gpsd_source_spec(argv[optind], & source);

    } else {
        gpsd_source_spec(NULL, & source);
    }

    // Open the GPSD stream
    if (gps_open("127.0.0.1", "2947", & gpsdata) != 0) {
        error("[GPS Socket]: No GPSD running or network error!\n");
        // Exit with error status
        return 1;
    } else {
        printf("[GPS Socket]: GPS port successfully opened!\n");
    }

    status_timer = time(NULL);

    if (source.device != NULL) {
        flags |= WATCH_DEVICE;
    }

    // Stream GPS Parameters
    (void) gps_stream(&gpsdata, flags, source.device);

    // Setup the socket connection
    int sockfd, clientsockfd, port;

    socklen_t client;

    char buffer[256];
    struct sockaddr_in server_address, client_address;

    int n;

    if (argc < 2) {
        fprintf(stderr, "[GPS Socket]: Error: No port specified\n");
        exit(1);
    }

    // Create the socket connection
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (sockfd < 0) {
        error("[GPS Socket]: Error: Cannot open socket");
    }

    bzero((char*) & server_address, sizeof(server_address));

    port = atoi(argv[1]);
    server_address.sin_family = AF_INET;
    server_address.sin_addr.s_addr = INADDR_ANY;
    server_address.sin_port = htons(port);

    // Bind to the socket
    if (bind(sockfd, (struct sockaddr*) & server_address,
            sizeof(server_address)) < 0) {
        error("[GPS Socket]: Error: Failed to bind to socket");
    }

    listen(sockfd, 5);

    // Create and accept the client socket connection
    client = sizeof(client_address);
    clientsockfd = accept(sockfd, (struct sockaddr*) & client_address, &client);

    if (clientsockfd < 0) {
        error("[GPS Socket]: Error: Problem accepting request");
    }

    // Enter and infinite connection with the client
    for (;;) {
        bzero(buffer, 256);

        // Socket read functions
        n = read(clientsockfd, buffer, 255);

        if (n < 0) {
            error("[GPS Socket]: Error: Cannot read from socket");
        }

        get_data();
        build_json();

        // Socket write functions
        printf("Sent: %s\n", json);
        n = write(clientsockfd, json, 0);


        if (n < 0) {
            error("[GPS Socket]: Error: Cannot write to socket");
        }
    }

    // Close the client and socket connections
    close(clientsockfd);
    close(sockfd);

    return 0;
}

void build_json(void) {
    strcpy(json, "{ ");

    write_element("time", unix_time, "%d");
    write_element("latitude", latitude, "%0.7f");
    write_element("longitude", longitude, "%0.7f");
    write_element("heading", heading, "%f");
    write_element("roll", roll, "%0.3f");
    write_element("pitch", pitch, "%0.3f");
    write_element("yaw", yaw, "%0.3f");

    strcpy(json + strlen(json), " }");
}

void write_element(char* property, float value, char* format) {
    sprintf(json + strlen(json), "\"%s\":", property);
    sprintf(json + strlen(json), format, value);
    strcpy(json + strlen(json), ", ");
}


void get_data(void) {
        if (gps_read(&gpsdata) == -1) {
            // Print error if GPS isn't read
            printf("[GPS Socket]: GPS not read!\n");
        } else {
            if (isnan(gpsdata.fix.latitude) != 0) {
                // Don't use GPS data without a Fix
                printf("[GPS Socket]: No GPS fix!\n");
            }
            else {
                // Get Basic GPS parameters 
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
}