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

default_timeout = 60
default_interval = 60


last_ping_success = 0
last_ping_error = 0


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


def update_last_ping_success():
    global last_ping_success
    last_ping_success = datetime.datetime.now().timestamp()


def update_last_ping_error():
    global last_ping_error
    last_ping_error = datetime.datetime.now().timestamp()


def write_to_file(file):
    global last_ping_success
    global last_ping_error

    with open(file, 'w') as f:
        f.write(str(last_ping_success) + "\t" + str(last_ping_error))


def ping_loop(host, file, timeout, interval):
    global last_ping_success
    global last_ping_error

    process = subprocess.Popen(['ping', '-i', str(interval), '-t', str(timeout), host], stdout=subprocess.PIPE)

    while process.poll() is None:
        line = process.stdout.readline()
        if b"time=" in line:
            update_last_ping_success()
        elif line.startswith(b"PING"):
            pass
        else:
            update_last_ping_error()

        write_to_file(file)

    if process.returncode != 0:
        update_last_ping_error()
        write_to_file(file)

    return process.returncode


def main():
    args = get_parser().parse_args()

    while True:
        ping_loop(args.host, args.output, args.timeout, args.interval)
        print("ping stops, will be restarted for: " + str(args.interval) + " seconds")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
