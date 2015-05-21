#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>

// Define error handling methods
void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
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

        // Socket write functions
        printf("Sent: %s\n", "");
        n = write(clientsockfd, "", 0);


        if (n < 0) {
            error("[GPS Socket]: Error: Cannot write to socket");
        }
    }

    // Close the client and socket connections
    close(clientsockfd);
    close(sockfd);

    return 0;
}