#ifndef _GPSD_GPSDCLIENT_H_
#define _GPSD_GPSDCLIENT_H_
struct fixsource_t 
/* Describe a data source */
{
    char *spec;		/* Pointer to actual storage */
    char *server;
    char *port;
    /*@null@*/char *device;
};

enum unit {unspecified, imperial, nautical, metric};
enum unit gpsd_units(void);
enum deg_str_type { deg_dd, deg_ddmm, deg_ddmmss };

extern /*@observer@*/ char *deg_to_str( enum deg_str_type type,  double f);

extern void gpsd_source_spec(/*@null@*/const char *fromstring, 
			     /*@out@*/struct fixsource_t *source);

char *maidenhead(double n,double e);

/* This needs to match JSON_DATE_MAX in gpsd.h */
#define CLIENT_DATE_MAX	24

#endif /* _GPSDCLIENT_H_ */
