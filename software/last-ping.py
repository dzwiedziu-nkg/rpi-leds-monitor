#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Last-Ping script v1.0-alpha under GPL 3.0 license
Copyright (C) by Michał Niedźwiecki 2016

Ping continuously to given host and store in output file the timestamp of the last successful ping and the last failed
ping.

Usage:
    $ python last-ping.py host output (-t timeout) (-i interval)

    host
        Required: Host to being ping.

    output
        Required: File where ping result will be stored.

    -t timeout
        Optional: Timeout value for ping command.

    -i interval
        Optional: Interval value for ping command.

Example:
    Ping to 8.8.8.8 and store result in /tmp/last-ping-result.tmp file.

        $ python last-ping.py -h 8.8.8.8 -o /tmp/last-ping-result.tmp

Attributes:
    default_timeout (int): Default timeout value when -t is not used.
    default_interval (int): Default interval value when -i is not used.

"""
import datetime
import time
import subprocess
import argparse
from ping import Ping

default_timeout = 60
default_interval = 60

ping = None
output = None


def get_parser():
    parser = argparse.ArgumentParser(
        prog="last-ping",
        description="Ping continuously to given host and store in output file the timestamp of the last successful ping"
                    " and the last failed ping."
    )

    parser.add_argument(dest='host', help="host to being ping", type=str)
    parser.add_argument(dest='output', help="file where ping result will be stored", type=str)
    parser.add_argument('-t', '--timeout', help="timeout value for ping command", default=default_timeout, type=int)
    parser.add_argument('-i', '--interval', help="interval value for ping command", default=default_interval, type=int)
    return parser


def write_to_file():
    global ping
    global output

    with open(output, 'w') as f:
        f.write(str(ping.get_last_ping_success()) + "\t" + str(ping.get_last_ping_error()))
    print("ping updated")


def ping_restarted(code):
    global ping
    print("ping stops, will be restarted for: " + str(ping.interval) + " seconds" + ", error code: " + str(code))


def main():
    global ping
    global output

    args = get_parser().parse_args()

    ping = Ping(args.host, args.timeout, args.interval)
    ping.on_update = write_to_file
    ping.on_process_restarted = ping_restarted

    output = args.output

    t = ping.start()
    try:
        while t.isAlive():
            print("Last success: " + str(ping.get_last_ping_success()) + ", last error: " + str(ping.get_last_ping_error()))
            time.sleep(1)
    except KeyboardInterrupt:
        ping.stop()

    t.join()


if __name__ == "__main__":
    main()
